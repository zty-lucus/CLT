<template>
  <div class="contacts-page">
    <!-- 顶部标题栏 -->
    <div class="contacts-header">
      <h3>通讯录</h3>
      <el-tabs v-model="activeTab" class="contacts-tabs">
        <el-tab-pane label="好友列表" name="friends">
          <template #label>
            <span>好友列表 ({{ friendStore.friendCount }})</span>
          </template>
        </el-tab-pane>
        <el-tab-pane name="requests">
          <template #label>
            <span>
              好友申请
              <el-badge
                v-if="friendStore.pendingReceivedCount > 0"
                :value="friendStore.pendingReceivedCount"
                class="badge-item"
              />
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="搜索添加" name="search" />
      </el-tabs>
    </div>

    <!-- 好友列表 Tab -->
    <div v-if="activeTab === 'friends'" class="tab-content">
      <ContactList
        :friends="friendStore.friendList"
        :loading="loading"
        @delete-friend="handleDeleteFriend"
      />
    </div>

    <!-- 好友申请 Tab -->
    <div v-if="activeTab === 'requests'" class="tab-content">
      <!-- 收到的申请 -->
      <div v-if="friendStore.pendingReceived.length > 0" class="request-section">
        <h4 class="section-title">收到的申请 ({{ friendStore.pendingReceived.length }})</h4>
        <div
          v-for="req in friendStore.pendingReceived"
          :key="req.id"
          class="request-item"
        >
          <div class="request-info">
            <el-avatar :size="40">
              {{ (req.friend?.nickname || 'U')[0].toUpperCase() }}
            </el-avatar>
            <div class="request-detail">
              <span class="request-name">{{ req.friend?.nickname || req.friend?.username }}</span>
              <span class="request-msg">{{ req.request_message || '请求添加您为好友' }}</span>
              <span class="request-time">{{ formatTime(req.created_at) }}</span>
            </div>
          </div>
          <div class="request-actions">
            <el-button type="primary" size="small" @click="handleAccept(req.id)">
              同意
            </el-button>
            <el-button size="small" @click="handleReject(req.id)">
              拒绝
            </el-button>
          </div>
        </div>
      </div>

      <!-- 发出的申请 -->
      <div v-if="friendStore.pendingSent.length > 0" class="request-section">
        <h4 class="section-title">发出的申请 ({{ friendStore.pendingSent.length }})</h4>
        <div
          v-for="req in friendStore.pendingSent"
          :key="req.id"
          class="request-item"
        >
          <div class="request-info">
            <el-avatar :size="40">
              {{ (req.friend?.nickname || 'U')[0].toUpperCase() }}
            </el-avatar>
            <div class="request-detail">
              <span class="request-name">{{ req.friend?.nickname || req.friend?.username }}</span>
              <span class="request-msg">等待对方验证</span>
              <span class="request-time">{{ formatTime(req.created_at) }}</span>
            </div>
          </div>
          <el-tag type="warning" size="small">等待验证</el-tag>
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty
        v-if="
          friendStore.pendingReceived.length === 0 &&
          friendStore.pendingSent.length === 0
        "
        description="暂无好友申请"
      />
    </div>

    <!-- 搜索添加 Tab -->
    <div v-if="activeTab === 'search'" class="tab-content">
      <div class="search-box">
        <el-input
          v-model="searchKeyword"
          placeholder="输入用户名或昵称搜索（至少2个字符）"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button :loading="searchLoading" @click="handleSearch">
              搜索
            </el-button>
          </template>
        </el-input>
      </div>

      <!-- 搜索结果 -->
      <div v-if="searchResults.length > 0" class="search-results">
        <div
          v-for="user in searchResults"
          :key="user.id"
          class="search-user-item"
        >
          <div class="user-info">
            <el-avatar :size="40">
              {{ (user.nickname || user.username)[0].toUpperCase() }}
            </el-avatar>
            <div class="user-detail">
              <span class="user-name">{{ user.nickname || user.username }}</span>
              <span class="user-username">@{{ user.username }}</span>
            </div>
          </div>
          <el-button
            type="primary"
            size="small"
            :loading="addingUserId === user.id"
            @click="handleAddFriend(user)"
          >
            添加好友
          </el-button>
        </div>
      </div>

      <!-- 搜索空结果 -->
      <el-empty
        v-if="hasSearched && searchResults.length === 0 && !searchLoading"
        description="未找到匹配的用户"
      />
      <el-empty
        v-if="!hasSearched"
        description="输入关键词搜索用户"
      />
    </div>

    <!-- 添加好友对话框 -->
    <el-dialog v-model="addDialogVisible" title="添加好友" width="400px">
      <el-form :model="addForm">
        <el-form-item label="对方">
          <span>{{ addTargetUser?.nickname || addTargetUser?.username }}</span>
        </el-form-item>
        <el-form-item label="验证消息">
          <el-input
            v-model="addForm.message"
            type="textarea"
            :rows="3"
            placeholder="你好，我是..."
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="addLoading" @click="confirmAddFriend">
          发送申请
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessageBox } from 'element-plus'
import { useFriendStore } from '@/stores/friend'
import ContactList from '@/components/ContactList.vue'

const friendStore = useFriendStore()

const activeTab = ref('friends')
const searchKeyword = ref('')
const searchResults = ref([])
const searchLoading = ref(false)
const hasSearched = ref(false)

const addDialogVisible = ref(false)
const addTargetUser = ref(null)
const addLoading = ref(false)
const addingUserId = ref(null)
const addForm = ref({ message: '' })

const loading = ref(false)

onMounted(async () => {
  loading.value = true
  await Promise.all([
    friendStore.fetchFriendList(),
    friendStore.fetchPendingRequests(),
  ])
  loading.value = false
})

async function handleSearch() {
  const keyword = searchKeyword.value.trim()
  if (keyword.length < 2) return
  hasSearched.value = true
  searchLoading.value = true
  try {
    searchResults.value = await friendStore.searchUsers(keyword)
  } finally {
    searchLoading.value = false
  }
}

function handleAddFriend(user) {
  addTargetUser.value = user
  addForm.value.message = `你好，我是...`
  addDialogVisible.value = true
}

async function confirmAddFriend() {
  if (!addTargetUser.value) return
  addLoading.value = true
  addingUserId.value = addTargetUser.value.id
  try {
    await friendStore.sendRequest(addTargetUser.value.id, addForm.value.message)
    addDialogVisible.value = false
    searchResults.value = searchResults.value.filter(
      u => u.id !== addTargetUser.value.id
    )
  } finally {
    addLoading.value = false
    addingUserId.value = null
  }
}

async function handleAccept(friendshipId) {
  await friendStore.acceptRequest(friendshipId)
}

async function handleReject(friendshipId) {
  await friendStore.rejectRequest(friendshipId)
}

async function handleDeleteFriend(friendship) {
  try {
    await ElMessageBox.confirm(
      `确定要删除好友「${friendship.friend?.nickname || friendship.friend?.username}」吗？`,
      '删除好友',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await friendStore.deleteFriend(friendship.id)
  } catch {}
}

function formatTime(isoString) {
  if (!isoString) return ''
  const date = new Date(isoString)
  const now = new Date()
  const diff = now - date
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return date.toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.contacts-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
}

/* ── 顶部标题栏 ─────────────────── */
.contacts-header {
  padding: 20px 24px 0;
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

.contacts-header h3 {
  margin: 0 0 12px;
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--color-text);
}

.contacts-tabs {
  margin-bottom: -1px;
}

.badge-item {
  margin-left: 4px;
}

.tab-content {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

/* ── 搜索 ──────────────────────── */
.search-box {
  padding: 16px 20px;
}

.search-box :deep(.el-input__wrapper) {
  border-radius: 12px;
  background: var(--color-bg);
  box-shadow: none;
  border: 1px solid transparent;
  transition: border-color 200ms ease, box-shadow 200ms ease;
}

.search-box :deep(.el-input__wrapper:hover) {
  border-color: var(--color-border);
}

.search-box :deep(.el-input__wrapper.is-focus) {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(79, 110, 247, 0.1);
}

.search-box :deep(.el-input-group__append) {
  border-radius: 0 12px 12px 0;
  background: var(--color-bg);
}

/* ── 搜索结果 ──────────────────── */
.search-results {
  padding: 0;
}

.search-user-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  margin: 0 8px 2px;
  border-radius: 12px;
  transition: background-color 200ms ease;
}

.search-user-item:hover {
  background-color: var(--color-surface-hover);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info :deep(.el-avatar) {
  background-color: var(--color-primary-bg);
  color: var(--color-primary);
  font-weight: 600;
}

.user-detail {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.user-name {
  font-size: var(--text-base);
  font-weight: 500;
  color: var(--color-text);
}

.user-username {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

/* ── 好友申请 ──────────────────── */
.request-section {
  margin-bottom: 8px;
}

.section-title {
  padding: 12px 20px 4px;
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  font-weight: 500;
}

.request-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  margin: 0 8px 2px;
  border-radius: 12px;
  transition: background-color 200ms ease;
}

.request-item:hover {
  background-color: var(--color-surface-hover);
}

.request-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.request-info :deep(.el-avatar) {
  background-color: var(--color-primary-bg);
  color: var(--color-primary);
  font-weight: 600;
}

.request-detail {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.request-name {
  font-size: var(--text-base);
  font-weight: 500;
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.request-msg {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

.request-time {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.request-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.request-actions .el-button {
  border-radius: 8px;
}
</style>
