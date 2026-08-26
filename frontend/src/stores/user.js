import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

import * as authApi from '@/api/auth'
import { getToken, setToken, clearToken } from '@/api/request'
import { oppositeCampus } from '@/utils/dict'

const USER_KEY = 'campus_file_user'

function readCachedUser() {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY)) || null
  } catch {
    return null
  }
}

export const useUserStore = defineStore('user', () => {
  const token = ref(getToken())
  const user = ref(readCachedUser())

  const campus = computed(() => user.value?.campus || '')
  const peerCampus = computed(() => (campus.value ? oppositeCampus(campus.value) : ''))
  const isAdmin = computed(() => !!user.value?.is_admin)

  function persistUser(value) {
    user.value = value
    if (value) {
      localStorage.setItem(USER_KEY, JSON.stringify(value))
    } else {
      localStorage.removeItem(USER_KEY)
    }
  }

  async function login(credentials) {
    const data = await authApi.login(credentials)
    token.value = data.access_token
    setToken(data.access_token)
    persistUser(data.user)
    return data.user
  }

  async function fetchMe() {
    const data = await authApi.getMe()
    persistUser(data)
    return data
  }

  function logout() {
    token.value = ''
    clearToken()
    persistUser(null)
  }

  return { token, user, campus, peerCampus, isAdmin, login, fetchMe, logout }
})
