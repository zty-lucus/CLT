/**
 * 聊天状态 Store
 * 管理当前会话、消息列表、未读计数
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  getConversationsApi,
  getMessagesApi,
  createPrivateConversationApi,
  markReadApi,
} from '@/api/chat'

export const useChatStore = defineStore('chat', () => {
  // ── State ────────────────
  const currentConversationId = ref(null)
  const messages = ref([])
  const totalMessages = ref(0)
  const currentPage = ref(1)
  const hasMore = ref(false)
  const isLoading = ref(false)
  const sending = ref(false)

  // ── Getters ──────────────
  const currentMessages = computed(() => messages.value)

  const sortedMessages = computed(() => {
    return [...messages.value].sort((a, b) => {
      return new Date(a.created_at) - new Date(b.created_at)
    })
  })

  // ── Actions ──────────────
  async function fetchMessages(conversationId, page = 1) {
    isLoading.value = true
    try {
      const res = await getMessagesApi(conversationId, page)
      if (res.code === 0) {
        if (page === 1) {
          messages.value = res.data.messages
        } else {
          messages.value = [...res.data.messages, ...messages.value]
        }
        totalMessages.value = res.data.total
        currentPage.value = page
        hasMore.value = res.data.has_more
      }
    } finally {
      isLoading.value = false
    }
  }

  async function loadMoreMessages() {
    if (!hasMore.value || isLoading.value) return
    await fetchMessages(currentConversationId.value, currentPage.value + 1)
  }

  function setCurrentConversation(conversationId) {
    currentConversationId.value = conversationId
    messages.value = []
    currentPage.value = 1
    hasMore.value = false
    if (conversationId) {
      fetchMessages(conversationId)
    }
  }

  function addMessage(message) {
    const exists = messages.value.find((m) => m.id === message.id)
    if (!exists) {
      messages.value.push(message)
    }
  }

  function setSending(val) {
    sending.value = val
  }

  async function markAsRead(conversationId) {
    try {
      await markReadApi(conversationId)
    } catch (e) {
      // 静默处理
    }
  }

  return {
    currentConversationId,
    messages,
    totalMessages,
    currentPage,
    hasMore,
    isLoading,
    sending,
    currentMessages,
    sortedMessages,
    fetchMessages,
    loadMoreMessages,
    setCurrentConversation,
    addMessage,
    setSending,
    markAsRead,
  }
})
