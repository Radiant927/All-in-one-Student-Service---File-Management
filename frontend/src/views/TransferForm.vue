<template>
  <div class="page">
    <div class="page-header">
      <h2 class="page-title">{{ isEdit ? '编辑转交单' : '发起转交' }}</h2>
      <el-button :icon="Back" @click="router.back()">返回</el-button>
    </div>

    <el-card v-loading="loading">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="110px"
        label-position="left"
      >
        <el-alert type="info" :closable="false" class="card-gap">
          本单由 <b>{{ campusLabel(userStore.campus) }}</b> 发往
          <b>{{ campusLabel(userStore.peerCampus) }}</b>
        </el-alert>

        <el-divider content-position="left">文件信息</el-divider>

        <el-form-item label="文件标题" prop="title">
          <el-input v-model="form.title" maxlength="200" show-word-limit placeholder="本次转交的事由" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="文件类型" prop="file_type">
              <el-select v-model="form.file_type" style="width: 100%">
                <el-option
                  v-for="item in fileTypeOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="紧急程度" prop="urgency">
              <el-select v-model="form.urgency" style="width: 100%">
                <el-option
                  v-for="item in urgencyOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="文件说明">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="份数、注意事项等备注信息"
          />
        </el-form-item>
        <el-form-item label="文件附件" prop="fileIds">
          <el-upload
            v-model:file-list="fileList"
            :http-request="doUpload"
            :before-upload="beforeUpload"
            :on-remove="onRemove"
            multiple
            class="upload-block"
          >
            <el-button :icon="UploadFilled">选择文件</el-button>
            <template #tip>
              <div class="text-muted upload-tip">
                支持 PDF / Word / Excel / 图片 / 压缩包，单个文件不超过 {{ MAX_SIZE_MB }}MB
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <el-divider content-position="left">校车与人员</el-divider>

        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="乘车日期">
              <el-date-picker
                v-model="busDate"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="选择日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="校车班次">
              <el-select
                v-model="busId"
                placeholder="选择班次后自动填写时间"
                clearable
                style="width: 100%"
              >
                <el-option
                  v-for="bus in availableBuses"
                  :key="bus.id"
                  :label="`${bus.name}（${bus.depart_time} → ${bus.arrive_time}）`"
                  :value="bus.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="发车时间" prop="depart_time">
              <el-date-picker
                v-model="form.depart_time"
                type="datetime"
                placeholder="选择发车时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="预计到达">
              <el-date-picker
                v-model="form.estimate_arrive_time"
                type="datetime"
                placeholder="选择预计到达时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="转交同学" prop="courier_name">
              <el-input v-model="form.courier_name" placeholder="坐校车带文件的同学" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="同学电话" prop="courier_phone">
              <el-input v-model="form.courier_phone" placeholder="选填" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="接收人" prop="receiver_name">
              <el-input v-model="form.receiver_name" placeholder="对方校区接收人" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="接收人电话" prop="receiver_phone">
              <el-input v-model="form.receiver_phone" placeholder="选填" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="onSubmit">
            {{ isEdit ? '保存修改' : '确认发起' }}
          </el-button>
          <el-button @click="router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back, UploadFilled } from '@element-plus/icons-vue'

import * as transfersApi from '@/api/transfers'
import * as busesApi from '@/api/buses'
import * as filesApi from '@/api/files'
import { useUserStore } from '@/stores/user'
import {
  FILE_TYPE,
  URGENCY,
  campusLabel,
  parseServerTime,
  toOptions,
  toServerTime,
} from '@/utils/dict'

const MAX_SIZE_MB = 50

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const fileTypeOptions = toOptions(FILE_TYPE)
const urgencyOptions = toOptions(URGENCY)

const transferId = computed(() => route.params.id)
const isEdit = computed(() => !!transferId.value)

const formRef = ref()
const loading = ref(false)
const submitting = ref(false)
const buses = ref([])
const fileList = ref([])
const busDate = ref(new Date().toISOString().slice(0, 10))
const busId = ref(null)
/** 编辑时已存在的附件 id，移除它们不需要调删除接口（后端在保存时重新关联） */
const existingFileIds = ref(new Set())

const form = ref({
  title: '',
  description: '',
  courier_name: '',
  courier_phone: '',
  receiver_name: '',
  receiver_phone: '',
  depart_time: null,
  estimate_arrive_time: null,
  file_type: 'other',
  urgency: 'normal',
})

const fileIds = computed(() =>
  fileList.value.map((file) => file.response?.id ?? file.id).filter(Boolean),
)

const rules = {
  title: [{ required: true, message: '请填写文件标题', trigger: 'blur' }],
  file_type: [{ required: true, message: '请选择文件类型', trigger: 'change' }],
  urgency: [{ required: true, message: '请选择紧急程度', trigger: 'change' }],
  depart_time: [{ required: true, message: '请选择发车时间', trigger: 'change' }],
  courier_name: [{ required: true, message: '请填写转交同学姓名', trigger: 'blur' }],
  receiver_name: [{ required: true, message: '请填写接收人姓名', trigger: 'blur' }],
  fileIds: [
    {
      validator: (_rule, _value, callback) => {
        if (!fileIds.value.length) callback(new Error('请至少上传一个文件附件'))
        else callback()
      },
      trigger: 'change',
    },
  ],
}

const availableBuses = computed(() =>
  buses.value.filter(
    (bus) => bus.from_campus === userStore.campus && bus.to_campus === userStore.peerCampus,
  ),
)

// 选好日期和班次就把两个时间字段填上，用户仍可手动微调
watch([busDate, busId], ([date, id]) => {
  if (!date || !id) return
  const bus = buses.value.find((item) => item.id === id)
  if (!bus) return
  form.value.depart_time = new Date(`${date}T${bus.depart_time}:00`)
  form.value.estimate_arrive_time = new Date(`${date}T${bus.arrive_time}:00`)
})

function beforeUpload(file) {
  if (file.size > MAX_SIZE_MB * 1024 * 1024) {
    ElMessage.error(`「${file.name}」超过 ${MAX_SIZE_MB}MB，无法上传`)
    return false
  }
  return true
}

async function doUpload(options) {
  const uploaded = await filesApi.uploadFile(options.file)
  formRef.value?.validateField('fileIds').catch(() => {})
  return uploaded
}

function onRemove(file) {
  const id = file.response?.id ?? file.id
  // 本次新上传的文件还没关联转交单，顺手删掉避免留下孤儿文件
  if (id && !existingFileIds.value.has(id)) {
    filesApi.deleteFile(id).catch(() => {})
  }
  formRef.value?.validateField('fileIds').catch(() => {})
}

async function loadDetail() {
  loading.value = true
  try {
    const data = await transfersApi.getTransfer(transferId.value)
    form.value = {
      title: data.title,
      description: data.description,
      courier_name: data.courier_name,
      courier_phone: data.courier_phone,
      receiver_name: data.receiver_name,
      receiver_phone: data.receiver_phone,
      depart_time: parseServerTime(data.depart_time),
      estimate_arrive_time: parseServerTime(data.estimate_arrive_time),
      file_type: data.file_type,
      urgency: data.urgency,
    }
    existingFileIds.value = new Set(data.files.map((file) => file.id))
    fileList.value = data.files.map((file) => ({
      name: file.original_name,
      uid: file.id,
      status: 'success',
      response: { id: file.id },
    }))
  } finally {
    loading.value = false
  }
}

async function onSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  const payload = {
    ...form.value,
    depart_time: toServerTime(form.value.depart_time),
    estimate_arrive_time: toServerTime(form.value.estimate_arrive_time),
    file_ids: fileIds.value,
  }

  submitting.value = true
  try {
    if (isEdit.value) {
      await transfersApi.updateTransfer(transferId.value, payload)
      ElMessage.success('修改已保存')
      router.push({ name: 'transfer-detail', params: { id: transferId.value } })
    } else {
      const created = await transfersApi.createTransfer({
        ...payload,
        to_campus: userStore.peerCampus,
      })
      ElMessage.success(`转交单 ${created.transfer_no} 已发起，已通知对方校区`)
      router.push({ name: 'transfer-detail', params: { id: created.id } })
    }
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  buses.value = await busesApi.listBuses({ only_active: true })
  if (isEdit.value) await loadDetail()
})
</script>

<style scoped>
.upload-block {
  width: 100%;
}

.upload-tip {
  font-size: 12px;
  line-height: 1.6;
}
</style>
