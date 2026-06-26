# 校园即时通信与文件传输系统

面向校园用户的 Web 端即时通信与文件传输平台，支持单聊、群聊、文件上传下载、好友管理等功能。

## 技术栈

### 后端
- **Python 3.10+** + **Flask 3.x** — Web 框架
- **Flask-SocketIO** — WebSocket 实时通信
- **SQLAlchemy** — ORM 数据库操作
- **Flask-JWT-Extended** — JWT 认证
- **MySQL 8.0** — 关系型数据库

### 前端
- **Vue 3** — 前端框架 (Composition API)
- **Element Plus** — UI 组件库
- **Pinia** — 状态管理
- **Socket.IO Client** — WebSocket 客户端
- **Vite** — 构建工具

## 功能特性

- 用户注册 / 登录（JWT 认证）
- 好友搜索、申请、管理
- 单聊 / 群聊实时消息
- 文件上传 / 下载（支持图片、文档、压缩包等）
- 消息记录持久化与分页加载
- 在线状态显示
- 未读消息计数

## 项目结构

```
campus-im/
├── backend/                 # 后端项目
│   ├── app/
│   │   ├── models/          # 数据模型
│   │   ├── routes/          # API 路由
│   │   ├── services/        # 业务逻辑
│   │   ├── sockets/         # WebSocket 事件
│   │   └── utils/           # 工具函数
│   ├── uploads/             # 文件上传目录
│   ├── requirements.txt     # Python 依赖
│   └── run.py               # 启动入口
├── frontend/                # 前端项目
│   ├── src/
│   │   ├── api/             # API 请求
│   │   ├── components/      # 公共组件
│   │   ├── stores/          # 状态管理
│   │   ├── views/           # 页面视图
│   │   └── router/          # 路由配置
│   └── package.json
├── docs/                    # 项目文档
│   ├── 需求分析文档.docx
│   ├── 系统设计文档.docx
│   └── 架构设计说明书.docx
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

前端默认运行在 `http://localhost:5173`

## 文档

详细文档请查看 [docs/](./docs/) 目录：

- 需求分析文档 — 功能需求、用户角色、用例分析
- 系统设计文档 — 数据库设计、API 接口、模块划分
- 架构设计说明书 — 系统架构、技术选型、部署方案

## 许可证

本项目仅供学习交流使用。
