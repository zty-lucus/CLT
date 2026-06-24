<template>
  <div class="messages-page">
    <div class="welcome-screen">
      <div class="welcome-icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
      </div>
      <h3>欢迎使用校园即时通信</h3>
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
  color: var(--color-text-muted);
}

.welcome-icon {
  width: 88px;
  height: 88px;
  background: var(--color-border-light);
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-5);
  color: var(--color-text-muted);
}

.welcome-screen h3 {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text-secondary);
  margin: 0 0 var(--space-2);
}

.welcome-screen p {
  font-size: var(--text-base);
  margin: 0;
}
</style>
