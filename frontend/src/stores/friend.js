import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { friendApi } from '@/api/friend'

export const useFriendStore = defineStore('friend', () => {
  // ============ State ============
  const friendList = ref([])           // 好友列表
  const pendingSent = ref([])          // 我发出的待处理申请
  const pendingReceived = ref([])      // 我收到的待处理申请
  const searchResults = ref([])        // 用户搜索结果
  const loading = ref(false)

  // ============ Getters ============
  const friendCount = computed(() => friendList.value.length)
  const pendingReceivedCount = computed(() => pendingReceived.value.length)
  const onlineFriends = computed(() =>
    friendList.value.filter(f => f.friend && f.friend.status === 1)
  )
  const offlineFriends = computed(() =>
    friendList.value.filter(f => !f.friend || f.friend.status === 0)
  )

  // ============ Actions ============

  /**
   * 搜索用户
   */
  async function searchUsers(keyword) {
    loading.value = true
    try {
      const res = await friendApi.searchUsers(keyword)
      searchResults.value = res.data.users || []
      return searchResults.value
    } catch {
      searchResults.value = []
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * 发送好友申请
   */
  async function sendRequest(addresseeId, message = '') {
    const res = await friendApi.sendRequest({ addressee_id: addresseeId, message })
    ElMessage.success(res.message || '好友申请已发送')
    // 从搜索结果中移除
    searchResults.value = searchResults.value.filter(u => u.id !== addresseeId)
    // 刷新待处理列表
    await fetchPendingRequests()
    return res
  }

  /**
   * 同意好友申请
   */
  async function acceptRequest(friendshipId) {
    const res = await friendApi.acceptRequest(friendshipId)
    ElMessage.success(res.message || '已同意好友申请')
    await Promise.all([fetchFriendList(), fetchPendingRequests()])
    return res
  }

  /**
   * 拒绝好友申请
   */
  async function rejectRequest(friendshipId) {
    const res = await friendApi.rejectRequest(friendshipId)
    ElMessage.info(res.message || '已拒绝好友申请')
    await fetchPendingRequests()
    return res
  }

  /**
   * 获取好友列表
   */
  async function fetchFriendList() {
    try {
      const res = await friendApi.getFriendList()
      friendList.value = res.data.friends || []
      return friendList.value
    } catch {
      friendList.value = []
      return []
    }
  }

  /**
   * 获取待处理的好友申请
   */
  async function fetchPendingRequests() {
    try {
      const res = await friendApi.getPendingRequests()
      pendingSent.value = res.data.sent || []
      pendingReceived.value = res.data.received || []
      return res.data
    } catch {
      pendingSent.value = []
      pendingReceived.value = []
      return { sent: [], received: [] }
    }
  }

  /**
   * 删除好友
   */
  async function deleteFriend(friendshipId) {
    const res = await friendApi.deleteFriend(friendshipId)
    ElMessage.success(res.message || '已删除好友')
    await fetchFriendList()
    return res
  }

  return {
    // State
    friendList,
    pendingSent,
    pendingReceived,
    searchResults,
    loading,
    // Getters
    friendCount,
    pendingReceivedCount,
    onlineFriends,
    offlineFriends,
    // Actions
    searchUsers,
    sendRequest,
    acceptRequest,
    rejectRequest,
    fetchFriendList,
    fetchPendingRequests,
    deleteFriend,
  }
})
