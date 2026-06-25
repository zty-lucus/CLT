/**
 * 会话与消息 API 封装
 */
import request from './request'

/**
 * 获取会话列表
 */
export function getConversationsApi() {
  return request.get('/conversations')
}

/**
 * 获取会话详情
 */
export function getConversationDetailApi(conversationId) {
  return request.get(`/conversations/${conversationId}`)
}

/**
 * 创建单聊会话
 */
export function createPrivateConversationApi(targetId) {
  return request.post('/conversations/private', {
    target_id: targetId,
  })
}

/**
 * 获取历史消息（分页）
 */
export function getMessagesApi(conversationId, page = 1, perPage = 20) {
  return request.get(
    `/conversations/${conversationId}/messages`,
    { params: { page, per_page: perPage } }
  )
}

/**
 * 标记会话已读
 */
export function markReadApi(conversationId) {
  return request.post('/conversations/read', {
    conversation_id: conversationId,
  })
}
