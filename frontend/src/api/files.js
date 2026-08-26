import request, { downloadBlob } from './request'

/** 上传单个文件，返回后端生成的附件记录（含 id，用于创建转交单时关联） */
export async function uploadFile(file) {
  const form = new FormData()
  form.append('files', file)
  const result = await request.post('/files/upload', form)
  return result[0]
}

export const deleteFile = (id) => request.delete(`/files/${id}`)

export const downloadFile = (id, filename) =>
  downloadBlob(`/files/${id}/download`, undefined, filename)
