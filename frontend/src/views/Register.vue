<template>
  <div class="register-page">
    <!-- 左侧品牌区 -->
    <div class="register-left">
      <div class="brand-bg-orb brand-bg-orb--1"></div>
      <div class="brand-bg-orb brand-bg-orb--2"></div>
      <div class="brand-bg-orb brand-bg-orb--3"></div>
      <div class="brand-content">
        <img src="/logo3.png" alt="logo" class="brand-logo" />
        <h1 class="brand-title">加入校园即时通信</h1>
        <p class="brand-subtitle">创建账号，开始与同学和老师交流<br/>支持文字、文件、图片多种消息形式</p>
      </div>
    </div>
    <!-- 右侧表单区 -->
    <div class="register-right">
      <div class="register-form-wrapper">
        <div class="form-header">
          <h2 class="form-title">创建账号</h2>
          <p class="form-subtitle">填写以下信息完成注册</p>
        </div>
        <el-form ref="formRef" :model="form" :rules="rules" @keyup.enter="handleRegister" class="register-form">
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="请输入用户名" prefix-icon="User" size="large" />
          </el-form-item>
          <el-form-item prop="email">
            <el-input v-model="form.email" placeholder="请输入邮箱" prefix-icon="Message" size="large" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="form.password" placeholder="请输入密码" prefix-icon="Lock" size="large" show-password />
          </el-form-item>
          <el-form-item prop="confirmPassword">
            <el-input v-model="form.confirmPassword" placeholder="请确认密码" prefix-icon="Lock" size="large" show-password />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" size="large" :loading="loading" class="register-btn" @click="handleRegister">
              注册
            </el-button>
          </el-form-item>
        </el-form>
        <div class="form-footer">
          已有账号？<router-link to="/login">返回登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '../api/request'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为3-20位', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' },
  ],
}

const handleRegister = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await request.post('/auth/register', {
      username: form.username,
      email: form.email,
      password: form.password,
    })
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (e) {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  display: flex;
  min-height: 100vh;
}

/* ── 左侧品牌区 ──────────────── */
.register-left {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #4F6EF7 0%, #6C5CE7 50%, #4F6EF7 100%);
  background-size: 200% 200%;
  animation: gradientShift 8s ease infinite;
  color: #fff;
  padding: 32px;
  position: relative;
  overflow: hidden;
}

@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.brand-bg-orb {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
}

.brand-bg-orb--1 {
  width: 400px;
  height: 400px;
  top: -15%;
  right: -10%;
  background: rgba(255, 255, 255, 0.06);
}

.brand-bg-orb--2 {
  width: 300px;
  height: 300px;
  bottom: -10%;
  left: -8%;
  background: rgba(255, 255, 255, 0.04);
}

.brand-bg-orb--3 {
  width: 180px;
  height: 180px;
  top: 50%;
  left: 60%;
  background: rgba(255, 255, 255, 0.03);
}

.brand-content {
  position: relative;
  z-index: 1;
  text-align: center;
  max-width: 360px;
}

.brand-logo {
  display: block;
  width: 140px;
  height: 140px;
  object-fit: contain;
  margin: 0 auto 28px;
}

.brand-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 12px;
  letter-spacing: 0.02em;
}

.brand-subtitle {
  font-size: 15px;
  line-height: 1.8;
  opacity: 0.8;
  margin: 0;
}

/* ── 右侧表单区 ──────────────── */
.register-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
  background: var(--color-bg);
}

.register-form-wrapper {
  width: 100%;
  max-width: 400px;
  background: var(--color-surface);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.form-header {
  margin-bottom: 28px;
}

.form-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text);
  margin: 0 0 8px;
}

.form-subtitle {
  font-size: 14px;
  color: var(--color-text-muted);
  margin: 0;
}

.register-form {
  margin-bottom: 24px;
}

.register-form :deep(.el-form-item) {
  margin-bottom: 20px;
}

.register-btn {
  width: 100%;
  height: 48px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 12px;
  letter-spacing: 0.02em;
  margin-top: 4px;
}

.form-footer {
  text-align: center;
  color: var(--color-text-muted);
  font-size: 14px;
}

.form-footer a {
  font-weight: 500;
  color: var(--color-primary);
}

.form-footer a:hover {
  color: var(--color-primary-dark);
}

/* ── 响应式 ─────────────────── */
@media (max-width: 900px) {
  .register-page {
    flex-direction: column;
  }
  .register-left {
    padding: 40px 24px;
    min-height: auto;
  }
  .brand-logo {
    width: 100px;
    height: 100px;
    margin-bottom: 20px;
  }
  .brand-title {
    font-size: 22px;
  }
  .brand-subtitle {
    font-size: 13px;
  }
  .register-right {
    padding: 24px;
  }
  .register-form-wrapper {
    padding: 28px;
  }
}
</style>
