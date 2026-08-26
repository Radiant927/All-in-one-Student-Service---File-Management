import request from './request'

export const listBuses = (params) => request.get('/buses', { params })
export const createBus = (data) => request.post('/buses', data)
export const updateBus = (id, data) => request.put(`/buses/${id}`, data)
export const deleteBus = (id) => request.delete(`/buses/${id}`)
