/**
 * 群组 API 封装
 */
import request from './request'

/**
 * 获取群组列表
 */
export function getGroupsApi() {
  return request.get('/api/groups')
}

/**
 * 获取群组详情
 */
export function getGroupDetailApi(groupId) {
  return request.get(`/api/groups/${groupId}`)
}

/**
 * 创建群组
 */
export function createGroupApi(name, memberIds) {
  return request.post('/api/groups', {
    name,
    member_ids: memberIds,
  })
}

/**
 * 修改群信息
 */
export function updateGroupApi(groupId, data) {
  return request.put(`/api/groups/${groupId}`, data)
}

/**
 * 获取群成员列表
 */
export function getGroupMembersApi(groupId) {
  return request.get(`/api/groups/${groupId}/members`)
}

/**
 * 邀请成员加入群组
 */
export function inviteMembersApi(groupId, userIds) {
  return request.post(`/api/groups/${groupId}/members`, {
    user_ids: userIds,
  })
}

/**
 * 踢出群成员
 */
export function removeMemberApi(groupId, targetId) {
  return request.delete(`/api/groups/${groupId}/members/${targetId}`)
}

/**
 * 退出群组
 */
export function leaveGroupApi(groupId) {
  return request.delete(`/api/groups/${groupId}/members/me`)
}

/**
 * 解散群组
 */
export function dismissGroupApi(groupId) {
  return request.delete(`/api/groups/${groupId}`)
}
