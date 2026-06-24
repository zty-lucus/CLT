<template>
  <div class="login-page">
    <div class="login-left">
      <div class="brand-content">
        <div class="brand-icon">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        </div>
        <h1 class="brand-title">校园即时通信</h1>
        <p class="brand-subtitle">与同学、老师随时保持联系<br/>分享文件、组建群聊，一切尽在掌握</p>
        <div class="brand-dots">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>
    <div class="login-right">
      <div class="login-form-wrapper">
        <h2 class="form-title">欢迎回来</h2>
        <p class="form-subtitle">登录你的账号继续使用</p>
        <el-form ref="formRef" :model="form" :rules="rules" @keyup.enter="handleLogin" class="login-form">
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" size="large" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="form.password" placeholder="密码" prefix-icon="Lock" size="large" show-password />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" size="large" :loading="loading" class="login-btn" @click="handleLogin">
              登录
            </el-button>
          </el-form-item>
        </el-form>
        <div class="form-footer">
          没有账号？<router-link to="/register">立即注册</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const router = useRouter()
const store = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({ username: '', password: '' })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const handleLogin = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await store.login(form.username, form.password)
    ElMessage.success('登录成功')
    router.push('/profile')
  } catch (e) {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  min-height: 100vh;
}

/* ── 左侧品牌区 ──────────── */
.login-left {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-primary);
  color: #fff;
  padding: var(--space-8);
  position: relative;
  overflow: hidden;
}

.login-left::before {
  content: '';
  position: absolute;
  top: -30%;
  right: -20%;
  width: 500px;
  height: 500px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.04);
}

.login-left::after {
  content: '';
  position: absolute;
  bottom: -20%;
  left: -10%;
  width: 350px;
  height: 350px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.03);
}

.brand-content {
  position: relative;
  z-index: 1;
  text-align: center;
}

.brand-icon {
  width: 72px;
  height: 72px;
  border-radius: var(--radius-xl);
  background: rgba(255, 255, 255, 0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto var(--space-6);
}

.brand-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 var(--space-4);
  letter-spacing: 0.02em;
}

.brand-subtitle {
  font-size: var(--text-base);
  line-height: 1.8;
  opacity: 0.75;
  margin: 0;
}

.brand-dots {
  display: flex;
  gap: 8px;
  justify-content: center;
  margin-top: var(--space-8);
}

.brand-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
}

.brand-dots span:first-child {
  background: rgba(255, 255, 255, 0.8);
}

/* ── 右侧表单区 ──────────── */
.login-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-8);
  background: var(--color-surface);
}

.login-form-wrapper {
  width: 100%;
  max-width: 380px;
}

.form-title {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text);
  margin: 0 0 var(--space-2);
}

.form-subtitle {
  font-size: var(--text-base);
  color: var(--color-text-muted);
  margin: 0 0 var(--space-8);
}

.login-form {
  margin-bottom: var(--space-6);
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: var(--text-base);
  border-radius: var(--radius-md);
}

.form-footer {
  text-align: center;
  color: var(--color-text-muted);
  font-size: var(--text-base);
}

.form-footer a {
  font-weight: 500;
}

/* ── 响应式 ───────────────── */
@media (max-width: 768px) {
  .login-page {
    flex-direction: column;
  }
  .login-left {
    padding: var(--space-8) var(--space-6);
    min-height: auto;
  }
  .brand-title {
    font-size: var(--text-xl);
  }
  .brand-subtitle {
    font-size: var(--text-sm);
  }
  .login-right {
    padding: var(--space-6);
  }
}
</style>
