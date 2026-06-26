import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../../src/api/chat', () => ({
  getMessagesApi: vi.fn(),
  getConversationsApi: vi.fn(),
  createPrivateConversationApi: vi.fn(),
  markReadApi: vi.fn(),
}))

import { getMessagesApi, markReadApi } from '../../src/api/chat'
import { useChatStore } from '../../src/stores/chat'
import { makeMessage } from '../helpers/factories'

describe('ChatStoreState', () => {
  it('initializes with empty messages and null conversation', () => {
    const store = useChatStore()
    expect(store.messages).toEqual([])
    expect(store.currentConversationId).toBeNull()
    expect(store.totalMessages).toBe(0)
    expect(store.hasMore).toBe(false)
    expect(store.isLoading).toBe(false)
  })
})

describe('FetchMessages', () => {
  it('loads page 1 and replaces messages', async () => {
    const msgs = [makeMessage({ id: 1 }), makeMessage({ id: 2 })]
    getMessagesApi.mockResolvedValue({
      code: 0,
      data: { messages: msgs, total: 10, has_more: true },
    })

    const store = useChatStore()
    await store.fetchMessages(5, 1)

    expect(store.messages).toEqual(msgs)
    expect(store.totalMessages).toBe(10)
    expect(store.hasMore).toBe(true)
    expect(store.currentPage).toBe(1)
  })

  it('prepends older messages on subsequent pages', async () => {
    const existing = makeMessage({ id: 10 })
    getMessagesApi.mockResolvedValue({
      code: 0,
      data: { messages: [makeMessage({ id: 1 }), makeMessage({ id: 2 })], total: 10, has_more: true },
    })

    const store = useChatStore()
    store.messages = [existing]
    await store.fetchMessages(5, 2)

    expect(store.messages).toHaveLength(3)
    expect(store.messages[0].id).toBe(1)
    expect(store.messages[2].id).toBe(10)
  })

  it('sets isLoading during request', async () => {
    let resolve
    getMessagesApi.mockReturnValue(new Promise((r) => { resolve = r }))

    const store = useChatStore()
    const promise = store.fetchMessages(1, 1)
    expect(store.isLoading).toBe(true)

    resolve({ code: 0, data: { messages: [], total: 0, has_more: false } })
    await promise
    expect(store.isLoading).toBe(false)
  })

  it('resets isLoading on error', async () => {
    getMessagesApi.mockRejectedValue(new Error('fail'))
    const store = useChatStore()

    await store.fetchMessages(1, 1).catch(() => {})
    expect(store.isLoading).toBe(false)
  })
})

describe('LoadMoreMessages', () => {
  it('does nothing when hasMore is false', async () => {
    getMessagesApi.mockClear()
    const store = useChatStore()
    store.hasMore = false

    await store.loadMoreMessages()
    expect(getMessagesApi).not.toHaveBeenCalled()
  })

  it('does nothing when isLoading is true', async () => {
    getMessagesApi.mockClear()
    const store = useChatStore()
    store.hasMore = true
    store.isLoading = true

    await store.loadMoreMessages()
    expect(getMessagesApi).not.toHaveBeenCalled()
  })

  it('fetches next page', async () => {
    getMessagesApi.mockResolvedValue({
      code: 0,
      data: { messages: [], total: 0, has_more: false },
    })

    const store = useChatStore()
    store.currentConversationId = 5
    store.currentPage = 1
    store.hasMore = true

    await store.loadMoreMessages()
    expect(getMessagesApi).toHaveBeenCalledWith(5, 2)
  })
})

describe('SetCurrentConversation', () => {
  it('resets state and fetches messages', async () => {
    getMessagesApi.mockResolvedValue({
      code: 0,
      data: { messages: [], total: 0, has_more: false },
    })

    const store = useChatStore()
    store.messages = [makeMessage()]
    store.currentPage = 3
    store.hasMore = true

    store.setCurrentConversation(3)

    expect(store.currentConversationId).toBe(3)
    expect(store.messages).toEqual([])
    expect(store.currentPage).toBe(1)
    expect(store.hasMore).toBe(false)
    expect(getMessagesApi).toHaveBeenCalledWith(3, 1)
  })

  it('does not fetch when conversationId is null', () => {
    getMessagesApi.mockClear()
    const store = useChatStore()
    store.setCurrentConversation(null)

    expect(store.currentConversationId).toBeNull()
    expect(getMessagesApi).not.toHaveBeenCalled()
  })
})

describe('AddMessage', () => {
  it('appends new message', () => {
    const store = useChatStore()
    store.addMessage(makeMessage({ id: 1 }))
    expect(store.messages).toHaveLength(1)
  })

  it('ignores duplicate by id', () => {
    const store = useChatStore()
    store.addMessage(makeMessage({ id: 1 }))
    store.addMessage(makeMessage({ id: 1, content: 'different' }))
    expect(store.messages).toHaveLength(1)
  })

  it('allows different ids', () => {
    const store = useChatStore()
    store.addMessage(makeMessage({ id: 1 }))
    store.addMessage(makeMessage({ id: 2 }))
    expect(store.messages).toHaveLength(2)
  })
})

describe('MarkAsRead', () => {
  it('calls API with conversationId', async () => {
    markReadApi.mockResolvedValue({})
    const store = useChatStore()
    await store.markAsRead(5)
    expect(markReadApi).toHaveBeenCalledWith(5)
  })

  it('swallows errors silently', async () => {
    markReadApi.mockRejectedValue(new Error('fail'))
    const store = useChatStore()
    await expect(store.markAsRead(5)).resolves.toBeUndefined()
  })
})
