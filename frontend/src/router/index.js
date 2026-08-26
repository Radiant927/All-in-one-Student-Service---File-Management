import { createRouter, createWebHistory } from 'vue-router'

import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/Login.vue'),
    meta: { public: true, title: '登录' },
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      { path: '', redirect: { name: 'dashboard' } },
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '工作台' },
      },
      {
        path: 'transfers',
        name: 'transfers',
        component: () => import('@/views/TransferList.vue'),
        meta: { title: '转交记录' },
      },
      {
        path: 'transfers/new',
        name: 'transfer-new',
        component: () => import('@/views/TransferForm.vue'),
        meta: { title: '发起转交', activeMenu: '/transfers/new' },
      },
      {
        path: 'transfers/:id/edit',
        name: 'transfer-edit',
        component: () => import('@/views/TransferForm.vue'),
        meta: { title: '编辑转交单', activeMenu: '/transfers' },
      },
      {
        path: 'transfers/:id',
        name: 'transfer-detail',
        component: () => import('@/views/TransferDetail.vue'),
        meta: { title: '转交详情', activeMenu: '/transfers' },
      },
      {
        path: 'buses',
        name: 'buses',
        component: () => import('@/views/BusSchedule.vue'),
        meta: { title: '校车班次' },
      },
      {
        path: 'profile',
        name: 'profile',
        component: () => import('@/views/Profile.vue'),
        meta: { title: '个人中心' },
      },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: { name: 'dashboard' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const userStore = useUserStore()
  const loggedIn = !!userStore.token

  if (to.meta.public) {
    return loggedIn && to.name === 'login' ? { name: 'dashboard' } : true
  }
  if (!loggedIn) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  return true
})

router.afterEach((to) => {
  const base = '跨校区文件交接管理系统'
  document.title = to.meta.title ? `${to.meta.title} · ${base}` : base
})

export default router
