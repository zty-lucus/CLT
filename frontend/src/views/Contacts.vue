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

// Tab 状态
const activeTab = ref('friends')

// 搜索状态
const searchKeyword = ref('')
const searchResults = ref([])
const searchLoading = ref(false)
const hasSearched = ref(false)

// 添加好友状态
const addDialogVisible = ref(false)
const addTargetUser = ref(null)
const addLoading = ref(false)
const addingUserId = ref(null)
const addForm = ref({ message: '' })

// 加载状态
const loading = ref(false)

// ============ 生命周期 ============

onMounted(async () => {
  loading.value = true
  await Promise.all([
    friendStore.fetchFriendList(),
    friendStore.fetchPendingRequests(),
  ])
  loading.value = false
})

// ============ 搜索 ============

async function handleSearch() {
  const keyword = searchKeyword.value.trim()
  if (keyword.length < 2) {
    return
  }
  hasSearched.value = true
  searchLoading.value = true
  try {
    searchResults.value = await friendStore.searchUsers(keyword)
  } finally {
    searchLoading.value = false
  }
}

// ============ 添加好友 ============

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
    // 从搜索结果移除
    searchResults.value = searchResults.value.filter(
      u => u.id !== addTargetUser.value.id
    )
  } finally {
    addLoading.value = false
    addingUserId.value = null
  }
}

// ============ 好友申请处理 ============

async function handleAccept(friendshipId) {
  await friendStore.acceptRequest(friendshipId)
}

async function handleReject(friendshipId) {
  await friendStore.rejectRequest(friendshipId)
}

// ============ 删除好友 ============

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
  } catch {
    // 用户取消
  }
}

// ============ 工具函数 ============

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
  background: #fff;
}
.contacts-header {
  padding: 16px 20px 0;
  border-bottom: 1px solid #f0f0f0;
}
.contacts-header h3 {
  margin: 0 0 8px;
  font-size: 18px;
}
.contacts-tabs {
  margin-bottom: -1px;
}
.badge-item {
  margin-left: 6px;
}
.tab-content {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

/* 搜索 */
.search-box {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

/* 搜索结果 */
.search-results {
  padding: 0;
}
.search-user-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  border-bottom: 1px solid #f5f5f5;
  transition: background 0.2s;
}
.search-user-item:hover {
  background: #fafafa;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}
.user-detail {
  display: flex;
  flex-direction: column;
}
.user-name {
  font-size: 14px;
  font-weight: 500;
}
.user-username {
  font-size: 12px;
  color: #999;
}

/* 好友申请 */
.request-section {
  margin-bottom: 16px;
}
.section-title {
  padding: 12px 20px 8px;
  font-size: 14px;
  color: #666;
  font-weight: 500;
}
.request-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  border-bottom: 1px solid #f5f5f5;
}
.request-item:hover {
  background: #fafafa;
}
.request-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}
.request-detail {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.request-name {
  font-size: 14px;
  font-weight: 500;
}
.request-msg {
  font-size: 12px;
  color: #999;
}
.request-time {
  font-size: 11px;
  color: #ccc;
}
.request-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}
</style>
