<template>
  <div class="chat-window">
    <!-- 顶部：会话标题栏 -->
    <header class="chat-header">
      <div class="chat-header-info">
        <el-avatar
          :size="36"
          :src="currentConv?.avatar"
        >
          {{ displayName?.charAt(0) }}
        </el-avatar>
        <div class="chat-header-text">
          <span class="chat-header-name">{{ displayName }}</span>
          <span class="chat-header-status">
            {{ isGroup ? `${currentConv?.members?.length || 0} 名成员` : '在线' }}
          </span>
        </div>
      </div>
      <div class="chat-header-actions">
        <el-button
          v-if="isGroup"
          text
          @click="showGroupManage = true"
        >
          群设置
        </el-button>
      </div>
    </header>

    <!-- 中部：消息列表 -->
    <div
      ref="messageListRef"
      class="chat-messages"
      @scroll="handleScroll"
    >
      <div v-if="chatStore.hasMore" class="load-more">
        <el-button
          text
          :loading="chatStore.isLoading"
          @click="chatStore.loadMoreMessages()"
        >
          加载更多消息
        </el-button>
      </div>
      <div
        v-for="msg in chatStore.sortedMessages"
        :key="msg.id"
        class="message-wrapper"
      >
        <MessageItem
          :message="msg"
          :is-self="msg.sender_id === userStore.userInfo?.id"
        />
      </div>
      <div ref="messageBottomRef" class="message-bottom" />
    </div>

    <!-- 底部：输入区域 -->
    <footer class="chat-input-area">
      <div class="chat-input-tools">
        <el-upload
          :before-upload="handleFileUpload"
          :show-file-list="false"
          accept=".doc,.docx,.pdf,.txt,.jpg,.jpeg,.png,.gif,.zip,.rar"
        >
          <el-button text>
            <el-icon :size="18"><Link /></el-icon>
          </el-button>
        </el-upload>
      </div>
      <div class="chat-input-box">
        <el-input
          v-model="inputText"
          type="textarea"
          :rows="3"
          placeholder="输入消息..."
          resize="none"
          @keydown.enter.exact.prevent="sendTextMessage"
          @input="handleTyping"
        />
        <el-button
          type="primary"
          :disabled="!inputText.trim()"
          :loading="chatStore.sending"
          @click="sendTextMessage"
        >
          发送
        </el-button>
      </div>
    </footer>

    <!-- 群管理弹窗 -->
    <GroupManage
      v-if="isGroup"
      v-model="showGroupManage"
      :conversation-id="chatStore.currentConversationId"
      :detail="currentConv"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'

import { useUserStore } from '@/stores/user'
import { useChatStore } from '@/stores/chat'
import { useConversationStore } from '@/stores/conversation'
import { sendSocketMessage, sendTypingEvent } from '@/socket'
import { getConversationDetailApi } from '@/api/chat'
import { uploadFileApi } from '@/api/file'
import MessageItem from '@/components/MessageItem.vue'
import GroupManage from '@/components/GroupManage.vue'

const userStore = useUserStore()
const chatStore = useChatStore()
const conversationStore = useConversationStore()

const inputText = ref('')
const currentConv = ref(null)
const showGroupManage = ref(false)
const messageListRef = ref(null)
const messageBottomRef = ref(null)
let typingTimer = null

const isGroup = computed(() => currentConv.value?.type === 2)
const displayName = computed(() => {
  if (!currentConv.value) return ''
  if (currentConv.value.type === 2) return currentConv.value.name || '群聊'
  return currentConv.value.name || '聊天'
})

// 加载会话详情
onMounted(async () => {
  await loadConversationDetail()
  scrollToBottom()
})

watch(
  () => chatStore.currentConversationId,
  async () => {
    await loadConversationDetail()
    nextTick(() => scrollToBottom())
  }
)

// 新消息时滚动到底部
watch(
  () => chatStore.sortedMessages.length,
  () => {
    nextTick(() => {
      const el = messageListRef.value
      if (!el) return
      const nearBottom =
        el.scrollHeight - el.scrollTop - el.clientHeight < 100
      if (nearBottom) scrollToBottom()
    })
  }
)

async function loadConversationDetail() {
  const convId = chatStore.currentConversationId
  if (!convId) return
  try {
    const res = await getConversationDetailApi(convId)
    if (res.code === 0) {
      currentConv.value = res.data
    }
  } catch (e) {
    // 静默处理
  }
}

// ── 发送消息 ──────────────
function sendTextMessage() {
  const text = inputText.value.trim()
  if (!text) return
  chatStore.setSending(true)
  sendSocketMessage({
    conversation_id: chatStore.currentConversationId,
    msg_type: 1,
    content: text,
  })
  inputText.value = ''
  chatStore.setSending(false)
}

// ── 文件上传 ──────────────
async function handleFileUpload(file) {
  const formData = new FormData()
  formData.append('file', file)
  try {
    const res = await uploadFileApi(formData)
    if (res.code === 0) {
      sendSocketMessage({
        conversation_id: chatStore.currentConversationId,
        msg_type: 2,
        content: file.name,
        file_id: res.data.file_id,
      })
    }
  } catch (e) {
    // 静默处理
  }
  return false
}

// ── 正在输入 ──────────────
function handleTyping() {
  if (typingTimer) clearTimeout(typingTimer)
  sendTypingEvent(chatStore.currentConversationId)
  typingTimer = setTimeout(() => {}, 2000)
}

// ── 滚动 ──────────────────
function handleScroll(e) {
  if (e.target.scrollTop === 0 && chatStore.hasMore) {
    chatStore.loadMoreMessages()
  }
}

function scrollToBottom() {
  messageBottomRef.value?.scrollIntoView({ behavior: 'instant' })
}
</script>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: var(--color-surface);
}

/* ── 顶部标题栏 ─────────── */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-5);
  border-bottom: 1px solid var(--color-border);
  background-color: var(--color-surface);
}

.chat-header-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.chat-header-text {
  display: flex;
  flex-direction: column;
}

.chat-header-name {
  font-size: var(--text-md);
  font-weight: 600;
  color: var(--color-text);
}

.chat-header-status {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

/* ── 消息列表 ───────────── */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-4) var(--space-5);
  background-color: var(--color-bg);
}

.load-more {
  text-align: center;
  margin-bottom: var(--space-3);
}

.message-wrapper {
  margin-bottom: var(--space-4);
}

.message-bottom {
  height: 0;
}

/* ── 输入区域 ───────────── */
.chat-input-area {
  border-top: 1px solid var(--color-border);
  background-color: var(--color-surface);
}

.chat-input-tools {
  padding: var(--space-2) var(--space-4) 0;
}

.chat-input-box {
  display: flex;
  align-items: flex-end;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-4) var(--space-3);
}

.chat-input-box :deep(.el-textarea__inner) {
  font-size: var(--text-base);
  line-height: 1.5;
  border-radius: var(--radius-md);
}
</style>
