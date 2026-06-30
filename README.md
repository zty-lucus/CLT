# 校园即时通信与文件传输系统

面向校园用户的即时通信与文件传输平台，支持单聊、群聊、文件上传下载、好友管理等功能。同时提供 **Web 端（B/S）** 和 **桌面客户端（C/S）** 两种使用方式。

## 架构

```
         ┌──────────────────────────┐
         │     Flask Server (:5000)  │
         │  REST API + WebSocket     │
         │  MySQL 数据库              │
         └──────┬────────┬──────────┘
                │        │
    HTTP/WS ───┘        └─── HTTP/WS
         │                    │
  ┌──────┴──────┐    ┌───────┴────────┐
  │  浏览器 (B/S) │    │ 桌面客户端 (C/S) │
  │  Vue 3 Web   │    │  Electron 壳    │
  │  localhost    │    │  .exe 安装包    │
  └──────────────┘    └────────────────┘
```

## 技术栈

### 后端
- **Python 3.10+** + **Flask 3.x** — Web 框架
- **Flask-SocketIO** — WebSocket 实时通信
- **SQLAlchemy** — ORM 数据库操作
- **Flask-JWT-Extended** — JWT 认证
- **MySQL 8.0** — 关系型数据库

### 前端 / 客户端
- **Vue 3** — 前端框架 (Composition API)
- **Element Plus** — UI 组件库
- **Pinia** — 状态管理
- **Socket.IO Client** — WebSocket 客户端
- **Vite** — 构建工具
- **Electron** — 桌面客户端框架

## 功能特性

- 用户注册 / 登录（JWT 认证）
- 好友搜索、添加、删除、管理
- 单聊 / 群聊实时消息（WebSocket）
- 群组创建、加入、退出、成员管理（角色：群主 / 管理员 / 成员）
- 文件上传 / 下载（支持图片、文档、压缩包等）
- 消息记录持久化与分页加载
- 在线状态实时显示
- 未读消息计数
- 系统消息通知（加群、退群、角色变更等）
- 个人资料编辑

## 项目结构

```
campus-im/
├── backend/                 # 后端项目
│   ├── app/
│   │   ├── models/          # 数据模型
│   │   ├── routes/          # API 路由
│   │   ├── services/        # 业务逻辑
│   │   ├── sockets/         # WebSocket 事件
│   │   ├── utils/           # 工具函数
│   │   └── constants.py     # 常量定义（消息类型、会话类型、角色枚举）
│   ├── tests/               # 后端测试（pytest）
│   ├── uploads/             # 文件上传目录
│   ├── config.py            # 配置管理
│   ├── requirements.txt     # Python 依赖
│   └── run.py               # 启动入口
├── frontend/                # 前端 + 桌面客户端
│   ├── electron/
│   │   ├── main.js          # Electron 主进程（窗口管理、系统托盘）
│   │   └── preload.js       # 预加载脚本（IPC 桥接）
│   ├── src/
│   │   ├── api/             # API 请求封装
│   │   ├── components/      # 公共组件
│   │   ├── constants/       # 常量定义
│   │   ├── router/          # 路由配置
│   │   ├── socket/          # WebSocket 客户端
│   │   ├── stores/          # 状态管理（Pinia）
│   │   ├── utils/           # 工具函数（localStorage 封装等）
│   │   ├── views/           # 页面视图
│   │   └── config.js        # 运行时配置（服务器地址）
│   ├── electron-builder.yml # Electron 打包配置
│   ├── server-config.json   # 服务器地址配置模板
│   └── package.json
└── README.md
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- MySQL 8.0

### 数据库配置（重要）

本项目不包含任何数据库密码，clone 后需要自行配置。

1. 创建 `.env` 文件：

```bash
cd backend
cp .env.example .env   # 或手动创建
```

2. 编辑 `backend/.env`，填入你的 MySQL 信息：

```env
DB_USER=root
DB_PASSWORD=你的MySQL密码
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=campus_im
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
```

3. 创建数据库：

```bash
mysql -u root -p -e "CREATE DATABASE campus_im CHARACTER SET utf8mb4;"
```

> **安全说明：** `backend/.env` 已被 `.gitignore` 忽略，不会被提交到仓库。
> 请勿将个人密码提交到版本控制中。

### 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库表
flask db init
flask db migrate
flask db upgrade

# 启动服务
python run.py
```

后端默认运行在 `http://localhost:5000`

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端默认运行在 `http://localhost:3000`

### 桌面客户端启动（Electron）

```bash
cd frontend

# 开发调试（需要先启动后端）
npm run electron:dev

# 构建安装包
npm run electron:build
# 输出：release/校园即时通信 Setup x.x.x.exe（安装版）
#       release/校园即时通信 x.x.x.exe（免安装版）
```

桌面客户端默认连接 `http://localhost:5000`，可通过系统托盘 → 右键 → "设置服务器地址" 修改。

## 测试

```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npx vitest
```

## 许可证

本项目仅供学习交流使用。
