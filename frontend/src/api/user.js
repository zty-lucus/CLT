import request from './request'

export const userApi = {
  /** 获取个人信息 */
  getProfile() {
    return request.get('/users/profile')
  },
  /** 更新个人信息 */
  updateProfile(data) {
    return request.put('/users/profile', data)
  },
  /** 搜索用户 */
  searchUsers(keyword) {
    return request.get('/users/search', { params: { keyword } })
  },
}
