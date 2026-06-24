<template>
  <div class="messages-page">
    <div class="welcome-screen">
      <div class="welcome-icon">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
      </div>
      <h2>欢迎使用校园即时通信</h2>
      <p>选择一个会话开始聊天，或前往通讯录添加好友</p>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.messages-page {
  height: 100%;
  display: flex;
}

.welcome-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  width: 100%;
  color: var(--text-muted);
}

.welcome-icon {
  width: 100px;
  height: 100px;
  background: var(--bg-card);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  box-shadow: var(--shadow-md);
  color: var(--primary);
}

.welcome-screen h2 {
  font-size: 22px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.welcome-screen p {
  font-size: 14px;
}
</style>
