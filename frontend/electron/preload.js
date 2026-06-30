const { contextBridge, ipcRenderer } = require('electron')

// 同步获取服务器地址（阻塞读取，确保 Vue 启动前 __SERVER_URL__ 已就绪）
let serverUrl = 'http://localhost:5000'
try {
  const fs = require('fs')
  const path = require('path')
  const { app } = require('@electron/remote') || {}
  // 直接读取打包同级的 server-config.json
  const configPath = path.join(__dirname, '..', 'server-config.json')
  const raw = fs.readFileSync(configPath, 'utf-8')
  serverUrl = JSON.parse(raw).serverUrl || 'http://localhost:5000'
} catch {
  // 文件不存在或无法读取，使用默认值
}

// 注入 window.__SERVER_URL__ 供 Vue 配置模块使用
contextBridge.exposeInMainWorld('__SERVER_URL__', serverUrl)

// 暴露 electronAPI 给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
  getServerUrl: () => ipcRenderer.invoke('get-server-url'),
  setServerUrl: (url) => ipcRenderer.invoke('set-server-url', url),
  onServerUrlChanged: (callback) => {
    ipcRenderer.on('server-url-changed', (_event, url) => callback(url))
  },
})
