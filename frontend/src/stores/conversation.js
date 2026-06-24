/**
 * 会话列表 Store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getConversationsApi, createPrivateConversationApi } from '@/api/chat'

export const useConversationStore = defineStore('conversation', () => {
  // ── State ────────────────
  const conversations = ref([])
  const loading = ref(false)

  // ── Getters ──────────────
  const sortedConversations = computed(() => {
    return [...conversations.value].sort((a, b) => {
      const timeA = a.last_message?.created_at || a.updated_at || ''
      const timeB = b.last_message?.created_at || b.updated_at || ''
      if (timeA > timeB) return -1
      if (timeA < timeB) return 1
      return 0
    })
  })

  const totalUnreadCount = computed(() => {
    return conversations.value.reduce(
      (sum, c) => sum + (c.unread_count || 0),
      0
    )
  })

  // ── Actions ──────────────
  async function fetchConversations() {
    loading.value = true
    try {
      const res = await getConversationsApi()
      if (res.code === 0) {
        conversations.value = res.data
      }
    } finally {
      loading.value = false
    }
  }

  function updateConversationLastMessage(message) {
    const conv = conversations.value.find(
      (c) => c.id === message.conversation_id
    )
    if (conv) {
      conv.last_message = {
        content: message.content,
        msg_type: message.msg_type,
        created_at: message.created_at,
      }
      conv.updated_at = message.created_at
    }
  }

  function incrementUnread(conversationId) {
    const conv = conversations.value.find((c) => c.id === conversationId)
    if (conv) {
      conv.unread_count = (conv.unread_count || 0) + 1
    }
  }

  function clearUnread(conversationId) {
    const conv = conversations.value.find((c) => c.id === conversationId)
    if (conv) {
      conv.unread_count = 0
    }
  }

  async function startConversation(targetId) {
    const res = await createPrivateConversationApi(targetId)
    if (res.code === 0) {
      await fetchConversations()
      return res.data
    }
    return null
  }

  return {
    conversations,
    loading,
    sortedConversations,
    totalUnreadCount,
    fetchConversations,
    updateConversationLastMessage,
    incrementUnread,
    clearUnread,
    startConversation,
  }
})
