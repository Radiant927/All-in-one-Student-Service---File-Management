import request from './request'

export const listUsers = () => request.get('/users')
export const createUser = (data) => request.post('/users', data)
export const deleteUser = (id) => request.delete(`/users/${id}`)