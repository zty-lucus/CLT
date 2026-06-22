import request from './request'

export const friendApi = {
  /**
   * 搜索可添加的用户
   * @param {string} keyword - 搜索关键词
   */
  searchUsers(keyword) {
    return request.get('/friends/search', { params: { keyword } })
  },

  /**
   * 发送好友申请
   * @param {Object} data - { addressee_id, message }
   */
  sendRequest(data) {
    return request.post('/friends/request', data)
  },

  /**
   * 同意好友申请
   * @param {number} friendshipId - 好友关系ID
   */
  acceptRequest(friendshipId) {
    return request.post(`/friends/request/${friendshipId}/accept`)
  },

  /**
   * 拒绝好友申请
   * @param {number} friendshipId - 好友关系ID
   */
  rejectRequest(friendshipId) {
    return request.post(`/friends/request/${friendshipId}/reject`)
  },

  /**
   * 获取好友列表
   */
  getFriendList() {
    return request.get('/friends/list')
  },

  /**
   * 获取待处理的好友申请（发出和收到）
   */
  getPendingRequests() {
    return request.get('/friends/requests')
  },

  /**
   * 获取好友关系详情
   * @param {number} friendshipId - 好友关系ID
   */
  getFriendDetail(friendshipId) {
    return request.get(`/friends/${friendshipId}`)
  },

  /**
   * 删除好友
   * @param {number} friendshipId - 好友关系ID
   */
  deleteFriend(friendshipId) {
    return request.delete(`/friends/${friendshipId}`)
  },
}
