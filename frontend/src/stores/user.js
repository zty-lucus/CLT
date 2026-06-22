import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  // State
  const token = ref(localStorage.getItem('token') || '')
  const refreshToken = ref(localStorage.getItem('refreshToken') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

  // Getters
  const isLoggedIn = computed(() => !!token.value)
  const userId = computed(() => userInfo.value?.id || null)
  const username = computed(() => userInfo.value?.username || '')
  const nickname = computed(() => userInfo.value?.nickname || userInfo.value?.username || '')

  // Actions
  async function login(username, password) {
    const res = await authApi.login({ username, password })
    setAuthData(res.data)
    return res
  }

  async function register(formData) {
    const res = await authApi.register(formData)
    setAuthData(res.data)
    return res
  }

  async function fetchUserInfo() {
    try {
      const res = await authApi.getMe()
      userInfo.value = res.data
      localStorage.setItem('userInfo', JSON.stringify(res.data))
    } catch {
      // Token可能已过期
      logout()
    }
  }

  function setAuthData(data) {
    token.value = data.access_token
    refreshToken.value = data.refresh_token
    userInfo.value = data.user
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('refreshToken', data.refresh_token)
    localStorage.setItem('userInfo', JSON.stringify(data.user))
  }

  function logout() {
    token.value = ''
    refreshToken.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('userInfo')
  }

  return {
    token,
    refreshToken,
    userInfo,
    isLoggedIn,
    userId,
    username,
    nickname,
    login,
    register,
    fetchUserInfo,
    logout,
  }
})
