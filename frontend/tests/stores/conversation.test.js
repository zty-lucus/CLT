import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../../src/api/chat', () => ({
  getConversationsApi: vi.fn(),
  createPrivateConversationApi: vi.fn(),
  getMessagesApi: vi.fn(),
  markReadApi: vi.fn(),
}))

import { getConversationsApi, createPrivateConversationApi } from '../../src/api/chat'
import { useConversationStore } from '../../src/stores/conversation'
import { makeConversation, makeMessage } from '../helpers/factories'

describe('SortedConversations', () => {
  it('sorts by last_message.created_at descending', () => {
    const store = useConversationStore()
    store.conversations = [
      makeConversation({ id: 1, last_message: { created_at: '2026-06-26T08:00:00Z' } }),
      makeConversation({ id: 2, last_message: { created_at: '2026-06-26T12:00:00Z' } }),
      makeConversation({ id: 3, last_message: { created_at: '2026-06-26T10:00:00Z' } }),
    ]

    const ids = store.sortedConversations.map((c) => c.id)
    expect(ids).toEqual([2, 3, 1])
  })

  it('falls back to updated_at when last_message is null', () => {
    const store = useConversationStore()
    store.conversations = [
      makeConversation({ id: 1, updated_at: '2026-06-26T08:00:00Z' }),
      makeConversation({ id: 2, updated_at: '2026-06-26T12:00:00Z' }),
    ]

    const ids = store.sortedConversations.map((c) => c.id)
    expect(ids).toEqual([2, 1])
  })

  it('handles mixed null and defined timestamps', () => {
    const store = useConversationStore()
    store.conversations = [
      makeConversation({ id: 1, last_message: { created_at: '2026-06-26T14:00:00Z' }, updated_at: '2026-06-26T08:00:00Z' }),
      makeConversation({ id: 2, last_message: null, updated_at: '2026-06-26T12:00:00Z' }),
    ]

    const ids = store.sortedConversations.map((c) => c.id)
    expect(ids).toEqual([1, 2])
  })
})

describe('TotalUnreadCount', () => {
  it('sums all unread counts', () => {
    const store = useConversationStore()
    store.conversations = [
      makeConversation({ id: 1, unread_count: 2 }),
      makeConversation({ id: 2, unread_count: 3 }),
      makeConversation({ id: 3, unread_count: 0 }),
    ]
    expect(store.totalUnreadCount).toBe(5)
  })

  it('returns 0 for empty list', () => {
    const store = useConversationStore()
    expect(store.totalUnreadCount).toBe(0)
  })
})

describe('FetchConversations', () => {
  it('loads and stores conversations', async () => {
    const convs = [makeConversation({ id: 1 }), makeConversation({ id: 2 })]
    getConversationsApi.mockResolvedValue({ code: 0, data: convs })

    const store = useConversationStore()
    await store.fetchConversations()

    expect(store.conversations).toEqual(convs)
  })

  it('sets loading during request', async () => {
    let resolve
    getConversationsApi.mockReturnValue(new Promise((r) => { resolve = r }))

    const store = useConversationStore()
    const promise = store.fetchConversations()
    expect(store.loading).toBe(true)

    resolve({ code: 0, data: [] })
    await promise
    expect(store.loading).toBe(false)
  })

  it('handles non-zero code', async () => {
    getConversationsApi.mockResolvedValue({ code: 1001, data: [] })
    const store = useConversationStore()
    await store.fetchConversations()

    expect(store.conversations).toEqual([])
  })
})

describe('UpdateConversationLastMessage', () => {
  it('updates matching conversation', () => {
    const store = useConversationStore()
    store.conversations = [makeConversation({ id: 1 })]

    const msg = makeMessage({ conversation_id: 1, content: 'Hi', msg_type: 1, created_at: '2026-06-26T15:00:00Z' })
    store.updateConversationLastMessage(msg)

    expect(store.conversations[0].last_message.content).toBe('Hi')
    expect(store.conversations[0].updated_at).toBe('2026-06-26T15:00:00Z')
  })

  it('does nothing for unknown conversation_id', () => {
    const store = useConversationStore()
    store.conversations = [makeConversation({ id: 1 })]

    store.updateConversationLastMessage(makeMessage({ conversation_id: 999 }))
    expect(store.conversations[0].last_message).toBeNull()
  })
})

describe('IncrementAndClearUnread', () => {
  it('increments existing unread_count', () => {
    const store = useConversationStore()
    store.conversations = [makeConversation({ id: 1, unread_count: 2 })]

    store.incrementUnread(1)
    expect(store.conversations[0].unread_count).toBe(3)
  })

  it('initializes to 1 when undefined', () => {
    const store = useConversationStore()
    store.conversations = [makeConversation({ id: 1 })]
    delete store.conversations[0].unread_count

    store.incrementUnread(1)
    expect(store.conversations[0].unread_count).toBe(1)
  })

  it('clearUnread sets unread_count to 0', () => {
    const store = useConversationStore()
    store.conversations = [makeConversation({ id: 1, unread_count: 5 })]

    store.clearUnread(1)
    expect(store.conversations[0].unread_count).toBe(0)
  })
})

describe('StartConversation', () => {
  it('creates and refreshes conversations', async () => {
    createPrivateConversationApi.mockResolvedValue({ code: 0, data: { id: 5 } })
    getConversationsApi.mockResolvedValue({ code: 0, data: [] })

    const store = useConversationStore()
    const result = await store.startConversation(99)

    expect(createPrivateConversationApi).toHaveBeenCalledWith(99)
    expect(getConversationsApi).toHaveBeenCalled()
    expect(result).toEqual({ id: 5 })
  })

  it('returns null on failure', async () => {
    createPrivateConversationApi.mockResolvedValue({ code: 1001 })

    const store = useConversationStore()
    const result = await store.startConversation(99)

    expect(result).toBeNull()
  })
})
