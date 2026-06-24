<template>
  <div class="message-item" :class="{ 'is-self': isSelf }">
    <!-- 头像 -->
    <el-avatar
      :size="32"
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
          <el-icon :size="20"><Document /></el-icon>
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
  gap: 10px;
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
  font-size: 12px;
  color: #999;
  margin-bottom: 2px;
  margin-left: 2px;
}

.message-system {
  text-align: center;
  font-size: 12px;
  color: #999;
  padding: 4px 12px;
}

.message-bubble {
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.5;
  word-break: break-word;
  background-color: #fff;
  color: #333;
}

.message-item.is-self .message-bubble {
  background-color: #95ec69;
}

.message-file .file-bubble {
  display: flex;
  align-items: center;
  gap: 8px;
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
  border-radius: 8px;
  cursor: pointer;
}

.message-meta {
  font-size: 11px;
  color: #bbb;
  margin-top: 2px;
  display: flex;
  gap: 6px;
}

.message-item.is-self .message-meta {
  justify-content: flex-end;
}
</style>
