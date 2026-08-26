import request, { downloadBlob } from './request'

export const getDashboard = () => request.get('/stats/dashboard')
export const getTrend = (days = 7) => request.get('/stats/trend', { params: { days } })

export function exportTransfers(params) {
  const stamp = new Date().toISOString().slice(0, 10)
  return downloadBlob('/stats/export', params, `转交单列表_${stamp}.xlsx`)
}
