<template>
  <div class="page">
    <div class="page-header">
      <h2 class="page-title">用户管理</h2>
      <el-button type="primary" :icon="CirclePlus" @click="dialogVisible = true">新增用户</el-button>
    </div>

    <el-card v-loading="loading">
      <el-table :data="users">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="real_name" label="姓名" width="140" />
        <el-table-column label="校区" width="120">
          <template #default="{ row }">{{ campusLabel(row.campus) }}</template>
        </el-table-column>
        <el-table-column prop="phone" label="电话" width="140" />
        <el-table-column label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_admin ? 'danger' : 'info'">{{ row.is_admin ? '管理员' : '校区负责人' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button text type="danger" @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无用户" />
        </template>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="新增用户" width="420px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="用于登录" />
        </el-form-item>
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="form.real_name" placeholder="真实姓名" />
        </el-form-item>
        <el-form-item label="校区" prop="campus">
          <el-select v-model="form.campus" style="width: 100%">
            <el-option v-for="item in campusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="管理员">
          <el-switch v-model="form.is_admin" />
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
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CirclePlus } from '@element-plus/icons-vue'
import * as usersApi from '@/api/users'
import { CAMPUS, campusLabel, toOptions } from '@/utils/dict'

const campusOptions = toOptions(CAMPUS)

const loading = ref(false)
const submitting = ref(false)
const users = ref([])
const dialogVisible = ref(false)
const formRef = ref()
const form = ref({
  username: '',
  real_name: '',
  campus: 'nanhai',
  phone: '',
  is_admin: false,
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  campus: [{ required: true, message: '请选择校区', trigger: 'change' }],
}

async function load() {
  loading.value = true
  try {
    users.value = await usersApi.listUsers()
  } finally {
    loading.value = false
  }
}

async function onSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    await usersApi.createUser(form.value)
    ElMessage.success('用户已创建，初始密码为 admin123')
    dialogVisible.value = false
    form.value = { username: '', real_name: '', campus: 'nanhai', phone: '', is_admin: false }
    load()
  } finally {
    submitting.value = false
  }
}

async function onDelete(row) {
  const confirmed = await ElMessageBox.confirm(
    `确定删除用户「${row.real_name}」吗？`,
    '删除用户',
    { type: 'warning' },
  ).catch(() => false)
  if (!confirmed) return
  await usersApi.deleteUser(row.id)
  ElMessage.success('用户已删除')
  load()
}

onMounted(load)
</script>