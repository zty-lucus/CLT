<template>
  <div class="profile-container">
    <el-card class="profile-card" shadow="always">
      <template #header>
        <div class="card-header">
          <span>个人资料</span>
        </div>
      </template>

      <div class="avatar-section">
        <el-avatar :size="80" :src="editForm.avatar ? `/uploads/${editForm.avatar}` : ''">
          {{ editForm.username?.charAt(0)?.toUpperCase() }}
        </el-avatar>
      </div>

      <el-descriptions :column="1" border label-width="100px">
        <el-descriptions-item label="用户名">{{ userInfo.username }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ userInfo.email || '未设置' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="userInfo.status === 1 ? 'success' : 'info'" size="small">
            {{ userInfo.status === 1 ? '在线' : '离线' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="注册时间">{{ userInfo.created_at }}</el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <el-form ref="formRef" :model="editForm" :rules="rules" label-width="80px">
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="editForm.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="头像" prop="avatar">
          <el-input v-model="editForm.avatar" placeholder="头像文件名" />
        </el-form-item>
        <el-form-item label="签名" prop="signature">
          <el-input v-model="editForm.signature" type="textarea" :rows="2" placeholder="个性签名" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
          <el-button type="danger" plain @click="handleLogout">退出登录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
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
  } catch (e) {
    // error handled by interceptor
  }
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
    // error handled by interceptor
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
.profile-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}
.profile-card {
  width: 520px;
  border-radius: 12px;
}
.card-header {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}
.avatar-section {
  text-align: center;
  margin-bottom: 20px;
}
</style>
