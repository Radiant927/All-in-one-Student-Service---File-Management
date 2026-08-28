<template>
  <div class="page" v-loading="loading">
    <div class="page-header">
      <div class="title-group">
        <h2 class="page-title">{{ transfer?.title || '转交详情' }}</h2>
        <el-tag v-if="transfer" :type="statusType(transfer.status)" effect="dark">
          {{ statusLabel(transfer.status) }}
        </el-tag>
        <el-tag v-if="transfer" :type="urgencyType(transfer.urgency)" effect="plain">
          {{ urgencyLabel(transfer.urgency) }}
        </el-tag>
      </div>
      <el-button :icon="Back" @click="router.back()">返回</el-button>
    </div>

    <template v-if="transfer">
      <el-alert
        v-if="transfer.status === 'exception'"
        type="error"
        :closable="false"
        title="该转交单已上报异常"
        :description="transfer.exception_note"
        class="card-gap"
      />
      <el-alert
        v-else-if="transfer.status === 'overdue'"
        type="warning"
        :closable="false"
        title="该转交单已超过预计到达时间仍未确认"
        class="card-gap"
      />

      <el-card class="card-gap">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
            <div class="actions">
              <el-button v-if="canConfirm" type="success" :icon="Select" @click="confirmDialog = true">
                确认收到
              </el-button>
              <el-button v-if="canConfirm" type="warning" :icon="WarningFilled" @click="exceptionDialog = true">
                上报异常
              </el-button>
              <el-button v-if="canModify" :icon="Edit" @click="goEdit">编辑</el-button>
              <el-button v-if="canModify" type="danger" plain :icon="RefreshLeft" @click="onCancel">
                撤回
              </el-button>
            </div>
          </div>
        </template>

        <el-descriptions :column="descColumn" border>
          <el-descriptions-item label="转交单编号">{{ transfer.transfer_no }}</el-descriptions-item>
          <el-descriptions-item label="转交方向">
            {{ campusLabel(transfer.from_campus) }} → {{ campusLabel(transfer.to_campus) }}
          </el-descriptions-item>
          <el-descriptions-item label="文件类型">{{ fileTypeLabel(transfer.file_type) }}</el-descriptions-item>
          <el-descriptions-item label="紧急程度">{{ urgencyLabel(transfer.urgency) }}</el-descriptions-item>
          <el-descriptions-item label="转交同学">
            {{ transfer.courier_name }}
            <span v-if="transfer.courier_phone" class="text-muted">（{{ transfer.courier_phone }}）</span>
          </el-descriptions-item>
          <el-descriptions-item label="接收人">
            {{ transfer.receiver_name }}
            <span v-if="transfer.receiver_phone" class="text-muted">（{{ transfer.receiver_phone }}）</span>
          </el-descriptions-item>
          <el-descriptions-item label="发车时间">{{ formatDateTime(transfer.depart_time) }}</el-descriptions-item>
          <el-descriptions-item label="预计到达">{{ formatDateTime(transfer.estimate_arrive_time) }}</el-descriptions-item>
          <el-descriptions-item label="发起时间">{{ formatDateTime(transfer.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="确认时间">{{ formatDateTime(transfer.confirm_time) }}</el-descriptions-item>
          <el-descriptions-item label="文件说明" :span="descColumn">{{ transfer.description || '—' }}</el-descriptions-item>
          <el-descriptions-item v-if="transfer.confirm_message" label="收件留言" :span="descColumn">
            {{ transfer.confirm_message }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <el-card class="card-gap">
        <template #header>附件（{{ transfer.files.length }}）</template>
        <el-empty v-if="!transfer.files.length" description="没有附件" :image-size="70" />
        <el-table v-else :data="transfer.files">
          <el-table-column prop="original_name" label="文件名" min-width="220" show-overflow-tooltip />
          <el-table-column label="大小" width="110">
            <template #default="{ row }">{{ formatFileSize(row.file_size) }}</template>
          </el-table-column>
          <el-table-column label="上传时间" width="160">
            <template #default="{ row }">{{ formatDateTime(row.uploaded_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button text type="primary" :icon="Download" @click="onDownload(row)">下载</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <el-card class="card-gap">
        <template #header>流转进度</template>
        <el-steps :active="activeStep" align-center finish-status="success">
          <el-step title="已发起" :description="formatDateTime(transfer.created_at)" />
          <el-step title="校车发出" :description="formatDateTime(transfer.depart_time)" />
          <el-step title="预计到达" :description="formatDateTime(transfer.estimate_arrive_time)" />
          <el-step :title="stepFinalTitle" :status="stepFinalStatus" :description="formatDateTime(transfer.confirm_time)" />
        </el-steps>
      </el-card>

      <el-card>
        <template #header>操作记录</template>
        <el-empty v-if="!logs.length" description="暂无记录" :image-size="70" />
        <el-timeline v-else>
          <el-timeline-item
            v-for="log in logs"
            :key="log.id"
            :timestamp="formatDateTime(log.created_at)"
            type="primary"
          >
            {{ log.detail }}
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </template>

    <el-dialog v-model="confirmDialog" title="确认收到文件" width="520px">
      <el-form label-position="top">
        <el-form-item label="回执留言（选填）">
          <el-input v-model="confirmMessage" type="textarea" :rows="3" placeholder="如：文件齐全，已交至教务处" />
        </el-form-item>
        <el-form-item label="签收凭证照片（选填）">
          <el-upload
            v-model:file-list="confirmFileList"
            :http-request="doUpload"
            :before-upload="beforeUpload"
            :on-remove="onRemove"
            multiple
            list-type="picture-card"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="confirmDialog = false">取消</el-button>
        <el-button type="primary" :loading="acting" @click="onConfirm">确认收到</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="exceptionDialog" title="上报异常" width="420px">
      <el-form label-position="top">
        <el-form-item label="异常说明" required>
          <el-input v-model="exceptionNote" type="textarea" :rows="3" placeholder="如：缺少第 3 份材料 / 文件被雨水浸湿" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="exceptionDialog = false">取消</el-button>
        <el-button type="warning" :loading="acting" @click="onException">提交上报</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Back, Download, Edit, RefreshLeft, Select, WarningFilled, Plus } from '@element-plus/icons-vue'
import * as transfersApi from '@/api/transfers'
import * as filesApi from '@/api/files'
import * as logsApi from '@/api/logs'
import { useUserStore } from '@/stores/user'
import { campusLabel, fileTypeLabel, formatDateTime, formatFileSize, parseServerTime, statusLabel, statusType, urgencyLabel, urgencyType } from '@/utils/dict'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const acting = ref(false)
const transfer = ref(null)
const logs = ref([])
const confirmDialog = ref(false)
const exceptionDialog = ref(false)
const confirmMessage = ref('')
const confirmFileList = ref([])
const exceptionNote = ref('')

const descColumn = computed(() => (window.innerWidth < 768 ? 1 : 2))

const canConfirm = computed(() =>
  transfer.value &&
  userStore.campus === transfer.value.to_campus &&
  ['pending', 'overdue'].includes(transfer.value.status),
)

const canModify = computed(() =>
  transfer.value &&
  transfer.value.created_by === userStore.user?.id &&
  transfer.value.status === 'pending',
)

const activeStep = computed(() => {
  if (!transfer.value) return 0
  if (['confirmed', 'exception'].includes(transfer.value.status)) return 4
  const now = Date.now()
  const arrive = parseServerTime(transfer.value.estimate_arrive_time)
  const depart = parseServerTime(transfer.value.depart_time)
  if (arrive && now >= arrive.getTime()) return 3
  if (depart && now >= depart.getTime()) return 2
  return 1
})

const stepFinalTitle = computed(() => {
  const s = transfer.value?.status
  if (s === 'confirmed') return '已确认签收'
  if (s === 'exception') return '异常'
  if (s === 'cancelled') return '已撤回'
  return '待确认签收'
})

const stepFinalStatus = computed(() => {
  const s = transfer.value?.status
  if (s === 'confirmed') return 'success'
  if (s === 'exception' || s === 'overdue') return 'error'
  return undefined
})

async function load() {
  loading.value = true
  try {
    transfer.value = await transfersApi.getTransfer(route.params.id)
    const logData = await logsApi.listLogs({ target_type: 'transfer', target_id: transfer.value.id })
    logs.value = logData.items
  } finally {
    loading.value = false
  }
}

function goEdit() {
  router.push({ name: 'transfer-edit', params: { id: transfer.value.id } })
}

function beforeUpload(file) {
  if (file.size > 50 * 1024 * 1024) {
    ElMessage.error(`「${file.name}」超过 50MB，无法上传`)
    return false
  }
  return true
}

async function doUpload(options) {
  const uploaded = await filesApi.uploadFile(options.file)
  return uploaded
}

function onRemove(file) {
  const id = file.response?.id ?? file.id
  if (id) filesApi.deleteFile(id).catch(() => {})
}

async function onConfirm() {
  acting.value = true
  try {
    const fileIds = confirmFileList.value.map(f => f.response?.id ?? f.id).filter(Boolean)
    transfer.value = await transfersApi.confirmTransfer(transfer.value.id, {
      message: confirmMessage.value,
      file_ids: fileIds,
    })
    confirmDialog.value = false
    confirmMessage.value = ''
    confirmFileList.value = []
    ElMessage.success('已确认收到，对方校区将收到通知')
    load()
  } finally {
    acting.value = false
  }
}

async function onException() {
  if (!exceptionNote.value.trim()) {
    ElMessage.warning('请填写异常说明')
    return
  }
  acting.value = true
  try {
    transfer.value = await transfersApi.reportException(transfer.value.id, {
      note: exceptionNote.value.trim(),
    })
    exceptionDialog.value = false
    exceptionNote.value = ''
    ElMessage.success('异常已上报')
    load()
  } finally {
    acting.value = false
  }
}

async function onCancel() {
  const confirmed = await ElMessageBox.confirm(
    '撤回后对方将无法确认此单，确定撤回吗？',
    '撤回转交单',
    { type: 'warning' },
  ).catch(() => false)
  if (!confirmed) return
  transfer.value = await transfersApi.cancelTransfer(transfer.value.id)
  ElMessage.success('转交单已撤回')
  load()
}

function onDownload(file) {
  filesApi.downloadFile(file.id, file.original_name)
}

onMounted(load)
</script>

<style scoped>
.title-group { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.card-header { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; }
.actions { display: flex; gap: 8px; flex-wrap: wrap; }
</style>