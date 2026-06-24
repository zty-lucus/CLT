<template>
  <el-dialog
    v-model="visible"
    title="群组管理"
    width="500px"
    destroy-on-close
    @close="handleClose"
  >
    <div v-if="detail" class="group-manage">
      <!-- 群信息 -->
      <div class="group-manage-section">
        <div class="section-title">群组信息</div>
        <div class="group-info-row">
          <span class="label">群名称</span>
          <span class="value">{{ detail.name }}</span>
        </div>
        <div class="group-info-row">
          <span class="label">群主</span>
          <span class="value">
            {{ getCreatorName() }}
          </span>
        </div>
        <div class="group-info-row">
          <span class="label">成员数</span>
          <span class="value">
            {{ detail.members?.length || 0 }}
          </span>
        </div>
        <div class="group-info-row">
          <span class="label">创建时间</span>
          <span class="value">
            {{ formatDate(detail.created_at) }}
          </span>
        </div>
      </div>

      <!-- 成员列表 -->
      <div class="group-manage-section">
        <div class="section-title">
          群成员 ({{ detail.members?.length || 0 }})
        </div>
        <div
          v-for="member in detail.members"
          :key="member.user_id"
          class="member-item"
        >
          <el-avatar :size="32" :src="member.avatar">
            {{ (member.nickname || '?').charAt(0) }}
          </el-avatar>
          <div class="member-info">
            <span class="member-name">{{ member.nickname }}</span>
            <el-tag
              v-if="member.role === 2"
              size="small"
              type="danger"
            >
              群主
            </el-tag>
            <el-tag
              v-else-if="member.role === 1"
              size="small"
              type="warning"
            >
              管理员
            </el-tag>
          </div>
          <el-button
            v-if="canRemove(member)"
            type="danger"
            text
            size="small"
            @click="handleKick(member.user_id)"
          >
            移出
          </el-button>
        </div>
      </div>

      <!-- 底部操作 -->
      <div class="group-manage-actions">
        <el-button
          v-if="isAdmin"
          type="danger"
          plain
          @click="handleDismiss"
        >
          解散群组
        </el-button>
        <el-button @click="handleLeave">
          退出群组
        </el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

import { useUserStore } from '@/stores/user'
import { useChatStore } from '@/stores/chat'
import {
  removeMemberApi,
  leaveGroupApi,
  dismissGroupApi,
} from '@/api/group'

const props = defineProps({
  modelValue: Boolean,
  conversationId: [Number, String],
  detail: Object,
})

const emit = defineEmits(['update:modelValue'])

const userStore = useUserStore()
const chatStore = useChatStore()
const router = useRouter()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const myRole = computed(() => {
  const me = props.detail?.members?.find(
    (m) => m.user_id === userStore.userInfo?.id
  )
  return me?.role ?? 0
})

const isAdmin = computed(() => myRole.value >= 1)
const isOwner = computed(() => myRole.value === 2)

function getCreatorName() {
  const creator = props.detail?.members?.find(
    (m) => m.user_id === props.detail?.creator_id
  )
  return creator?.nickname || ''
}

function canRemove(member) {
  return isAdmin.value && member.user_id !== userStore.userInfo?.id && member.role < myRole.value
}

function formatDate(isoString) {
  if (!isoString) return ''
  const d = new Date(isoString)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

// ── 操作 ──────────────────
async function handleKick(userId) {
  try {
    await ElMessageBox.confirm('确定要移除该成员吗？', '确认')
    const res = await removeMemberApi(props.conversationId, userId)
    if (res.code === 0) {
      ElMessage.success('成员已移除')
      visible.value = false
    } else {
      ElMessage.error(res.message)
    }
  } catch (e) {
    // 取消操作
  }
}

async function handleLeave() {
  if (isOwner.value) {
    ElMessage.warning('群主不可退出群组，请先转让群主或解散群组')
    return
  }
  try {
    await ElMessageBox.confirm('确定要退出该群组吗？', '确认')
    const res = await leaveGroupApi(props.conversationId)
    if (res.code === 0) {
      ElMessage.success('已退出群组')
      chatStore.setCurrentConversation(null)
      visible.value = false
    } else {
      ElMessage.error(res.message)
    }
  } catch (e) {
    // 取消操作
  }
}

async function handleDismiss() {
  try {
    await ElMessageBox.confirm(
      '确定要解散该群组吗？此操作不可撤销！',
      '确认解散',
      { confirmButtonClass: 'el-button--danger' }
    )
    const res = await dismissGroupApi(props.conversationId)
    if (res.code === 0) {
      ElMessage.success('群组已解散')
      chatStore.setCurrentConversation(null)
      visible.value = false
    } else {
      ElMessage.error(res.message)
    }
  } catch (e) {
    // 取消操作
  }
}

function handleClose() {
  visible.value = false
}
</script>

<style scoped>
.group-manage {
  max-height: 60vh;
}

.group-manage-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 13px;
  color: #999;
  margin-bottom: 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid #f0f0f0;
}

.group-info-row {
  display: flex;
  margin-bottom: 6px;
}

.group-info-row .label {
  width: 70px;
  color: #999;
  font-size: 13px;
}

.group-info-row .value {
  font-size: 13px;
}

.member-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid #f8f8f8;
}

.member-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 6px;
}

.member-name {
  font-size: 13px;
}

.group-manage-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}
</style>
