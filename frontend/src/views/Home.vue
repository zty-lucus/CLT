<template>
  <div class="home-container">
    <el-container style="height: 100%">
      <!-- 左侧边栏 -->
      <el-aside width="260px" class="home-aside">
        <div class="aside-header">
          <h3>校园即时通讯</h3>
        </div>
        <!-- 导航菜单 -->
        <el-menu :default-active="activeMenu" router>
          <el-menu-item index="/home">
            <el-icon><ChatDotRound /></el-icon>
            <span>消息</span>
          </el-menu-item>
          <el-menu-item index="/contacts">
            <el-icon><User /></el-icon>
            <span>通讯录</span>
          </el-menu-item>
          <el-menu-item index="/profile">
            <el-icon><Setting /></el-icon>
            <span>我的</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 右侧内容区 -->
      <el-main class="home-main">
        <router-view />
        <!-- 当没有子路由匹配时显示欢迎页 -->
        <div v-if="$route.path === '/home'" class="welcome">
          <h2>欢迎使用校园即时通讯</h2>
          <p>请选择一个会话开始聊天</p>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style scoped>
.home-container {
  height: 100vh;
  background: #f5f5f5;
}
.home-aside {
  background: #fff;
  border-right: 1px solid #e8e8e8;
}
.aside-header {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid #e8e8e8;
}
.aside-header h3 {
  margin: 0;
  color: #409eff;
}
.home-main {
  padding: 0;
  position: relative;
}
.welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
}
.welcome h2 {
  margin-bottom: 12px;
}
</style>
