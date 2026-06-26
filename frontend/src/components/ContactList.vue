<template>
  <div class="contact-list">
    <!-- 在线好友 -->
    <div v-if="onlineFriends.length > 0" class="friend-group">
      <div class="group-header">
        <span class="group-dot online"></span>
        <span class="group-title">在线 - {{ onlineFriends.length }}人</span>
      </div>
      <div
        v-for="item in onlineFriends"
        :key="item.id"
        class="friend-item"
        @contextmenu.prevent="showContextMenu($event, item)"
      >
        <div class="friend-avatar">
          <el-avatar :size="40">
            {{ getAvatarText(item.friend) }}
          </el-avatar>
          <span class="status-dot online"></span>
        </div>
        <div class="friend-info">
          <span class="friend-name">{{ item.friend?.nickname || item.friend?.username }}</span>
        </div>
        <div class="friend-actions">
          <el-button link type="primary" size="small" @click="$emit('send-message', item)">
            发消息
          </el-button>
        </div>
      </div>
    </div>

    <!-- 离线好友 -->
    <div v-if="offlineFriends.length > 0" class="friend-group">
      <div class="group-header">
        <span class="group-dot offline"></span>
        <span class="group-title">离线 - {{ offlineFriends.length }}人</span>
      </div>
      <div
        v-for="item in offlineFriends"
        :key="item.id"
        class="friend-item offline"
        @contextmenu.prevent="showContextMenu($event, item)"
      >
        <div class="friend-avatar">
          <el-avatar :size="40">
            {{ getAvatarText(item.friend) }}
          </el-avatar>
          <span class="status-dot offline"></span>
        </div>
        <div class="friend-info">
          <span class="friend-name">{{ item.friend?.nickname || item.friend?.username }}</span>
        </div>
        <div class="friend-actions">
          <el-button link type="primary" size="small" @click="$emit('send-message', item)">
            发消息
          </el-button>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-wrap">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- 空状态 -->
    <el-empty
      v-if="!loading && friends.length === 0"
      description="暂无好友，去搜索添加吧"
    />

    <!-- 右键菜单 -->
    <div
      v-if="contextMenu.visible"
      class="context-menu"
      :style="{ top: contextMenu.top + 'px', left: contextMenu.left + 'px' }"
    >
      <div class="menu-item" @click="handleSendMessage">
        <el-icon><ChatDotRound /></el-icon>
        <span>发送消息</span>
      </div>
      <div class="menu-item" @click="handleViewProfile">
        <el-icon><User /></el-icon>
        <span>查看资料</span>
      </div>
      <div class="menu-divider" />
      <div class="menu-item danger" @click="handleDeleteFriend">
        <el-icon><Delete /></el-icon>
        <span>删除好友</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  friends: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['delete-friend', 'send-message'])

// 在线/离线分类
const onlineFriends = computed(() =>
  props.friends.filter(f => f.friend && f.friend.status === 1)
)
const offlineFriends = computed(() =>
  props.friends.filter(f => !f.friend || f.friend.status !== 1)
)

// 右键菜单
const contextMenu = ref({
  visible: false,
  top: 0,
  left: 0,
  target: null,
})

function showContextMenu(event, friendItem) {
  contextMenu.value = {
    visible: true,
    top: event.clientY,
    left: event.clientX,
    target: friendItem,
  }
}

function hideContextMenu() {
  contextMenu.value.visible = false
  contextMenu.value.target = null
}

function handleSendMessage() {
  if (contextMenu.value.target) {
    emit('send-message', contextMenu.value.target)
  }
  hideContextMenu()
}

function handleViewProfile() {
  hideContextMenu()
}

function handleDeleteFriend() {
  if (contextMenu.value.target) {
    emit('delete-friend', contextMenu.value.target)
  }
  hideContextMenu()
}

function onDocumentClick() {
  hideContextMenu()
}

onMounted(() => {
  document.addEventListener('click', onDocumentClick)
})

onUnmounted(() => {
  document.removeEventListener('click', onDocumentClick)
})

function getAvatarText(friend) {
  if (!friend) return 'U'
  return (friend.nickname || friend.username || 'U')[0].toUpperCase()
}
</script>

<style scoped>
.contact-list {
  padding-bottom: var(--space-4);
}

/* ── 分组标题 ───────────────────── */
.friend-group {
  margin-bottom: var(--space-2);
}

.group-header {
  padding: 12px 20px 4px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.group-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.group-dot.online {
  background-color: var(--color-success);
}

.group-dot.offline {
  background-color: var(--color-text-muted);
}

.group-title {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  font-weight: 500;
}

/* ── 好友条目 ───────────────────── */
.friend-item {
  display: flex;
  align-items: center;
  padding: 8px 20px;
  gap: 12px;
  cursor: pointer;
  transition: background-color 200ms ease;
  border-radius: 12px;
  margin: 0 8px 2px;
}

.friend-item:hover {
  background-color: var(--color-surface-hover);
}

.friend-item.offline {
  opacity: 0.55;
}

.friend-item.offline:hover {
  opacity: 1;
}

.friend-avatar {
  flex-shrink: 0;
  position: relative;
}

.friend-avatar :deep(.el-avatar) {
  background-color: var(--color-primary-bg);
  color: var(--color-primary);
  font-weight: 600;
}

.status-dot {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 2px solid var(--color-surface);
}

.status-dot.online {
  background-color: var(--color-success);
}

.status-dot.offline {
  background-color: var(--color-text-muted);
}

/* ── 好友信息 ───────────────────── */
.friend-info {
  flex: 1;
  min-width: 0;
}

.friend-name {
  font-size: var(--text-base);
  font-weight: 500;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.friend-actions {
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 200ms ease;
}

.friend-item:hover .friend-actions {
  opacity: 1;
}

/* ── 加载态 ─────────────────────── */
.loading-wrap {
  padding: 20px;
}

/* ── 右键菜单 ───────────────────── */
.context-menu {
  position: fixed;
  z-index: 9999;
  background: var(--color-surface);
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(15, 23, 42, 0.12);
  padding: 4px 0;
  min-width: 160px;
  border: 1px solid var(--color-border-light);
  animation: menuFadeIn 150ms ease;
}

@keyframes menuFadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  font-size: 13px;
  color: var(--color-text);
  cursor: pointer;
  transition: background-color 150ms ease;
}

.menu-item:hover {
  background-color: var(--color-surface-hover);
}

.menu-item.danger {
  color: var(--color-danger);
}

.menu-item.danger:hover {
  background-color: #FEF2F2;
}

.menu-divider {
  height: 1px;
  background: var(--color-border-light);
  margin: 4px 0;
}
</style>
