<template>
  <div class="message-item" :class="{ 'is-self': isSelf }">
    <!-- 头像 -->
    <el-avatar
      :size="36"
      :src="message.sender_avatar"
      class="message-avatar"
    >
      {{ firstChar }}
    </el-avatar>

    <!-- 消息内容 -->
    <div class="message-body">
      <!-- 发送者昵称（群聊） -->
      <div v-if="!isSelf" class="message-sender">
        {{ message.sender_nickname }}
      </div>

      <!-- 系统消息 -->
      <div v-if="message.msg_type === 4" class="message-system">
        {{ message.content }}
      </div>

      <!-- 文本消息 -->
      <div v-else-if="message.msg_type === 1" class="message-text">
        <div class="message-bubble">
          {{ message.content }}
        </div>
      </div>

      <!-- 文件消息 -->
      <div v-else-if="message.msg_type === 2" class="message-file">
        <div class="message-bubble file-bubble">
          <div class="file-icon">
            <el-icon :size="20"><Document /></el-icon>
          </div>
          <div class="file-info">
            <span class="file-name">{{ message.content }}</span>
            <span class="file-hint">点击下载</span>
          </div>
          <el-button
            text
            size="small"
            type="primary"
            class="file-download-btn"
            @click="downloadFile(message.file_id)"
          >
            下载
          </el-button>
        </div>
      </div>

      <!-- 图片消息 -->
      <div v-else-if="message.msg_type === 3" class="message-image">
        <el-image
          :src="getFileUrl(message.file_id)"
          fit="cover"
          class="message-image-content"
          :preview-src-list="[getFileUrl(message.file_id)]"
        />
      </div>

      <!-- 时间与状态 -->
      <div class="message-meta">
        <span class="message-time">
          {{ formatTime(message.created_at) }}
        </span>
        <span v-if="isSelf" class="message-status">
          {{ message.status === 1 ? '已读' : '已发送' }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  message: {
    type: Object,
    required: true,
  },
  isSelf: {
    type: Boolean,
    default: false,
  },
})

const firstChar = computed(() => {
  return (props.message.sender_nickname || '?').charAt(0).toUpperCase()
})

function formatTime(isoString) {
  if (!isoString) return ''
  const date = new Date(isoString)
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

function getFileUrl(fileId) {
  const token = localStorage.getItem('token') || ''
  return `http://localhost:5000/api/files/${fileId}/download?inline=1&token=${token}`
}

function downloadFile(fileId) {
  if (fileId) {
    const token = localStorage.getItem('token') || ''
    const url = `http://localhost:5000/api/files/${fileId}/download?token=${token}`
    window.open(url, '_blank')
  }
}
</script>

<style scoped>
/* ── 消息行 ─────────────────────── */
.message-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.message-item.is-self {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
  background-color: var(--color-primary-bg);
  color: var(--color-primary);
  font-weight: 600;
}

.message-body {
  max-width: 70%;
  min-width: 0;
}

/* ── 发送者昵称（群聊） ─────────── */
.message-sender {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin-bottom: 3px;
  margin-left: 2px;
}

/* ── 系统消息 ───────────────────── */
.message-system {
  text-align: center;
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  padding: var(--space-1) var(--space-3);
  background: transparent;
}

/* ── 消息气泡 ───────────────────── */
.message-bubble {
  padding: 10px 14px;
  border-radius: 18px;
  font-size: var(--text-base);
  line-height: 1.55;
  word-break: break-word;
  background-color: var(--color-chat-other);
  color: var(--color-text);
  box-shadow: 0 1px 2px rgba(31, 41, 55, 0.04);
  transition: background-color 200ms ease;
}

.message-item.is-self .message-bubble {
  background-color: var(--color-primary);
  color: #fff;
}

/* ── 文件消息 ───────────────────── */
.message-file .file-bubble {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  min-width: 200px;
}

.file-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background-color: var(--color-primary-bg);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message-item.is-self .file-icon {
  background-color: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.file-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.file-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 160px;
  font-size: var(--text-base);
  font-weight: 500;
}

.file-hint {
  font-size: var(--text-xs);
  opacity: 0.6;
}

.file-download-btn {
  flex-shrink: 0;
  font-size: var(--text-sm);
  padding: 0;
}

/* ── 图片消息 ───────────────────── */
.message-image-content {
  max-width: 220px;
  max-height: 220px;
  border-radius: 12px;
  cursor: pointer;
  transition: opacity 200ms ease;
}

.message-image-content:hover {
  opacity: 0.9;
}

/* ── 时间与状态 ─────────────────── */
.message-meta {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin-top: 3px;
  display: flex;
  gap: var(--space-1);
  align-items: center;
}

.message-item.is-self .message-meta {
  justify-content: flex-end;
}

.message-status {
  font-size: var(--text-xs);
  opacity: 0.7;
}
</style>
