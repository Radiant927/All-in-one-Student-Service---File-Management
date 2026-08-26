import axios from 'axios'
import { ElMessage } from 'element-plus'

const TOKEN_KEY = 'campus_file_token'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY) || ''
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

request.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/** FastAPI 的报错体是 {detail: string} 或校验失败时的 {detail: [{msg, loc}]} */
function pickErrorMessage(error) {
  const detail = error.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail.length) {
    return detail.map((d) => `${d.loc?.slice(1).join('.') || ''} ${d.msg}`.trim()).join('；')
  }
  if (error.code === 'ECONNABORTED') return '请求超时，请重试'
  return error.message || '请求失败'
}

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      clearToken()
      // 会话失效直接整页跳登录，避免和路由守卫循环重定向
      if (!window.location.pathname.startsWith('/login')) {
        ElMessage.error('登录已过期，请重新登录')
        window.location.replace('/login')
      }
      return Promise.reject(error)
    }
    ElMessage.error(pickErrorMessage(error))
    return Promise.reject(error)
  },
)

/** 下载二进制流并触发浏览器保存 */
export async function downloadBlob(url, params, filename) {
  const blob = await request.get(url, { params, responseType: 'blob' })
  const link = document.createElement('a')
  const objectUrl = URL.createObjectURL(blob)
  link.href = objectUrl
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(objectUrl)
}

export default request
