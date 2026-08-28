export const CAMPUS = {
  nanhai: '南海校区',
  shipai: '石牌校区',
}

export const TRANSFER_STATUS = {
  pending: { label: '待接收', type: 'warning' },
  confirmed: { label: '已确认', type: 'success' },
  overdue: { label: '已逾期', type: 'danger' },
  exception: { label: '异常', type: 'danger' },
  cancelled: { label: '已撤回', type: 'info' },
}

export const FILE_TYPE = {
  admin: '行政文件',
  teaching: '教学资料',
  student: '学生材料',
  finance: '财务票据',
  other: '其他',
}

export const URGENCY = {
  normal: { label: '普通', type: 'info' },
  urgent: { label: '加急', type: 'warning' },
  critical: { label: '特急', type: 'danger' },
}

export function toOptions(dict) {
  return Object.entries(dict).map(([value, item]) => ({
    value,
    label: typeof item === 'string' ? item : item.label,
  }))
}

export const campusLabel = (v) => CAMPUS[v] || v || ''
export const statusLabel = (v) => TRANSFER_STATUS[v]?.label || v || ''
export const statusType = (v) => TRANSFER_STATUS[v]?.type || 'info'
export const fileTypeLabel = (v) => FILE_TYPE[v] || v || ''
export const urgencyLabel = (v) => URGENCY[v]?.label || v || ''
export const urgencyType = (v) => URGENCY[v]?.type || 'info'

/** 后端已统一使用本地时间，直接解析即可 */
export function parseServerTime(value) {
  if (!value) return null
  if (value instanceof Date) return value
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? null : date
}

/** 提交给后端的时间直接转 ISO 字符串 */
export function toServerTime(value) {
  if (!value) return null
  const date = value instanceof Date ? value : new Date(value)
  return Number.isNaN(date.getTime()) ? null : date.toISOString()
}

function pad(n) {
  return String(n).padStart(2, '0')
}

export function formatDateTime(value) {
  const date = parseServerTime(value)
  if (!date) return '—'
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

export function formatDate(value) {
  const date = parseServerTime(value)
  if (!date) return '—'
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
}

export function formatFileSize(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let i = 0
  while (size >= 1024 && i < units.length - 1) {
    size /= 1024
    i += 1
  }
  return `${size.toFixed(i === 0 ? 0 : 1)} ${units[i]}`
}

export function oppositeCampus(campus) {
  return campus === 'nanhai' ? 'shipai' : 'nanhai'
}