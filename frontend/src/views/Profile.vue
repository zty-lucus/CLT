<template>
  <div class="profile-page">
    <!-- 背景光晕 -->
    <div class="bg-orb bg-orb--1"></div>
    <div class="bg-orb bg-orb--2"></div>
    <div class="bg-orb bg-orb--3"></div>

    <!-- 顶部导航栏 -->
    <header class="profile-topbar">
      <div class="topbar-left">
        <el-button text class="topbar-back" @click="$router.push('/home')">
          <el-icon :size="18"><ArrowLeft /></el-icon>
          <span>返回</span>
        </el-button>
      </div>
      <div class="topbar-center">
        <span class="topbar-title">个人资料</span>
      </div>
      <div class="topbar-right">
        <el-dropdown trigger="click" @command="handleTopCommand">
          <el-avatar
            :size="32"
            :src="avatarDisplaySrc"
            class="topbar-avatar"
          >
            {{ userInfo.nickname?.charAt(0) || userInfo.username?.charAt(0) || 'U' }}
          </el-avatar>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="profile-content">
      <div class="profile-layout">
        <!-- 左侧：信息展示卡 -->
        <section class="profile-info-card">
          <!-- 渐变 Banner -->
          <div class="info-banner">
            <div class="banner-pattern"></div>
          </div>

          <!-- 头像悬浮区 -->
          <div class="info-avatar-zone">
            <div class="info-avatar-wrapper">
              <el-avatar
                :size="88"
                :src="avatarDisplaySrc"
                class="info-avatar"
              >
                {{ userInfo.nickname?.charAt(0) || userInfo.username?.charAt(0) || 'U' }}
              </el-avatar>
              <span
                class="avatar-status-dot"
                :class="userInfo.status === 1 ? 'online' : 'offline'"
              ></span>
            </div>
            <h2 class="info-nickname">{{ userInfo.nickname || '未设置昵称' }}</h2>
            <p class="info-username">@{{ userInfo.username }}</p>
          </div>

          <!-- 图标化信息项 -->
          <div class="info-card-body">
            <div class="info-row">
              <div class="info-icon-wrap">
                <el-icon :size="15"><Message /></el-icon>
              </div>
              <div class="info-row-content">
                <span class="info-row-label">邮箱</span>
                <span class="info-row-value">{{ userInfo.email || '未设置' }}</span>
              </div>
            </div>

            <div class="info-row">
              <div class="info-icon-wrap">
                <el-icon :size="15"><CircleCheck /></el-icon>
              </div>
              <div class="info-row-content">
                <span class="info-row-label">状态</span>
                <span class="info-row-value">
                  <span class="status-pill" :class="userInfo.status === 1 ? 'online' : 'offline'">
                    {{ userInfo.status === 1 ? '在线' : '离线' }}
                  </span>
                </span>
              </div>
            </div>

            <div class="info-row">
              <div class="info-icon-wrap">
                <el-icon :size="15"><EditPen /></el-icon>
              </div>
              <div class="info-row-content">
                <span class="info-row-label">个性签名</span>
                <span class="info-row-value signature">{{ userInfo.signature || '这个人很懒，什么都没写' }}</span>
              </div>
            </div>

            <div class="info-row">
              <div class="info-icon-wrap">
                <el-icon :size="15"><Calendar /></el-icon>
              </div>
              <div class="info-row-content">
                <span class="info-row-label">加入时间</span>
                <span class="info-row-value">{{ formatDate(userInfo.created_at) }}</span>
              </div>
            </div>
          </div>

          <!-- 退出登录 -->
          <div class="info-card-footer">
            <el-button text class="logout-btn" @click="handleLogout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-button>
          </div>
        </section>

        <!-- 右侧：编辑表单卡 -->
        <section class="profile-edit-card">
          <div class="edit-card-header">
            <h3 class="edit-card-title">编辑资料</h3>
            <p class="edit-card-desc">更新你的个人信息</p>
          </div>

          <!-- 头像上传区 -->
          <div class="edit-avatar-section">
            <el-upload
              class="avatar-uploader"
              :show-file-list="false"
              :before-upload="handleAvatarBefore"
              accept="image/jpeg,image/png,image/webp"
            >
              <div class="avatar-upload-trigger">
                <el-avatar
                  :size="64"
                  :src="avatarPreviewSrc"
                  class="edit-avatar"
                >
                  {{ editForm.nickname?.charAt(0) || userInfo.username?.charAt(0) || 'U' }}
                </el-avatar>
                <div class="avatar-overlay">
                  <el-icon :size="18"><Camera /></el-icon>
                </div>
              </div>
            </el-upload>
            <div class="avatar-upload-info">
              <span class="avatar-upload-label">更换头像</span>
              <span class="avatar-upload-hint">支持 JPG / PNG / WebP，不超过 2MB</span>
            </div>
          </div>

          <!-- 编辑表单 -->
          <el-form
            ref="formRef"
            :model="editForm"
            :rules="rules"
            label-position="top"
            class="edit-form"
          >
            <el-form-item label="昵称" prop="nickname">
              <el-input
                v-model="editForm.nickname"
                placeholder="输入你的昵称"
                maxlength="20"
                show-word-limit
              />
            </el-form-item>

            <el-form-item label="个性签名" prop="signature">
              <el-input
                v-model="editForm.signature"
                type="textarea"
                :rows="3"
                placeholder="写点什么介绍自己..."
                maxlength="100"
                show-word-limit
              />
            </el-form-item>

            <div class="edit-actions">
              <el-button class="btn-cancel" @click="handleCancel">取消</el-button>
              <el-button class="btn-save" :loading="saving" @click="handleSave">
                保存修改
              </el-button>
            </div>
          </el-form>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, SwitchButton, Camera, Message, CircleCheck, EditPen, Calendar } from '@element-plus/icons-vue'
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

// 本地头像预览（新选择的图片）
const avatarLocalPreview = ref('')

// 头像显示源：优先本地预览，其次后端路径
const avatarDisplaySrc = computed(() => {
  if (avatarLocalPreview.value) return avatarLocalPreview.value
  const av = userInfo.value.avatar
  if (av && av !== 'default.png') return `/uploads/${av}`
  return ''
})

const avatarPreviewSrc = computed(() => {
  if (avatarLocalPreview.value) return avatarLocalPreview.value
  const av = editForm.avatar
  if (av && av !== 'default.png') return `/uploads/${av}`
  return ''
})

const rules = {
  nickname: [
    { max: 20, message: '昵称不超过 20 个字符', trigger: 'blur' },
  ],
}

const loadProfile = async () => {
  try {
    const res = await store.getProfile()
    userInfo.value = res.data
    editForm.nickname = res.data.nickname || ''
    editForm.avatar = res.data.avatar || ''
    editForm.signature = res.data.signature || ''
  } catch (e) {}
}

// ── 头像上传 ──────────────────────
function handleAvatarBefore(file) {
  const isImage = ['image/jpeg', 'image/png', 'image/webp'].includes(file.type)
  if (!isImage) {
    ElMessage.warning('仅支持 JPG / PNG / WebP 格式')
    return false
  }
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isLt2M) {
    ElMessage.warning('头像大小不能超过 2MB')
    return false
  }
  // 本地预览
  avatarLocalPreview.value = URL.createObjectURL(file)
  // 保存文件名到表单（接口仍然接收字符串）
  // TODO: 后续如有文件上传接口，替换此处为真正的上传逻辑
  editForm.avatar = file.name
  return false // 阻止 Element Plus 自动上传
}

// ── 保存 ──────────────────────────
async function handleSave() {
  saving.value = true
  try {
    const res = await request.put('/users/profile', {
      nickname: editForm.nickname,
      avatar: editForm.avatar,
      signature: editForm.signature,
    })
    userInfo.value = res.data
    avatarLocalPreview.value = ''
    ElMessage.success('保存成功')
  } catch (e) {
  } finally {
    saving.value = false
  }
}

// ── 取消 ──────────────────────────
function handleCancel() {
  editForm.nickname = userInfo.value.nickname || ''
  editForm.avatar = userInfo.value.avatar || ''
  editForm.signature = userInfo.value.signature || ''
  avatarLocalPreview.value = ''
}

// ── 退出登录 ──────────────────────
function handleLogout() {
  store.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

function handleTopCommand(cmd) {
  if (cmd === 'logout') handleLogout()
}

// ── 日期格式化 ────────────────────
function formatDate(isoString) {
  if (!isoString) return ''
  const d = new Date(isoString)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

onMounted(loadProfile)
</script>

<style scoped>
/* ═══════════════════════════════════════
   Feishu + Apple + Linear Design System
   ═══════════════════════════════════════ */
.profile-page {
  min-height: 100vh;
  background: linear-gradient(160deg, #F0F4FF 0%, #E8F0FE 30%, #F5F0FF 60%, #EDF6FF 100%);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow-x: hidden;
}

/* ── 背景光晕 ───────────────────────── */
.bg-orb {
  position: fixed;
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
  filter: blur(80px);
}

.bg-orb--1 {
  width: 500px;
  height: 500px;
  top: -120px;
  right: -80px;
  background: rgba(91, 124, 250, 0.10);
}

.bg-orb--2 {
  width: 400px;
  height: 400px;
  bottom: -100px;
  left: -60px;
  background: rgba(84, 198, 235, 0.08);
}

.bg-orb--3 {
  width: 300px;
  height: 300px;
  top: 40%;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(139, 92, 246, 0.06);
}

/* ═══════════════════════════════════════
   顶部导航栏 - Glass
   ═══════════════════════════════════════ */
.profile-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 24px;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.5);
  flex-shrink: 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.topbar-left,
.topbar-right {
  width: 120px;
  display: flex;
}

.topbar-right {
  justify-content: flex-end;
}

.topbar-center {
  flex: 1;
  text-align: center;
}

.topbar-title {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a2e;
}

.topbar-back {
  font-size: 13px;
  color: #8890a0;
  gap: 4px;
  transition: color 200ms ease;
}

.topbar-back:hover {
  color: #5B7CFA;
}

.topbar-avatar {
  cursor: pointer;
  background: linear-gradient(135deg, #5B7CFA 0%, #54C6EB 100%);
  color: #fff;
  font-weight: 600;
  font-size: 13px;
  transition: transform 200ms ease, box-shadow 200ms ease;
}

.topbar-avatar:hover {
  transform: scale(1.06);
  box-shadow: 0 2px 12px rgba(91, 124, 250, 0.3);
}

/* ═══════════════════════════════════════
   主内容区
   ═══════════════════════════════════════ */
.profile-content {
  flex: 1;
  padding: 40px 24px 80px;
  display: flex;
  justify-content: center;
  position: relative;
  z-index: 1;
}

.profile-layout {
  display: flex;
  gap: 24px;
  width: 100%;
  max-width: 860px;
  align-items: flex-start;
}

/* ═══════════════════════════════════════
   左侧：信息展示卡 - Glass Card
   ═══════════════════════════════════════ */
.profile-info-card {
  width: 320px;
  min-width: 320px;
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(24px) saturate(160%);
  -webkit-backdrop-filter: blur(24px) saturate(160%);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow:
    0 1px 2px rgba(91, 124, 250, 0.04),
    0 4px 16px rgba(91, 124, 250, 0.06);
  overflow: hidden;
  transition: box-shadow 300ms ease, transform 300ms ease;
}

.profile-info-card:hover {
  box-shadow:
    0 2px 4px rgba(91, 124, 250, 0.06),
    0 8px 24px rgba(91, 124, 250, 0.10);
  transform: translateY(-2px);
}

/* ── 渐变 Banner ─────────────────────── */
.info-banner {
  height: 100px;
  background: linear-gradient(135deg, #5B7CFA 0%, #7B6CF6 40%, #54C6EB 100%);
  position: relative;
  overflow: hidden;
}

.banner-pattern {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 20% 50%, rgba(255,255,255,0.15) 0%, transparent 50%),
    radial-gradient(circle at 80% 30%, rgba(255,255,255,0.10) 0%, transparent 40%);
}

/* ── 头像悬浮区 ─────────────────────── */
.info-avatar-zone {
  text-align: center;
  padding: 0 24px 20px;
  margin-top: -44px;
}

.info-avatar-wrapper {
  position: relative;
  display: inline-block;
}

.info-avatar {
  background: linear-gradient(135deg, #5B7CFA 0%, #54C6EB 100%);
  color: #fff;
  font-weight: 700;
  font-size: 28px;
  border: 4px solid rgba(255, 255, 255, 0.9);
  box-shadow:
    0 4px 12px rgba(91, 124, 250, 0.2),
    0 0 0 3px rgba(91, 124, 250, 0.08);
  transition: transform 300ms ease;
}

.info-avatar:hover {
  transform: scale(1.04);
}

.avatar-status-dot {
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 3px solid #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.avatar-status-dot.online {
  background: #34C759;
}

.avatar-status-dot.offline {
  background: #9DA3B0;
}

.info-nickname {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 14px 0 4px;
  letter-spacing: -0.01em;
}

.info-username {
  font-size: 13px;
  color: #8890a0;
  margin: 0;
}

/* ── 图标化信息项 ───────────────────── */
.info-card-body {
  padding: 4px 20px 20px;
}

.info-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 8px;
  border-radius: 10px;
  transition: background-color 200ms ease;
}

.info-row:hover {
  background: rgba(91, 124, 250, 0.04);
}

.info-icon-wrap {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(91,124,250,0.08) 0%, rgba(84,198,235,0.08) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #5B7CFA;
  margin-top: 1px;
}

.info-row-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.info-row-label {
  font-size: 11px;
  color: #8890a0;
  font-weight: 500;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.info-row-value {
  font-size: 13px;
  color: #1a1a2e;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.info-row-value.signature {
  white-space: normal;
  line-height: 1.5;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 100px;
  font-weight: 500;
}

.status-pill::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-pill.online {
  color: #16a34a;
  background: rgba(22, 163, 74, 0.08);
}

.status-pill.online::before {
  background: #34C759;
}

.status-pill.offline {
  color: #8890a0;
  background: rgba(157, 163, 176, 0.1);
}

.status-pill.offline::before {
  background: #9DA3B0;
}

/* ── 退出登录 ───────────────────────── */
.info-card-footer {
  padding: 12px 20px 16px;
  border-top: 1px solid rgba(91, 124, 250, 0.06);
}

.logout-btn {
  width: 100%;
  justify-content: center;
  font-size: 13px;
  color: #8890a0;
  gap: 6px;
  transition: all 200ms ease;
  border-radius: 10px;
  padding: 8px 0;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.06);
  color: #ef4444;
}

/* ═══════════════════════════════════════
   右侧：编辑表单卡 - Glass Card
   ═══════════════════════════════════════ */
.profile-edit-card {
  flex: 1;
  min-width: 0;
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(24px) saturate(160%);
  -webkit-backdrop-filter: blur(24px) saturate(160%);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow:
    0 1px 2px rgba(91, 124, 250, 0.04),
    0 4px 16px rgba(91, 124, 250, 0.06);
  padding: 32px;
  transition: box-shadow 300ms ease, transform 300ms ease;
}

.profile-edit-card:hover {
  box-shadow:
    0 2px 4px rgba(91, 124, 250, 0.06),
    0 8px 24px rgba(91, 124, 250, 0.10);
  transform: translateY(-2px);
}

.edit-card-header {
  margin-bottom: 28px;
}

.edit-card-title {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 4px;
  letter-spacing: -0.01em;
}

.edit-card-desc {
  font-size: 13px;
  color: #8890a0;
  margin: 0;
}

/* ── 头像上传区 ─────────────────────── */
.edit-avatar-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 28px;
  padding: 16px;
  background: linear-gradient(135deg, rgba(91,124,250,0.03) 0%, rgba(84,198,235,0.03) 100%);
  border-radius: 12px;
  border: 1px dashed rgba(91, 124, 250, 0.15);
}

.avatar-uploader {
  flex-shrink: 0;
}

.avatar-uploader :deep(.el-upload) {
  cursor: pointer;
  display: block;
}

.avatar-upload-trigger {
  position: relative;
  display: inline-block;
  border-radius: 50%;
  overflow: hidden;
}

.edit-avatar {
  background: linear-gradient(135deg, #5B7CFA 0%, #54C6EB 100%);
  color: #fff;
  font-weight: 700;
  font-size: 22px;
  transition: filter 200ms ease;
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.4);
  color: #fff;
  opacity: 0;
  transition: opacity 200ms ease;
  border-radius: 50%;
  backdrop-filter: blur(2px);
}

.avatar-upload-trigger:hover .avatar-overlay {
  opacity: 1;
}

.avatar-upload-trigger:hover .edit-avatar {
  filter: brightness(0.85);
}

.avatar-upload-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.avatar-upload-label {
  font-size: 14px;
  font-weight: 500;
  color: #1a1a2e;
}

.avatar-upload-hint {
  font-size: 12px;
  color: #8890a0;
}

/* ── 表单 ───────────────────────────── */
.edit-form {
  margin: 0;
}

.edit-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: #3a3e4a;
  font-size: 13px;
  padding-bottom: 6px;
}

.edit-form :deep(.el-input__wrapper) {
  border-radius: 12px;
  background: rgba(91, 124, 250, 0.025);
  box-shadow: none;
  border: 1px solid rgba(91, 124, 250, 0.10);
  transition: all 250ms ease;
  min-height: 44px;
}

.edit-form :deep(.el-input__wrapper:hover) {
  border-color: rgba(91, 124, 250, 0.25);
  background: rgba(91, 124, 250, 0.04);
}

.edit-form :deep(.el-input__wrapper.is-focus) {
  border-color: #5B7CFA;
  background: rgba(91, 124, 250, 0.04);
  box-shadow: 0 0 0 3px rgba(91, 124, 250, 0.08);
}

.edit-form :deep(.el-textarea__inner) {
  border-radius: 12px;
  background: rgba(91, 124, 250, 0.025);
  box-shadow: none;
  border: 1px solid rgba(91, 124, 250, 0.10);
  transition: all 250ms ease;
  padding: 12px 14px;
  font-size: 14px;
  line-height: 1.6;
}

.edit-form :deep(.el-textarea__inner:hover) {
  border-color: rgba(91, 124, 250, 0.25);
  background: rgba(91, 124, 250, 0.04);
}

.edit-form :deep(.el-textarea__inner:focus) {
  border-color: #5B7CFA;
  background: rgba(91, 124, 250, 0.04);
  box-shadow: 0 0 0 3px rgba(91, 124, 250, 0.08);
}

.edit-form :deep(.el-input__count) {
  font-size: 11px;
  color: #8890a0;
}

/* ── 按钮 ───────────────────────────── */
.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 12px;
}

.edit-actions .btn-cancel {
  height: 44px;
  border-radius: 12px;
  font-weight: 500;
  padding: 0 24px;
  font-size: 14px;
  color: #5a6175;
  border: 1px solid rgba(91, 124, 250, 0.12);
  background: transparent;
  transition: all 200ms ease;
}

.edit-actions .btn-cancel:hover {
  border-color: rgba(91, 124, 250, 0.25);
  background: rgba(91, 124, 250, 0.04);
  color: #3a3e4a;
}

.edit-actions .btn-save {
  height: 44px;
  border-radius: 12px;
  font-weight: 600;
  padding: 0 28px;
  font-size: 14px;
  color: #fff;
  background: linear-gradient(135deg, #5B7CFA 0%, #7B6CF6 50%, #54C6EB 100%);
  background-size: 200% 200%;
  border: none;
  box-shadow: 0 2px 8px rgba(91, 124, 250, 0.25);
  transition: all 250ms ease;
}

.edit-actions .btn-save:hover {
  background-position: 100% 0;
  box-shadow: 0 4px 14px rgba(91, 124, 250, 0.35);
  transform: translateY(-1px);
}

.edit-actions .btn-save:active {
  transform: translateY(0);
  box-shadow: 0 1px 4px rgba(91, 124, 250, 0.2);
}

/* ═══════════════════════════════════════
   响应式
   ═══════════════════════════════════════ */
@media (max-width: 768px) {
  .profile-content {
    padding: 24px 16px 60px;
  }

  .profile-layout {
    flex-direction: column;
    gap: 16px;
  }

  .profile-info-card {
    width: 100%;
    min-width: 100%;
  }

  .profile-edit-card {
    padding: 24px 20px;
  }

  .info-banner {
    height: 80px;
  }

  .info-avatar-zone {
    padding: 0 20px 16px;
    margin-top: -36px;
  }

  .info-avatar {
    width: 72px !important;
    height: 72px !important;
    font-size: 24px !important;
  }

  .info-card-body {
    padding: 4px 16px 16px;
  }

  .topbar-left,
  .topbar-right {
    width: 80px;
  }

  .bg-orb--1 {
    width: 300px;
    height: 300px;
  }

  .bg-orb--2 {
    width: 250px;
    height: 250px;
  }

  .bg-orb--3 {
    display: none;
  }
}
</style>
