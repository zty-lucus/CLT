const { app, BrowserWindow, Tray, Menu, nativeImage, dialog, ipcMain } = require('electron')
const path = require('path')
const fs = require('fs')

const isDev = process.env.NODE_ENV === 'development'

let mainWindow = null
let tray = null

// ── 服务器配置管理 ──────────────────────────────────────────
function getConfigPath() {
  return path.join(app.getPath('userData'), 'server-config.json')
}

function getServerUrl() {
  try {
    const raw = fs.readFileSync(getConfigPath(), 'utf-8')
    return JSON.parse(raw).serverUrl || 'http://localhost:5000'
  } catch {
    return 'http://localhost:5000'
  }
}

function saveServerUrl(url) {
  fs.writeFileSync(getConfigPath(), JSON.stringify({ serverUrl: url }, null, 2), 'utf-8')
}

// ── IPC 处理 ────────────────────────────────────────────────
function setupIPC() {
  ipcMain.handle('get-server-url', () => getServerUrl())

  ipcMain.handle('set-server-url', (_event, url) => {
    saveServerUrl(url)
    // 通知所有窗口刷新以使用新地址
    BrowserWindow.getAllWindows().forEach((win) => {
      win.webContents.send('server-url-changed', url)
    })
    return true
  })
}

// ── 创建主窗口 ──────────────────────────────────────────────
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 960,
    height: 680,
    minWidth: 800,
    minHeight: 600,
    title: '校园即时通信',
    icon: path.join(__dirname, '..', 'public', 'logo3.png'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  if (isDev) {
    mainWindow.loadURL('http://localhost:3000')
    mainWindow.webContents.openDevTools({ mode: 'detach' })
  } else {
    mainWindow.loadFile(path.join(__dirname, '..', 'dist', 'index.html'))
  }

  mainWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault()
      mainWindow.hide()
    }
  })
}

// ── 系统托盘 ────────────────────────────────────────────────
function createTray() {
  const iconPath = path.join(__dirname, '..', 'public', 'logo3.png')
  let trayIcon
  try {
    trayIcon = nativeImage.createFromPath(iconPath).resize({ width: 16, height: 16 })
  } catch {
    trayIcon = nativeImage.createEmpty()
  }

  tray = new Tray(trayIcon)
  tray.setToolTip('校园即时通信')

  const contextMenu = Menu.buildFromTemplate([
    { label: '显示主窗口', click: () => mainWindow && mainWindow.show() },
    { type: 'separator' },
    {
      label: '设置服务器地址',
      click: () => {
        // 优先用主进程的 inputBox，不依赖渲染进程
        const win = BrowserWindow.getFocusedWindow() || mainWindow
        dialog
          .showInputBox(win, {
            title: '服务器设置',
            label: '请输入服务器地址：',
            value: getServerUrl(),
          })
          .then(({ inputValue }) => {
            if (inputValue && /^https?:\/\/.+/.test(inputValue)) {
              saveServerUrl(inputValue)
              dialog.showMessageBox(win, {
                type: 'info',
                title: '提示',
                message: '服务器地址已保存，重启后生效',
              })
            }
          })
          .catch(() => {})
      },
    },
    { type: 'separator' },
    {
      label: '退出',
      click: () => {
        app.isQuitting = true
        app.quit()
      },
    },
  ])

  tray.setContextMenu(contextMenu)
  tray.on('double-click', () => mainWindow && mainWindow.show())
}

// ── App 生命周期 ────────────────────────────────────────────
app.whenReady().then(() => {
  setupIPC()
  createWindow()
  createTray()
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow()
  else mainWindow && mainWindow.show()
})

app.on('before-quit', () => {
  app.isQuitting = true
})
