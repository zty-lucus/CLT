<template>
  <div class="home-page">
    <!-- 左侧会话列表 -->
    <aside class="home-sidebar">
      <!-- 侧边栏头部 -->
      <div class="sidebar-header">
        <el-avatar
          :size="36"
          :src="userStore.userInfo?.avatar"
          class="sidebar-header-avatar"
        >
          {{ userStore.userInfo?.nickname?.charAt(0) || 'U' }}
        </el-avatar>
        <div class="sidebar-header-info">
          <span class="sidebar-header-name">
            {{ userStore.userInfo?.nickname || userStore.userInfo?.username }}
          </span>
          <span class="sidebar-header-status">
            <span class="status-dot"></span> 在线
          </span>
        </div>
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
          placeholder="搜索会话或联系人"
          :prefix-icon="SearchIcon"
          clearable
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
            :size="44"
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
              <span
                v-if="conv.unread_count > 0"
                class="unread-badge"
              >
                {{ conv.unread_count > 99 ? '99+' : conv.unread_count }}
              </span>
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
          <div class="empty-state">
            <img src="/logo3.png" alt="logo" class="empty-logo" />
            <h3>欢迎使用校园即时通信</h3>
            <p>从左侧选择会话开始聊天，或前往通讯录添加好友</p>
            <div class="empty-actions">
              <el-button type="primary" @click="$router.push('/contacts')">
                查看通讯录
              </el-button>
            </div>
          </div>
        </div>
      </template>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Search as SearchIcon, MoreFilled } from '@element-plus/icons-vue'

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
/* ═══════════════════════════════════════
   Campus IM Home — CSS Visual Only
   DOM / JS / 交互逻辑零改动
   ═══════════════════════════════════════ */
.home-page {
  display: flex;
  height: 100vh;
  background: linear-gradient(155deg, #F0F4FF 0%, #EAF0FE 25%, #F4F0FF 55%, #EDF6FF 100%);
  position: relative;
}

/* ── 左侧边栏 ─────────────────────── */
.home-sidebar {
  width: 340px;
  min-width: 340px;
  background: rgba(255, 255, 255, 0.78);
  backdrop-filter: blur(24px) saturate(160%);
  -webkit-backdrop-filter: blur(24px) saturate(160%);
  border-right: 1px solid rgba(255, 255, 255, 0.5);
  display: flex;
  flex-direction: column;
}

/* ── 侧边栏头部 ───────────────────── */
.sidebar-header {
  display: flex;
  align-items: center;
  padding: 18px 20px;
  border-bottom: 1px solid rgba(91, 124, 250, 0.06);
  gap: 12px;
}

.sidebar-header-avatar {
  flex-shrink: 0;
  background: linear-gradient(135deg, #5B7CFA 0%, #54C6EB 100%);
  color: #fff;
  font-weight: 600;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(91, 124, 250, 0.2);
}

.sidebar-header-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.sidebar-header-name {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a2e;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sidebar-header-status {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #16a34a;
  font-weight: 500;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #34C759;
  box-shadow: 0 0 0 2px rgba(52, 199, 89, 0.18);
}

.sidebar-header-menu {
  cursor: pointer;
  font-size: 18px;
  color: #9DA3B0;
  transition: color 200ms ease;
  flex-shrink: 0;
}

.sidebar-header-menu:hover {
  color: #1a1a2e;
}

/* ── 搜索框 ───────────────────────── */
.sidebar-search {
  padding: 14px 16px 10px;
}

.sidebar-search :deep(.el-input__wrapper) {
  border-radius: 12px;
  background: rgba(91, 124, 250, 0.03);
  box-shadow: none;
  border: 1px solid rgba(91, 124, 250, 0.08);
  transition: all 200ms ease;
}

.sidebar-search :deep(.el-input__wrapper:hover) {
  border-color: rgba(91, 124, 250, 0.18);
  background: rgba(91, 124, 250, 0.05);
}

.sidebar-search :deep(.el-input__wrapper.is-focus) {
  border-color: #5B7CFA;
  background: rgba(91, 124, 250, 0.04);
  box-shadow: 0 0 0 3px rgba(91, 124, 250, 0.08);
}

/* ── Tab 切换 ──────────────────────── */
.sidebar-tabs {
  padding: 0 16px;
}

.sidebar-tabs :deep(.el-tabs__header) {
  margin-bottom: 0;
}

.sidebar-tabs :deep(.el-tabs__item) {
  font-size: 13px;
  font-weight: 500;
  padding: 0 14px;
  height: 38px;
  line-height: 38px;
  color: #8890a0;
  transition: all 200ms ease;
}

.sidebar-tabs :deep(.el-tabs__item.is-active) {
  color: #5B7CFA;
  font-weight: 600;
}

.sidebar-tabs :deep(.el-tabs__active-bar) {
  background: linear-gradient(90deg, #5B7CFA 0%, #54C6EB 100%);
  height: 2.5px;
  border-radius: 2px;
}

.sidebar-tabs :deep(.el-tabs__nav-wrap::after) {
  background-color: rgba(91, 124, 250, 0.06);
}

/* ── 会话列表 ──────────────────────── */
.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 6px 8px;
}

.conversation-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  cursor: pointer;
  transition: all 200ms ease;
  gap: 12px;
  border-radius: 12px;
  margin-bottom: 2px;
}

.conversation-item:hover {
  background: rgba(91, 124, 250, 0.05);
}

.conversation-item.active {
  background: rgba(91, 124, 250, 0.08);
  box-shadow: inset 3px 0 0 #5B7CFA;
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
  margin-bottom: 4px;
}

.conversation-name {
  font-size: 14px;
  font-weight: 500;
  color: #1a1a2e;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 160px;
}

.conversation-item.active .conversation-name {
  color: #5B7CFA;
  font-weight: 600;
}

.conversation-time {
  font-size: 11px;
  color: #9DA3B0;
  flex-shrink: 0;
}

.conversation-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.conversation-last-msg {
  font-size: 13px;
  color: #9DA3B0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 180px;
}

/* ── 未读角标 ──────────────────────── */
.unread-badge {
  flex-shrink: 0;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 10px;
  background: linear-gradient(135deg, #5B7CFA 0%, #7B6CF6 100%);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  box-shadow: 0 1px 4px rgba(91, 124, 250, 0.3);
}

/* ── 通讯录入口 ───────────────────── */
.contacts-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.contacts-link {
  text-decoration: none;
  color: #5B7CFA;
  font-size: 14px;
  font-weight: 500;
  transition: all 200ms ease;
  padding: 8px 16px;
  border-radius: 10px;
}

.contacts-link:hover {
  background: rgba(91, 124, 250, 0.06);
  color: #4A6AE8;
}

/* ── 右侧主区域 ───────────────────── */
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
  background:
    radial-gradient(ellipse at 30% 40%, rgba(91, 124, 250, 0.04) 0%, transparent 50%),
    radial-gradient(ellipse at 70% 60%, rgba(84, 198, 235, 0.04) 0%, transparent 50%),
    transparent;
}

.empty-state {
  text-align: center;
  max-width: 380px;
  padding: 40px 32px;
}

.empty-logo {
  width: 108px;
  height: 108px;
  object-fit: contain;
  margin-bottom: 28px;
  opacity: 0.92;
  filter: drop-shadow(0 4px 12px rgba(91, 124, 250, 0.12));
}

.empty-state h3 {
  font-size: 22px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 10px;
  letter-spacing: -0.02em;
}

.empty-state p {
  font-size: 14px;
  color: #8890a0;
  margin: 0 0 28px;
  line-height: 1.7;
}

.empty-actions {
  display: flex;
  justify-content: center;
}

.empty-actions .el-button {
  height: 44px;
  border-radius: 12px;
  padding: 0 32px;
  font-size: 14px;
  font-weight: 600;
  background: linear-gradient(135deg, #5B7CFA 0%, #7B6CF6 50%, #54C6EB 100%);
  background-size: 200% 200%;
  border: none;
  box-shadow: 0 2px 10px rgba(91, 124, 250, 0.25);
  transition: all 250ms ease;
}

.empty-actions .el-button:hover {
  background-position: 100% 0;
  box-shadow: 0 4px 16px rgba(91, 124, 250, 0.35);
  transform: translateY(-1px);
}

.empty-actions .el-button:active {
  transform: translateY(0);
}

/* ── 空状态插画区 ─────────────────── */
.conversation-list :deep(.el-empty) {
  padding: 48px 0 32px;
}

.conversation-list :deep(.el-empty__image) {
  width: 140px;
  height: 140px;
  opacity: 0.6;
  filter: hue-rotate(200deg) saturate(0.6) brightness(1.05);
}

.conversation-list :deep(.el-empty__description p) {
  font-size: 13px;
  color: #9DA3B0;
  margin-top: 8px;
}

/* ── 响应式 ───────────────────────── */
@media (max-width: 900px) {
  .home-sidebar {
    width: 100%;
    min-width: 100%;
  }
}
</style>
