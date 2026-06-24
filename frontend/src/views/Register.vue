<template>
  <div class="register-page">
    <div class="register-left">
      <div class="brand-content">
        <div class="brand-icon">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        </div>
        <h1 class="brand-title">加入校园即时通信</h1>
        <p class="brand-subtitle">创建账号，开始与同学和老师交流<br/>支持文字、文件、图片多种消息形式</p>
        <div class="brand-dots">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>
    <div class="register-right">
      <div class="register-form-wrapper">
        <h2 class="form-title">创建账号</h2>
        <p class="form-subtitle">填写以下信息完成注册</p>
        <el-form ref="formRef" :model="form" :rules="rules" @keyup.enter="handleRegister" class="register-form">
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" size="large" />
          </el-form-item>
          <el-form-item prop="email">
            <el-input v-model="form.email" placeholder="邮箱" prefix-icon="Message" size="large" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="form.password" placeholder="密码" prefix-icon="Lock" size="large" show-password />
          </el-form-item>
          <el-form-item prop="confirmPassword">
            <el-input v-model="form.confirmPassword" placeholder="确认密码" prefix-icon="Lock" size="large" show-password />
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

/* ── 左侧品牌区 ──────────── */
.register-left {
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

.register-left::before {
  content: '';
  position: absolute;
  top: -30%;
  right: -20%;
  width: 500px;
  height: 500px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.04);
}

.register-left::after {
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
.register-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-8);
  background: var(--color-surface);
}

.register-form-wrapper {
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
  margin: 0 0 var(--space-6);
}

.register-form {
  margin-bottom: var(--space-6);
}

.register-btn {
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
  .register-page {
    flex-direction: column;
  }
  .register-left {
    padding: var(--space-6);
    min-height: auto;
  }
  .brand-title {
    font-size: var(--text-xl);
  }
  .brand-subtitle {
    font-size: var(--text-sm);
  }
  .register-right {
    padding: var(--space-6);
  }
}
</style>
