<template>
  <div class="register-container">
    <el-card class="register-card" shadow="always">
      <h2 class="register-title">校园即时通信系统</h2>
      <el-form ref="formRef" :model="form" :rules="rules" @keyup.enter="handleRegister">
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
          <el-button type="primary" size="large" :loading="loading" style="width:100%" @click="handleRegister">
            注册
          </el-button>
        </el-form-item>
      </el-form>
      <div class="register-footer">
        已有账号？<router-link to="/login">返回登录</router-link>
      </div>
    </el-card>
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
.register-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.register-card {
  width: 420px;
  padding: 20px;
  border-radius: 12px;
}
.register-title {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
  font-size: 24px;
}
.register-footer {
  text-align: center;
  color: #909399;
  font-size: 14px;
}
.register-footer a {
  color: #409eff;
  text-decoration: none;
}
</style>
