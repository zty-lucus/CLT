<template>
  <div class="contact-list">
    <!-- 在线好友 -->
    <div v-if="onlineFriends.length > 0" class="friend-group">
      <div class="group-header">
        <span class="group-title">在线 - {{ onlineFriends.length }}人</span>
      </div>
      <div
        v-for="item in onlineFriends"
        :key="item.id"
        class="friend-item"
        @contextmenu.prevent="showContextMenu($event, item)"
      >
        <div class="friend-avatar">
          <el-badge
            is-dot
            :type="'success'"
            :offset="[0, 36]"
          >
            <el-avatar :size="42">
              {{ getAvatarText(item.friend) }}
            </el-avatar>
          </el-badge>
        </div>
        <div class="friend-info">
          <span class="friend-name">{{ item.friend?.nickname || item.friend?.username }}</span>
          <span class="friend-status online">在线</span>
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
        <span class="group-title">离线 - {{ offlineFriends.length }}人</span>
      </div>
      <div
        v-for="item in offlineFriends"
        :key="item.id"
        class="friend-item offline"
        @contextmenu.prevent="showContextMenu($event, item)"
      >
        <div class="friend-avatar">
          <el-badge
            is-dot
            :type="'info'"
            :offset="[0, 36]"
          >
            <el-avatar :size="42">
              {{ getAvatarText(item.friend) }}
            </el-avatar>
          </el-badge>
        </div>
        <div class="friend-info">
          <span class="friend-name">{{ item.friend?.nickname || item.friend?.username }}</span>
          <span class="friend-status offline">离线</span>
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
  // TODO: 查看好友资料 - 可由成员A的 Profile.vue 支持
  hideContextMenu()
}

function handleDeleteFriend() {
  if (contextMenu.value.target) {
    emit('delete-friend', contextMenu.value.target)
  }
  hideContextMenu()
}

// 点击页面其他位置关闭右键菜单
function onDocumentClick() {
  hideContextMenu()
}

onMounted(() => {
  document.addEventListener('click', onDocumentClick)
})

onUnmounted(() => {
  document.removeEventListener('click', onDocumentClick)
})

// 头像文字
function getAvatarText(friend) {
  if (!friend) return 'U'
  return (friend.nickname || friend.username || 'U')[0].toUpperCase()
}
</script>

<style scoped>
.contact-list {
  padding-bottom: 16px;
}

/* 分组 */
.friend-group {
  margin-bottom: 8px;
}
.group-header {
  padding: 12px 20px 6px;
}
.group-title {
  font-size: 12px;
  color: #999;
  font-weight: 500;
}

/* 好友条目 */
.friend-item {
  display: flex;
  align-items: center;
  padding: 10px 20px;
  gap: 12px;
  cursor: pointer;
  transition: background 0.15s;
  border-bottom: 1px solid #fafafa;
}
.friend-item:hover {
  background: #f0f5ff;
}
.friend-item.offline {
  opacity: 0.7;
}
.friend-item.offline:hover {
  opacity: 1;
}

.friend-avatar {
  flex-shrink: 0;
}

.friend-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.friend-name {
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.friend-status {
  font-size: 11px;
}
.friend-status.online {
  color: #67c23a;
}
.friend-status.offline {
  color: #c0c4cc;
}

.friend-actions {
  flex-shrink: 0;
}

.loading-wrap {
  padding: 20px;
}

/* 右键菜单 */
.context-menu {
  position: fixed;
  z-index: 9999;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  padding: 4px 0;
  min-width: 160px;
}
.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.15s;
}
.menu-item:hover {
  background: #f0f5ff;
}
.menu-item.danger {
  color: #f56c6c;
}
.menu-item.danger:hover {
  background: #fef0f0;
}
.menu-divider {
  height: 1px;
  background: #f0f0f0;
  margin: 4px 0;
}
</style>
