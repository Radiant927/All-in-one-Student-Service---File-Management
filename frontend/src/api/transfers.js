import request from './request'

export const createTransfer = (data) => request.post('/transfers', data)
export const listTransfers = (params) => request.get('/transfers', { params })
export const getTransfer = (id) => request.get(`/transfers/${id}`)
export const updateTransfer = (id, data) => request.put(`/transfers/${id}`, data)
export const cancelTransfer = (id) => request.post(`/transfers/${id}/cancel`)
export const confirmTransfer = (id, data) => request.post(`/transfers/${id}/confirm`, data)
export const reportException = (id, data) => request.post(`/transfers/${id}/exception`, data)
