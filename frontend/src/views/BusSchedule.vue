<template>
  <div class="page">
    <div class="page-header">
      <h2 class="page-title">校车班次</h2>
      <div class="header-actions">
        <el-checkbox v-model="onlyActive" @change="load">只看启用</el-checkbox>
        <el-button v-if="userStore.isAdmin" type="primary" :icon="CirclePlus" @click="openCreate">
          新增班次
        </el-button>
      </div>
    </div>

    <el-card v-loading="loading">
      <el-table :data="buses">
        <el-table-column prop="name" label="班次名称" min-width="150" />
        <el-table-column label="方向" min-width="180">
          <template #default="{ row }">
            {{ campusLabel(row.from_campus) }} → {{ campusLabel(row.to_campus) }}
          </template>
        </el-table-column>
        <el-table-column prop="depart_time" label="发车" width="90" />
        <el-table-column prop="arrive_time" label="预计到达" width="100" />
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" effect="plain" size="small">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="userStore.isAdmin" label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button text type="danger" @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无班次数据" />
        </template>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑班次' : '新增班次'" width="440px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="班次名称" prop="name">
          <el-input v-model="form.name" placeholder="如：上午第一班" />
        </el-form-item>
        <el-form-item label="出发校区" prop="from_campus">
          <el-select v-model="form.from_campus" style="width: 100%">
            <el-option
              v-for="item in campusOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="到达校区" prop="to_campus">
          <el-select v-model="form.to_campus" style="width: 100%">
            <el-option
              v-for="item in campusOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="发车时间" prop="depart_time">
          <el-time-picker
            v-model="departTime"
            format="HH:mm"
            placeholder="选择时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="预计到达" prop="arrive_time">
          <el-time-picker
            v-model="arriveTime"
            format="HH:mm"
            placeholder="选择时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" :max="999" />
        </el-form-item>
        <el-form-item v-if="editingId" label="启用">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="onSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CirclePlus } from '@element-plus/icons-vue'

import * as busesApi from '@/api/buses'
import { useUserStore } from '@/stores/user'
import { CAMPUS, campusLabel, toOptions } from '@/utils/dict'

const userStore = useUserStore()
const campusOptions = toOptions(CAMPUS)

const loading = ref(false)
const submitting = ref(false)
const onlyActive = ref(true)
const buses = ref([])
const dialogVisible = ref(false)
const editingId = ref(null)
const formRef = ref()

const form = ref(emptyForm())
// el-time-picker 用 Date 对象，后端存的是 "08:00" 字符串，这里分开存再互相转换
const departTime = ref(null)
const arriveTime = ref(null)

function emptyForm() {
  return {
    name: '',
    from_campus: 'nanhai',
    to_campus: 'shipai',
    depart_time: '',
    arrive_time: '',
    sort_order: 0,
    is_active: true,
  }
}

function toTimeDate(value) {
  if (!value) return null
  return new Date(`1970-01-01T${value}:00`)
}

function toTimeString(date) {
  if (!date) return ''
  return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

watch(departTime, (value) => {
  form.value.depart_time = toTimeString(value)
})
watch(arriveTime, (value) => {
  form.value.arrive_time = toTimeString(value)
})

const rules = computed(() => ({
  name: [{ required: true, message: '请填写班次名称', trigger: 'blur' }],
  from_campus: [{ required: true, message: '请选择出发校区', trigger: 'change' }],
  to_campus: [
    { required: true, message: '请选择到达校区', trigger: 'change' },
    {
      validator: (_rule, value, callback) => {
        if (value === form.value.from_campus) callback(new Error('出发和到达校区不能相同'))
        else callback()
      },
      trigger: 'change',
    },
  ],
  depart_time: [{ required: true, message: '请选择发车时间', trigger: 'change' }],
  arrive_time: [{ required: true, message: '请选择预计到达时间', trigger: 'change' }],
}))

async function load() {
  loading.value = true
  try {
    buses.value = await busesApi.listBuses({ only_active: onlyActive.value })
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  form.value = emptyForm()
  departTime.value = null
  arriveTime.value = null
  dialogVisible.value = true
}

function openEdit(row) {
  editingId.value = row.id
  form.value = { ...row }
  departTime.value = toTimeDate(row.depart_time)
  arriveTime.value = toTimeDate(row.arrive_time)
  dialogVisible.value = true
}

async function onSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (editingId.value) {
      await busesApi.updateBus(editingId.value, form.value)
      ElMessage.success('班次已更新')
    } else {
      await busesApi.createBus(form.value)
      ElMessage.success('班次已新增')
    }
    dialogVisible.value = false
    load()
  } finally {
    submitting.value = false
  }
}

async function onDelete(row) {
  const confirmed = await ElMessageBox.confirm(`确定删除班次「${row.name}」吗？`, '删除班次', {
    type: 'warning',
  }).catch(() => false)
  if (!confirmed) return

  await busesApi.deleteBus(row.id)
  ElMessage.success('班次已删除')
  load()
}

onMounted(load)
</script>

<style scoped>
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
</style>
