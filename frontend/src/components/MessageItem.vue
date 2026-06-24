<template>
  <div class="message-item" :class="{ 'is-self': isSelf }">
    <!-- 头像 -->
    <el-avatar
      :size="34"
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
          <el-icon :size="18"><Document /></el-icon>
          <span class="file-name">{{ message.content }}</span>
          <el-button
            text
            size="small"
            type="primary"
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
  return `/api/files/${fileId}/download`
}

function downloadFile(fileId) {
  if (fileId) {
    window.open(getFileUrl(fileId), '_blank')
  }
}
</script>

<style scoped>
.message-item {
  display: flex;
  gap: var(--space-2);
  align-items: flex-start;
}

.message-item.is-self {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.message-body {
  max-width: 70%;
}

.message-sender {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin-bottom: 2px;
  margin-left: 2px;
}

.message-system {
  text-align: center;
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  padding: var(--space-1) var(--space-3);
}

.message-bubble {
  padding: 10px 14px;
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  line-height: 1.5;
  word-break: break-word;
  background-color: var(--color-chat-other);
  color: var(--color-text);
  box-shadow: var(--shadow-sm);
}

.message-item.is-self .message-bubble {
  background-color: var(--color-primary);
  color: #fff;
}

.message-file .file-bubble {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.file-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 160px;
}

.message-image-content {
  max-width: 200px;
  max-height: 200px;
  border-radius: var(--radius-md);
  cursor: pointer;
}

.message-meta {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin-top: 2px;
  display: flex;
  gap: var(--space-1);
}

.message-item.is-self .message-meta {
  justify-content: flex-end;
}
</style>
