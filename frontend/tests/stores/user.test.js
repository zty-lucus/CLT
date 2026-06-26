import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('../../src/api/request', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
}))

import request from '../../src/api/request'
import { useUserStore } from '../../src/stores/user'

describe('UserStoreInit', () => {
  it('initializes token from localStorage', () => {
    localStorage.setItem('token', 'abc')
    const store = useUserStore()
    expect(store.token).toBe('abc')
  })

  it('initializes empty token when localStorage is empty', () => {
    const store = useUserStore()
    expect(store.token).toBe('')
  })

  it('initializes userInfo from localStorage', () => {
    localStorage.setItem('userInfo', JSON.stringify({ id: 1, nickname: 'Test' }))
    const store = useUserStore()
    expect(store.userInfo.id).toBe(1)
    expect(store.userInfo.nickname).toBe('Test')
  })

  it('initializes null userInfo when localStorage is empty', () => {
    const store = useUserStore()
    expect(store.userInfo).toBeNull()
  })
})

describe('LoginAction', () => {
  it('stores token and userInfo on success', async () => {
    request.post.mockResolvedValue({
      data: { token: 'xyz', user: { id: 1, nickname: 'Test' } },
    })
    const store = useUserStore()
    await store.login('testuser', 'password')

    expect(store.token).toBe('xyz')
    expect(store.userInfo.id).toBe(1)
  })

  it('persists to localStorage on success', async () => {
    request.post.mockResolvedValue({
      data: { token: 'xyz', user: { id: 1, nickname: 'Test' } },
    })
    const store = useUserStore()
    await store.login('testuser', 'password')

    expect(localStorage.getItem('token')).toBe('xyz')
    expect(JSON.parse(localStorage.getItem('userInfo')).id).toBe(1)
  })

  it('sends correct payload to API', async () => {
    request.post.mockResolvedValue({
      data: { token: 'x', user: {} },
    })
    const store = useUserStore()
    await store.login('myuser', 'mypass')

    expect(request.post).toHaveBeenCalledWith('/auth/login', {
      username: 'myuser',
      password: 'mypass',
    })
  })

  it('propagates error on failure', async () => {
    request.post.mockRejectedValue(new Error('Network error'))
    const store = useUserStore()
    await expect(store.login('u', 'p')).rejects.toThrow('Network error')
  })
})

describe('LogoutAction', () => {
  it('clears token and userInfo', () => {
    localStorage.setItem('token', 'abc')
    localStorage.setItem('userInfo', JSON.stringify({ id: 1 }))
    const store = useUserStore()
    store.token = 'abc'
    store.userInfo = { id: 1 }

    store.logout()

    expect(store.token).toBe('')
    expect(store.userInfo).toBeNull()
  })

  it('removes localStorage entries', () => {
    localStorage.setItem('token', 'abc')
    localStorage.setItem('userInfo', '{}')
    const store = useUserStore()
    store.logout()

    expect(localStorage.getItem('token')).toBeNull()
    expect(localStorage.getItem('userInfo')).toBeNull()
  })
})

describe('GetProfileAction', () => {
  it('updates userInfo from API response', async () => {
    request.get.mockResolvedValue({
      data: { id: 2, nickname: 'Updated' },
    })
    const store = useUserStore()
    await store.getProfile()

    expect(store.userInfo.nickname).toBe('Updated')
    expect(store.userInfo.id).toBe(2)
  })

  it('persists updated userInfo to localStorage', async () => {
    request.get.mockResolvedValue({
      data: { id: 2, nickname: 'Updated' },
    })
    const store = useUserStore()
    await store.getProfile()

    expect(JSON.parse(localStorage.getItem('userInfo')).nickname).toBe('Updated')
  })
})
