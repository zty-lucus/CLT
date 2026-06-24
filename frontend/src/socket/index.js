/**
 * Socket.IO 客户端初始化与事件监听
 */
import { io } from 'socket.io-client'
import { useUserStore } from '@/stores/user'
import { useChatStore } from '@/stores/chat'
import { useConversationStore } from '@/stores/conversation'

let socket = null

/**
 * 初始化 Socket.IO 连接
 */
export function initSocket() {
  const userStore = useUserStore()
  const token = userStore.token

  if (!token) {
    console.warn('[Socket] 未登录，无法建立 WebSocket 连接')
    return null
  }

  if (socket && socket.connected) {
    return socket
  }

  socket = io('http://localhost:5000', {
    transports: ['websocket', 'polling'],
    auth: { token },
    reconnection: true,
    reconnectionDelay: 3000,
    reconnectionAttempts: 5,
  })

  socket.on('connect', () => {
    console.log('[Socket] 已连接:', socket.id)
  })

  socket.on('disconnect', (reason) => {
    console.log('[Socket] 已断开:', reason)
  })

  socket.on('connect_error', (error) => {
    console.error('[Socket] 连接错误:', error.message)
  })

  // ── 新消息事件 ──────────
  socket.on('new_message', (message) => {
    const chatStore = useChatStore()
    const conversationStore = useConversationStore()

    // 如果正在当前会话中查看，则添加到消息列表
    if (chatStore.currentConversationId === message.conversation_id) {
      chatStore.addMessage(message)
      // 标记已读
      socket.emit('msg_read', {
        token: userStore.token,
        conversation_id: message.conversation_id,
      })
    } else {
      // 增加未读计数
      conversationStore.incrementUnread(message.conversation_id)
    }

    // 更新会话列表的最后消息
    conversationStore.updateConversationLastMessage(message)
  })

  // ── 用户上线/下线 ──────
  socket.on('user_online', (data) => {
    console.log('[Socket] 用户上线:', data.user_id)
  })

  socket.on('user_offline', (data) => {
    console.log('[Socket] 用户下线:', data.user_id)
  })

  // ── 正在输入 ───────────
  socket.on('user_typing', (data) => {
    // 可由 ChatWindow 组件进一步处理
    window.dispatchEvent(
      new CustomEvent('user-typing', { detail: data })
    )
  })

  return socket
}

/**
 * 获取 socket 实例
 */
export function getSocket() {
  return socket
}

/**
 * 发送消息
 */
export function sendSocketMessage(data) {
  if (!socket || !socket.connected) {
    console.error('[Socket] 未连接，无法发送消息')
    return
  }
  const userStore = useUserStore()
  socket.emit('send_message', {
    ...data,
    token: userStore.token,
  })
}

/**
 * 发送"正在输入"状态
 */
export function sendTypingEvent(conversationId) {
  if (!socket || !socket.connected) return
  const userStore = useUserStore()
  socket.emit('typing', {
    token: userStore.token,
    conversation_id: conversationId,
  })
}

/**
 * 标记已读
 */
export function sendMarkRead(conversationId) {
  if (!socket || !socket.connected) return
  const userStore = useUserStore()
  socket.emit('msg_read', {
    token: userStore.token,
    conversation_id: conversationId,
  })
}

/**
 * 断开 Socket 连接
 */
export function disconnectSocket() {
  if (socket) {
    socket.disconnect()
    socket = null
  }
}
