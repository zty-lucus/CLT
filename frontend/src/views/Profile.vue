<template>
  <div class="profile-page">
    <div class="profile-sidebar">
      <div class="sidebar-nav">
        <el-button text @click="$router.push('/home')">
          <el-icon><ArrowLeft /></el-icon>
          返回聊天
        </el-button>
      </div>
      <div class="profile-card">
        <div class="avatar-section">
          <el-avatar :size="80" :src="editForm.avatar ? `/uploads/${editForm.avatar}` : ''">
            {{ editForm.username?.charAt(0)?.toUpperCase() }}
          </el-avatar>
          <h3 class="profile-name">{{ userInfo.nickname || userInfo.username }}</h3>
          <p class="profile-username">@{{ userInfo.username }}</p>
        </div>

        <div class="info-list">
          <div class="info-item">
            <span class="info-label">邮箱</span>
            <span class="info-value">{{ userInfo.email || '未设置' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">状态</span>
            <span class="info-value">
              <span class="status-badge" :class="userInfo.status === 1 ? 'online' : 'offline'">
                {{ userInfo.status === 1 ? '在线' : '离线' }}
              </span>
            </span>
          </div>
          <div class="info-item">
            <span class="info-label">注册时间</span>
            <span class="info-value">{{ userInfo.created_at }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="profile-main">
      <div class="profile-form-wrapper">
        <h2 class="form-title">编辑资料</h2>
        <p class="form-subtitle">更新你的个人信息</p>
        <el-form ref="formRef" :model="editForm" :rules="rules" label-position="top" class="profile-form">
          <el-form-item label="昵称" prop="nickname">
            <el-input v-model="editForm.nickname" placeholder="请输入昵称" />
          </el-form-item>
          <el-form-item label="头像文件名" prop="avatar">
            <el-input v-model="editForm.avatar" placeholder="头像文件名" />
          </el-form-item>
          <el-form-item label="个性签名" prop="signature">
            <el-input v-model="editForm.signature" type="textarea" :rows="3" placeholder="写点什么介绍自己..." />
          </el-form-item>
          <el-form-item>
            <div class="form-actions">
              <el-button type="primary" :loading="saving" @click="handleSave">保存修改</el-button>
              <el-button type="danger" plain @click="handleLogout">退出登录</el-button>
            </div>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'
import request from '../api/request'

const router = useRouter()
const store = useUserStore()
const formRef = ref(null)
const saving = ref(false)

const userInfo = ref({})
const editForm = reactive({
  nickname: '',
  avatar: '',
  signature: '',
})

const rules = {}

const loadProfile = async () => {
  try {
    const res = await store.getProfile()
    userInfo.value = res.data
    editForm.nickname = res.data.nickname || ''
    editForm.avatar = res.data.avatar || ''
    editForm.signature = res.data.signature || ''
  } catch (e) {}
}

const handleSave = async () => {
  saving.value = true
  try {
    const res = await request.put('/users/profile', {
      nickname: editForm.nickname,
      avatar: editForm.avatar,
      signature: editForm.signature,
    })
    userInfo.value = res.data
    ElMessage.success('保存成功')
  } catch (e) {
  } finally {
    saving.value = false
  }
}

const handleLogout = () => {
  store.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

onMounted(loadProfile)
</script>

<style scoped>
.profile-page {
  display: flex;
  min-height: 100vh;
  background: var(--color-bg);
}

/* ── 左侧信息栏 ──────────── */
.profile-sidebar {
  width: 320px;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
}

.sidebar-nav {
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--color-border-light);
}

.profile-card {
  padding: var(--space-8) var(--space-5);
}

.avatar-section {
  text-align: center;
  margin-bottom: var(--space-8);
}

.profile-name {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text);
  margin: var(--space-4) 0 var(--space-1);
}

.profile-username {
  font-size: var(--text-base);
  color: var(--color-text-muted);
  margin: 0;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

.info-value {
  font-size: var(--text-base);
  color: var(--color-text);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: var(--text-sm);
  padding: 2px 10px;
  border-radius: var(--radius-full);
}

.status-badge::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-badge.online {
  color: var(--color-success);
  background: #F0F9F0;
}

.status-badge.online::before {
  background: var(--color-success);
}

.status-badge.offline {
  color: var(--color-text-muted);
  background: var(--color-border-light);
}

.status-badge.offline::before {
  background: var(--color-text-muted);
}

/* ── 右侧表单区 ──────────── */
.profile-main {
  flex: 1;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: var(--space-8);
}

.profile-form-wrapper {
  width: 100%;
  max-width: 480px;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border-light);
}

.form-title {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--color-text);
  margin: 0 0 var(--space-2);
}

.form-subtitle {
  font-size: var(--text-base);
  color: var(--color-text-muted);
  margin: 0 0 var(--space-6);
}

.profile-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: var(--color-text);
}

.form-actions {
  display: flex;
  gap: var(--space-3);
}

/* ── 响应式 ───────────────── */
@media (max-width: 768px) {
  .profile-page {
    flex-direction: column;
  }
  .profile-sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--color-border);
  }
  .profile-card {
    padding: var(--space-5);
  }
  .profile-main {
    padding: var(--space-5);
  }
  .profile-form-wrapper {
    padding: var(--space-5);
  }
}
</style>
