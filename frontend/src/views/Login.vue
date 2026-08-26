<template>
  <div class="login-page">
    <el-card class="login-card">
      <div class="login-brand">
        <el-icon :size="32" color="#409eff"><Van /></el-icon>
        <h2 class="login-title">跨校区文件交接管理系统</h2>
        <p class="text-muted login-subtitle">南海校区 ↔ 石牌校区</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @keyup.enter="onSubmit"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" :prefix-icon="User" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
            :prefix-icon="Lock"
          />
        </el-form-item>
        <el-button type="primary" class="login-button" :loading="loading" @click="onSubmit">
          登录
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Lock, User } from '@element-plus/icons-vue'

import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const formRef = ref()
const loading = ref(false)
const form = ref({ username: '', password: '' })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function onSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const user = await userStore.login(form.value)
    ElMessage.success(`欢迎回来，${user.real_name}`)
    router.push(route.query.redirect || { name: 'dashboard' })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #1f3a63 0%, #409eff 100%);
}

.login-card {
  width: 100%;
  max-width: 380px;
}

.login-brand {
  text-align: center;
  margin-bottom: 8px;
}

.login-title {
  margin: 8px 0 4px;
  font-size: 19px;
}

.login-subtitle {
  margin: 0 0 8px;
  font-size: 13px;
}

.login-button {
  width: 100%;
}
</style>
