<template>
  <el-container class="layout">
    <el-aside :width="collapsed ? '64px' : '210px'" class="layout-aside">
      <div class="logo">
        <el-icon :size="22"><Van /></el-icon>
        <span v-if="!collapsed" class="logo-text">文件交接</span>
      </div>
      <el-menu :default-active="activeMenu" :collapse="collapsed" router class="layout-menu">
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>工作台</template>
        </el-menu-item>
        <el-menu-item index="/transfers/new">
          <el-icon><CirclePlus /></el-icon>
          <template #title>发起转交</template>
        </el-menu-item>
        <el-menu-item index="/transfers">
          <el-icon><Tickets /></el-icon>
          <template #title>转交记录</template>
        </el-menu-item>
        <el-menu-item index="/buses">
          <el-icon><Clock /></el-icon>
          <template #title>校车班次</template>
        </el-menu-item>
        <el-menu-item index="/profile">
          <el-icon><User /></el-icon>
          <template #title>个人中心</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="layout-header">
        <div class="header-left">
          <el-button text :icon="collapsed ? Expand : Fold" @click="collapsed = !collapsed" />
          <span class="header-title hide-on-mobile">{{ route.meta.title }}</span>
        </div>
        <div class="header-right">
          <el-tag type="primary" effect="plain">{{ campusLabel(userStore.campus) }}</el-tag>
          <el-dropdown @command="onCommand">
            <span class="user-trigger">
              {{ userStore.user?.real_name || userStore.user?.username }}
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { Expand, Fold } from '@element-plus/icons-vue'

import { useUserStore } from '@/stores/user'
import { campusLabel } from '@/utils/dict'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const collapsed = ref(window.innerWidth < 768)

const activeMenu = computed(() => route.meta.activeMenu || route.path)

onMounted(() => {
  // 刷新页面时用缓存的 token 拉一次用户信息，顺带校验 token 是否还有效
  userStore.fetchMe().catch(() => {})
})

async function onCommand(command) {
  if (command === 'profile') {
    router.push({ name: 'profile' })
    return
  }
  const confirmed = await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    type: 'warning',
  }).catch(() => false)
  if (!confirmed) return

  userStore.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.layout {
  height: 100%;
}

.layout-aside {
  background: #001529;
  transition: width 0.2s;
  overflow: hidden;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 56px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
}

.layout-menu {
  border-right: none;
  background: transparent;
  --el-menu-bg-color: transparent;
  --el-menu-text-color: rgba(255, 255, 255, 0.75);
  --el-menu-hover-bg-color: rgba(255, 255, 255, 0.08);
  --el-menu-active-color: #fff;
}

.layout-menu :deep(.is-active) {
  background: var(--el-color-primary);
}

.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 16px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.header-left,
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
}

.user-trigger {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  outline: none;
}

.layout-main {
  padding: 0;
  overflow-y: auto;
}
</style>
