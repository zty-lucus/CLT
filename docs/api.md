# Campus IM API 文档

> 基础路径：`/api`
>
> 认证方式：JWT Bearer Token（Header: `Authorization: Bearer <token>`）

---

## 统一响应格式

**成功：**

```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

**失败：**

```json
{
  "code": 1001,
  "message": "错误信息",
  "data": null
}
```

---

## 错误码

| Code | 含义 | 说明 |
|------|------|------|
| 0 | 成功 | 请求正常 |
| 1001 | 参数错误 | 缺少必填字段、格式校验失败 |
| 1002 | 用户名已存在 | 注册/更新时用户名重复 |
| 1003 | 邮箱已存在 | 注册/更新时邮箱重复 |
| 1004 | 用户名或密码错误 | 登录失败 |
| 1005 | Token无效或过期 | JWT 验证失败 |
| 1006 | 无权限 | 非管理员/群主操作 |
| 1007 | 资源不存在 | 用户/会话/消息未找到 |
| 1008 | 文件过大 | 超过 50MB 限制 |
| 1009 | 文件类型不支持 | 不在白名单内 |
| 2001 | 已是好友 | 重复发送好友请求 |
| 2002 | 已在群中 | 重复加入群聊 |

---

## Auth 模块

### POST /api/auth/register

用户注册。无需认证。

**请求体：**

```json
{
  "username": "zhangsan",
  "password": "123456",
  "email": "zhangsan@example.com",
  "nickname": "张三"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 3-20位，字母数字下划线 |
| password | string | 是 | 6-32位 |
| email | string | 否 | 邮箱格式 |
| nickname | string | 否 | 默认等于 username |

**成功响应 (200)：**

```json
{
  "code": 0,
  "message": "注册成功",
  "data": {
    "user_id": 1
  }
}
```

**失败响应：**

```json
{
  "code": 1001,
  "message": "用户名长度需为3~20个字符",
  "data": null
}
```

---

### POST /api/auth/login

用户登录。无需认证。

**请求体：**

```json
{
  "username": "zhangsan",
  "password": "123456"
}
```

**成功响应 (200)：**

```json
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "zhangsan",
      "nickname": "张三",
      "avatar": "default.png"
    }
  }
}
```

**失败响应 (401)：**

```json
{
  "code": 1004,
  "message": "用户名或密码错误",
  "data": null
}
```

---

### POST /api/auth/logout

用户登出。需要认证。

**请求头：**

```
Authorization: Bearer <token>
```

**成功响应 (200)：**

```json
{
  "code": 0,
  "message": "登出成功",
  "data": null
}
```

---

## User 模块

### GET /api/users/profile

获取当前用户资料。需要认证。

**请求头：**

```
Authorization: Bearer <token>
```

**成功响应 (200)：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "username": "zhangsan",
    "nickname": "张三",
    "avatar": "default.png",
    "signature": "你好世界",
    "email": "zhangsan@example.com",
    "status": 1,
    "created_at": "2026-06-19 10:30:00"
  }
}
```

**失败响应 (401)：**

```json
{
  "code": 1005,
  "message": "Token无效或过期",
  "data": null
}
```

---

### PUT /api/users/profile

更新当前用户资料。需要认证。

**请求头：**

```
Authorization: Bearer <token>
```

**请求体（所有字段可选）：**

```json
{
  "nickname": "新昵称",
  "avatar": "avatar.png",
  "signature": "新的个性签名",
  "username": "newname",
  "email": "new@example.com"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| nickname | string | 昵称 |
| avatar | string | 头像文件名 |
| signature | string | 个性签名 |
| username | string | 用户名（需唯一） |
| email | string | 邮箱（需唯一） |

**成功响应 (200)：**

```json
{
  "code": 0,
  "message": "更新成功",
  "data": {
    "id": 1,
    "username": "newname",
    "nickname": "新昵称",
    "avatar": "avatar.png",
    "signature": "新的个性签名",
    "email": "new@example.com"
  }
}
```

**失败响应：**

```json
{
  "code": 1002,
  "message": "用户名已存在",
  "data": null
}
```

---

## JWT 使用方式

### 获取 Token

调用 `POST /api/auth/login` 成功后，从 `data.token` 获取。

### 携带 Token

所有需要认证的接口，在请求头中添加：

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token 过期

- 有效期：**7天**
- 过期后接口返回 `code: 1005`，HTTP 状态码 `401`
- 前端收到 1005 后应清除本地 token 并跳转登录页

### 后端使用

```python
from flask_jwt_extended import jwt_required, get_jwt_identity

@bp.route('/some-api', methods=['GET'])
@jwt_required()
def some_api():
    user_id = get_jwt_identity()  # 返回用户ID (int)
    ...
```

---

## WebSocket 连接

### 连接地址

```
ws://localhost:5000/socket.io/?token=<jwt_token>&EIO=4&transport=websocket
```

或使用 Socket.IO 客户端：

```javascript
const socket = io('http://localhost:5000', {
  auth: { token: 'jwt_token_here' }
});
```

### 事件

| 事件 | 方向 | 数据 | 说明 |
|------|------|------|------|
| connect | 客户端 -> 服务端 | `{ token: "..." }` | 建立连接，验证 JWT |
| disconnect | 客户端 -> 服务端 | - | 断开连接 |
| user_online | 服务端 -> 客户端 | `{ user_id, username }` | 广播：用户上线 |
| user_offline | 服务端 -> 客户端 | `{ user_id }` | 广播：用户下线 |

---

## B/C 部分接入说明

### 接入前提

A部分已完成以下基础设施，B/C可直接使用：

| 组件 | 文件 | 用途 |
|------|------|------|
| 数据库模型 | `app/models/*.py` | User, Message, Conversation, Friendship, File |
| 统一响应 | `app/utils/response.py` | `success(data, message)` / `error(code, message, status)` |
| JWT 验证 | `app/utils/auth.py` | `get_current_user_id()` 获取当前用户ID |
| 参数校验 | `app/utils/validators.py` | `validate_username/validate_password/validate_email/validate_file` |
| 数据库实例 | `app/extensions.py` | `from app.extensions import db` |

### 注册 Blueprint

在 `app/__init__.py` 中添加：

```python
from app.routes.chat import chat_bp
from app.routes.group import group_bp
app.register_blueprint(chat_bp, url_prefix='/api/conversations')
app.register_blueprint(group_bp, url_prefix='/api/groups')
```

### 新建路由文件示例

```python
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.response import success, error

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/', methods=['GET'])
@jwt_required()
def get_conversations():
    user_id = get_jwt_identity()
    # your logic here
    return success(data)
```

### 新建模型文件

在 `app/models/` 下新建，然后在 `app/models/__init__.py` 中导入：

```python
from app.models.your_model import YourModel
```

### 注册 WebSocket 事件

在 `app/sockets/` 下新建文件，然后在 `app/__init__.py` 中导入：

```python
import app.sockets.chat_events  # noqa: F401
```

### 数据库迁移

模型变更后执行：

```bash
cd backend
flask db migrate -m "描述"
flask db upgrade
```
