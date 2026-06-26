export function makeUser(overrides = {}) {
  return {
    id: 1,
    username: 'testuser',
    nickname: 'Test User',
    avatar: '',
    email: 'test@example.com',
    status: 1,
    ...overrides,
  }
}

export function makeConversation(overrides = {}) {
  return {
    id: 1,
    type: 1,
    name: '',
    avatar: '',
    unread_count: 0,
    last_message: null,
    updated_at: '2026-06-26T10:00:00Z',
    ...overrides,
  }
}

export function makeMessage(overrides = {}) {
  return {
    id: 1,
    conversation_id: 1,
    sender_id: 1,
    msg_type: 1,
    content: 'Hello',
    created_at: '2026-06-26T10:00:00Z',
    ...overrides,
  }
}
