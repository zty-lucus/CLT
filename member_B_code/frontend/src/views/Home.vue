<template>
  <div class="home-page">
    <!-- 左侧会话列表 -->
    <aside class="home-sidebar">
      <div class="sidebar-header">
        <div class="sidebar-header-avatar">
          <el-avatar
            :size="36"
            :src="userStore.userInfo?.avatar"
          />
        </div>
        <span class="sidebar-header-name">
          {{ userStore.userInfo?.nickname }}
        </span>
        <el-dropdown trigger="click">
          <el-icon class="sidebar-header-menu">
            <MoreFilled />
          </el-icon>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="$router.push('/profile')">
                个人中心
              </el-dropdown-item>
              <el-dropdown-item @click="$router.push('/contacts')">
                通讯录
              </el-dropdown-item>
              <el-dropdown-item @click="handleLogout">
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>

      <!-- 搜索框 -->
      <div class="sidebar-search">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索会话"
          :prefix-icon="SearchIcon"
          clearable
          size="small"
        />
      </div>

      <!-- 会话Tab切换 -->
      <el-tabs v-model="activeTab" class="sidebar-tabs">
        <el-tab-pane label="聊天" name="chat" />
        <el-tab-pane label="通讯录" name="contacts" />
      </el-tabs>

      <!-- 会话列表 -->
      <div class="conversation-list" v-if="activeTab === 'chat'">
        <div
          v-for="conv in filteredConversations"
          :key="conv.id"
          class="conversation-item"
          :class="{ active: conv.id === chatStore.currentConversationId }"
          @click="selectConversation(conv)"
        >
          <el-avatar
            :size="40"
            :src="conv.avatar"
            class="conversation-avatar"
          >
            {{ getConvFirstChar(conv) }}
          </el-avatar>
          <div class="conversation-info">
            <div class="conversation-top">
              <span class="conversation-name">
                {{ getConvDisplayName(conv) }}
              </span>
              <span class="conversation-time">
                {{ formatTime(conv.last_message?.created_at) }}
              </span>
            </div>
            <div class="conversation-bottom">
              <span class="conversation-last-msg">
                {{ getLastMsgPreview(conv) }}
              </span>
              <el-badge
                v-if="conv.unread_count > 0"
                :value="conv.unread_count"
                :max="99"
                class="conversation-badge"
              />
            </div>
          </div>
        </div>
        <el-empty
          v-if="filteredConversations.length === 0"
          description="暂无会话"
        />
      </div>

      <!-- 通讯录Tab -->
      <div class="contacts-panel" v-else>
        <router-link to="/contacts" class="contacts-link">
          查看通讯录 →
        </router-link>
      </div>
    </aside>

    <!-- 右侧聊天窗口 -->
    <main class="home-main">
      <template v-if="chatStore.currentConversationId">
        <ChatWindow />
      </template>
      <template v-else>
        <div class="no-conversation">
          <el-empty description="选择一个会话开始聊天" :image-size="120" />
        </div>
      </template>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Search as SearchIcon } from '@element-plus/icons-vue'

import { useUserStore } from '@/stores/user'
import { useChatStore } from '@/stores/chat'
import { useConversationStore } from '@/stores/conversation'
import { initSocket, disconnectSocket } from '@/socket'
import ChatWindow from '@/components/ChatWindow.vue'

const router = useRouter()
const userStore = useUserStore()
const chatStore = useChatStore()
const conversationStore = useConversationStore()

const activeTab = ref('chat')
const searchKeyword = ref('')

// 初始化
onMounted(async () => {
  await conversationStore.fetchConversations()
  initSocket()
})

// 监听当前会话变化，标记已读
watch(
  () => chatStore.currentConversationId,
  (newVal) => {
    if (newVal) {
      conversationStore.clearUnread(newVal)
      chatStore.markAsRead(newVal)
    }
  }
)

// ── Computed ──────────────
const filteredConversations = computed(() => {
  const list = conversationStore.sortedConversations
  if (!searchKeyword.value) return list
  const kw = searchKeyword.value.toLowerCase()
  return list.filter((c) => {
    const name = getConvDisplayName(c).toLowerCase()
    return name.includes(kw)
  })
})

// ── Methods ───────────────
function getConvDisplayName(conv) {
  if (conv.type === 2) return conv.name || '群聊'
  return conv.name || '聊天'
}

function getConvFirstChar(conv) {
  const name = getConvDisplayName(conv)
  return name.charAt(0).toUpperCase()
}

function getLastMsgPreview(conv) {
  const msg = conv.last_message
  if (!msg) return ''
  if (msg.msg_type === 2) return '[文件]'
  if (msg.msg_type === 3) return '[图片]'
  if (msg.msg_type === 4) return '[系统通知]'
  return msg.content || ''
}

function formatTime(isoString) {
  if (!isoString) return ''
  const date = new Date(isoString)
  const now = new Date()
  const diff = now - date
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  if (now.toDateString() === date.toDateString()) {
    return `${hours}:${minutes}`
  }
  const month = (date.getMonth() + 1).toString()
  const day = date.getDate().toString()
  return `${month}/${day}`
}

function selectConversation(conv) {
  chatStore.setCurrentConversation(conv.id)
}

function handleLogout() {
  userStore.logout()
  disconnectSocket()
  router.push('/login')
}
</script>

<style scoped>
.home-page {
  display: flex;
  height: 100vh;
  background-color: #f5f5f5;
}

/* ── 左侧边栏 ───────────── */
.home-sidebar {
  width: 320px;
  min-width: 320px;
  background-color: #fff;
  border-right: 1px solid #e8e8e8;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  gap: 10px;
}

.sidebar-header-name {
  flex: 1;
  font-size: 16px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sidebar-header-menu {
  cursor: pointer;
  font-size: 18px;
  color: #666;
}

.sidebar-search {
  padding: 12px 16px;
}

.sidebar-tabs {
  padding: 0 16px;
}

.sidebar-tabs :deep(.el-tabs__header) {
  margin-bottom: 0;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
}

.conversation-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  cursor: pointer;
  transition: background-color 0.2s;
  gap: 12px;
}

.conversation-item:hover {
  background-color: #f5f5f5;
}

.conversation-item.active {
  background-color: #e6f7ff;
}

.conversation-avatar {
  flex-shrink: 0;
}

.conversation-info {
  flex: 1;
  min-width: 0;
}

.conversation-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.conversation-name {
  font-size: 14px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 160px;
}

.conversation-time {
  font-size: 12px;
  color: #999;
  flex-shrink: 0;
}

.conversation-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4px;
}

.conversation-last-msg {
  font-size: 13px;
  color: #999;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 180px;
}

.conversation-badge {
  flex-shrink: 0;
}

.contacts-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.contacts-link {
  text-decoration: none;
  color: #409eff;
  font-size: 15px;
}

/* ── 右侧主区域 ─────────── */
.home-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.no-conversation {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
