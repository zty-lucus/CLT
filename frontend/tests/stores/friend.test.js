import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
  },
}))

vi.mock('../../src/api/friend', () => ({
  friendApi: {
    searchUsers: vi.fn(),
    sendRequest: vi.fn(),
    acceptRequest: vi.fn(),
    rejectRequest: vi.fn(),
    getFriendList: vi.fn(),
    getPendingRequests: vi.fn(),
    deleteFriend: vi.fn(),
  },
}))

import { ElMessage } from 'element-plus'
import { friendApi } from '../../src/api/friend'
import { useFriendStore } from '../../src/stores/friend'
import { makeUser } from '../helpers/factories'

function makeFriend(id, status = 1) {
  return { id, friend: makeUser({ id, status }) }
}

describe('FriendGetters', () => {
  it('friendCount returns list length', () => {
    const store = useFriendStore()
    store.friendList = [makeFriend(1), makeFriend(2), makeFriend(3)]
    expect(store.friendCount).toBe(3)
  })

  it('pendingReceivedCount returns received list length', () => {
    const store = useFriendStore()
    store.pendingReceived = [{ id: 1 }, { id: 2 }]
    expect(store.pendingReceivedCount).toBe(2)
  })

  it('onlineFriends filters by status === 1', () => {
    const store = useFriendStore()
    store.friendList = [makeFriend(1, 1), makeFriend(2, 0), makeFriend(3, 1)]
    expect(store.onlineFriends).toHaveLength(2)
    expect(store.onlineFriends[0].friend.id).toBe(1)
    expect(store.onlineFriends[1].friend.id).toBe(3)
  })

  it('offlineFriends filters by status === 0', () => {
    const store = useFriendStore()
    store.friendList = [makeFriend(1, 1), makeFriend(2, 0), makeFriend(3, 0)]
    expect(store.offlineFriends).toHaveLength(2)
  })
})

describe('SearchUsers', () => {
  it('populates searchResults', async () => {
    friendApi.searchUsers.mockResolvedValue({
      data: { users: [makeUser({ id: 1 }), makeUser({ id: 2 })] },
    })

    const store = useFriendStore()
    const result = await store.searchUsers('test')

    expect(store.searchResults).toHaveLength(2)
    expect(result).toHaveLength(2)
  })

  it('clears results on error', async () => {
    friendApi.searchUsers.mockRejectedValue(new Error('fail'))
    const store = useFriendStore()
    store.searchResults = [makeUser()]

    const result = await store.searchUsers('test')

    expect(store.searchResults).toEqual([])
    expect(result).toEqual([])
  })
})

describe('SendRequest', () => {
  it('calls API and removes user from searchResults', async () => {
    friendApi.sendRequest.mockResolvedValue({ message: 'ok' })
    friendApi.getPendingRequests.mockResolvedValue({ data: { sent: [], received: [] } })

    const store = useFriendStore()
    store.searchResults = [makeUser({ id: 1 }), makeUser({ id: 2 }), makeUser({ id: 3 })]
    await store.sendRequest(2, 'hello')

    expect(friendApi.sendRequest).toHaveBeenCalledWith({ addressee_id: 2, message: 'hello' })
    expect(store.searchResults.find((u) => u.id === 2)).toBeUndefined()
    expect(store.searchResults).toHaveLength(2)
  })

  it('calls ElMessage.success', async () => {
    friendApi.sendRequest.mockResolvedValue({ message: 'done' })
    friendApi.getPendingRequests.mockResolvedValue({ data: { sent: [], received: [] } })

    const store = useFriendStore()
    await store.sendRequest(1)

    expect(ElMessage.success).toHaveBeenCalledWith('done')
  })

  it('refreshes pending requests', async () => {
    friendApi.sendRequest.mockResolvedValue({ message: 'ok' })
    friendApi.getPendingRequests.mockResolvedValue({ data: { sent: [], received: [] } })

    const store = useFriendStore()
    await store.sendRequest(1)

    expect(friendApi.getPendingRequests).toHaveBeenCalled()
  })
})

describe('AcceptRejectRequest', () => {
  it('acceptRequest refreshes friendList and pendingRequests', async () => {
    friendApi.acceptRequest.mockResolvedValue({ message: 'ok' })
    friendApi.getFriendList.mockResolvedValue({ data: { friends: [] } })
    friendApi.getPendingRequests.mockResolvedValue({ data: { sent: [], received: [] } })

    const store = useFriendStore()
    await store.acceptRequest(1)

    expect(friendApi.acceptRequest).toHaveBeenCalledWith(1)
    expect(friendApi.getFriendList).toHaveBeenCalled()
    expect(friendApi.getPendingRequests).toHaveBeenCalled()
    expect(ElMessage.success).toHaveBeenCalled()
  })

  it('rejectRequest refreshes only pendingRequests', async () => {
    friendApi.rejectRequest.mockResolvedValue({ message: 'ok' })
    friendApi.getFriendList.mockClear()
    friendApi.getPendingRequests.mockResolvedValue({ data: { sent: [], received: [] } })

    const store = useFriendStore()
    await store.rejectRequest(1)

    expect(friendApi.rejectRequest).toHaveBeenCalledWith(1)
    expect(friendApi.getPendingRequests).toHaveBeenCalled()
    expect(ElMessage.info).toHaveBeenCalled()
  })
})

describe('DeleteFriend', () => {
  it('calls API and refreshes friendList', async () => {
    friendApi.deleteFriend.mockResolvedValue({ message: 'deleted' })
    friendApi.getFriendList.mockResolvedValue({ data: { friends: [] } })

    const store = useFriendStore()
    await store.deleteFriend(5)

    expect(friendApi.deleteFriend).toHaveBeenCalledWith(5)
    expect(friendApi.getFriendList).toHaveBeenCalled()
    expect(ElMessage.success).toHaveBeenCalled()
  })
})

describe('FetchFriendList', () => {
  it('populates friendList', async () => {
    const friends = [makeFriend(1), makeFriend(2)]
    friendApi.getFriendList.mockResolvedValue({ data: { friends } })

    const store = useFriendStore()
    await store.fetchFriendList()

    expect(store.friendList).toEqual(friends)
  })

  it('clears list on error', async () => {
    friendApi.getFriendList.mockRejectedValue(new Error('fail'))
    const store = useFriendStore()
    store.friendList = [makeFriend(1)]

    await store.fetchFriendList()
    expect(store.friendList).toEqual([])
  })
})

describe('FetchPendingRequests', () => {
  it('populates sent and received', async () => {
    friendApi.getPendingRequests.mockResolvedValue({
      data: { sent: [{ id: 1 }], received: [{ id: 2 }] },
    })

    const store = useFriendStore()
    await store.fetchPendingRequests()

    expect(store.pendingSent).toEqual([{ id: 1 }])
    expect(store.pendingReceived).toEqual([{ id: 2 }])
  })

  it('clears both on error', async () => {
    friendApi.getPendingRequests.mockRejectedValue(new Error('fail'))
    const store = useFriendStore()
    store.pendingSent = [{ id: 1 }]
    store.pendingReceived = [{ id: 2 }]

    await store.fetchPendingRequests()

    expect(store.pendingSent).toEqual([])
    expect(store.pendingReceived).toEqual([])
  })
})
