<template>
  <div class="profile-container">
    <el-card>
      <h3>个人信息</h3>
      <el-form v-if="userStore.userInfo" :model="form" label-width="80px" style="max-width: 500px">
        <el-form-item label="用户名">
          <el-input :model-value="userStore.userInfo.username" disabled />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="form.nickname" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleUpdate">保存修改</el-button>
          <el-button type="danger" @click="handleLogout">退出登录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { userApi } from '@/api/user'

const router = useRouter()
const userStore = useUserStore()

const form = reactive({
  nickname: userStore.userInfo?.nickname || '',
  email: userStore.userInfo?.email || '',
})

async function handleUpdate() {
  try {
    await userApi.updateProfile(form)
    await userStore.fetchUserInfo()
    ElMessage.success('信息更新成功')
  } catch {
    // 错误已在拦截器中处理
  }
}

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.profile-container {
  padding: 24px;
  max-width: 600px;
}
</style>
