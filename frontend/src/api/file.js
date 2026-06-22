import request from './request'

export const fileApi = {
  /**
   * 上传单个文件
   * @param {File} file - 文件对象
   * @param {Function} onProgress - 上传进度回调 (progressEvent) => void
   */
  upload(file, onProgress) {
    const formData = new FormData()
    formData.append('file', file)
    return request.post('/files/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000, // 上传超时120秒
      onUploadProgress: onProgress,
    })
  },

  /**
   * 批量上传文件
   * @param {File[]} files - 文件对象数组
   * @param {Function} onProgress - 上传进度回调
   */
  uploadMultiple(files, onProgress) {
    const formData = new FormData()
    files.forEach((file) => {
      formData.append('files', file)
    })
    return request.post('/files/upload/multiple', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 300000, // 批量上传超时300秒
      onUploadProgress: onProgress,
    })
  },

  /**
   * 获取文件下载URL（直接拼接）
   * @param {number} fileId - 文件ID
   * @param {boolean} inline - 是否内联预览
   */
  getDownloadUrl(fileId, inline = false) {
    const token = localStorage.getItem('token') || ''
    // 通过后端认证，使用 Bearer Token
    // 注意：文件下载通过浏览器直接访问，需要在请求头带 Token
    return `/api/files/${fileId}/download?inline=${inline ? '1' : '0'}`
  },

  /**
   * 通过 Axios 下载文件（带 Token）
   * @param {number} fileId - 文件ID
   */
  downloadFile(fileId) {
    return request.get(`/files/${fileId}/download`, {
      responseType: 'blob',
      timeout: 60000,
    })
  },

  /**
   * 获取文件详情
   * @param {number} fileId - 文件ID
   */
  getFileInfo(fileId) {
    return request.get(`/files/${fileId}`)
  },

  /**
   * 获取我的文件列表
   * @param {number} page - 页码
   * @param {number} perPage - 每页数量
   */
  getMyFiles(page = 1, perPage = 20) {
    return request.get('/files/my', { params: { page, per_page: perPage } })
  },

  /**
   * 删除文件
   * @param {number} fileId - 文件ID
   */
  deleteFile(fileId) {
    return request.delete(`/files/${fileId}`)
  },
}
