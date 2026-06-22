import request from './request'

export const authApi = {
  /** 用户注册 */
  register(data) {
    return request.post('/auth/register', data)
  },
  /** 用户登录 */
  login(data) {
    return request.post('/auth/login', data)
  },
  /** 用户登出 */
  logout() {
    return request.post('/auth/logout')
  },
  /** 获取当前用户信息 */
  getMe() {
    return request.get('/auth/me')
  },
}
