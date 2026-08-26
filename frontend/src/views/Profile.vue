<template>
  <div class="page">
    <div class="page-header">
      <h2 class="page-title">个人中心</h2>
    </div>

    <el-row :gutter="16">
      <el-col :xs="24" :md="12">
        <el-card class="card-gap">
          <template #header>账号信息</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="用户名">{{ user?.username }}</el-descriptions-item>
            <el-descriptions-item label="姓名">{{ user?.real_name }}</el-descriptions-item>
            <el-descriptions-item label="所属校区">
              {{ campusLabel(user?.campus) }}
            </el-descriptions-item>
            <el-descriptions-item label="联系电话">{{ user?.phone || '—' }}</el-descriptions-item>
            <el-descriptions-item label="角色">
              {{ user?.is_admin ? '管理员' : '校区负责人' }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatDateTime(user?.created_at) }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card class="card-gap">
          <template #header>修改密码</template>
          <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
            <el-form-item label="原密码" prop="old_password">
              <el-input v-model="form.old_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="form.new_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirm_password">
              <el-input v-model="form.confirm_password" type="password" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="submitting" @click="onSubmit">
                确认修改
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import * as authApi from '@/api/auth'
import { useUserStore } from '@/stores/user'
import { campusLabel, formatDateTime } from '@/utils/dict'

const router = useRouter()
const userStore = useUserStore()

const user = computed(() => userStore.user)

const formRef = ref()
const submitting = ref(false)
const form = ref({ old_password: '', new_password: '', confirm_password: '' })

const rules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度需在 6 到 50 个字符之间', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== form.value.new_password) callback(new Error('两次输入的密码不一致'))
        else callback()
      },
      trigger: 'blur',
    },
  ],
}

async function onSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    await authApi.changePassword({
      old_password: form.value.old_password,
      new_password: form.value.new_password,
    })
    ElMessage.success('密码修改成功，请重新登录')
    userStore.logout()
    router.push({ name: 'login' })
  } finally {
    submitting.value = false
  }
}
</script>
