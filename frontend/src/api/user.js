import request from './request'

export const userApi = {
  /** 获取个人信息 */
  getProfile() {
    return request.get('/user/profile')
  },
  /** 更新个人信息 */
  updateProfile(data) {
    return request.put('/user/profile', data)
  },
  /** 搜索用户 */
  searchUsers(keyword) {
    return request.get('/user/search', { params: { keyword } })
  },
}
