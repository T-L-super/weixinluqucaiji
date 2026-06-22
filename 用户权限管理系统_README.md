# 用户权限管理系统 - Agent-10

## 📋 概述

为大学录取信息整理系统实现的多用户角色权限控制系统，支持 JWT Token 认证和三种角色权限管理。

## 🎯 角色定义

| 角色 | 标识 | 权限 |
|------|------|------|
| **超级管理员** | `super_admin` | 全部权限 (`*`) |
| **数据管理员** | `data_admin` | 数据管理权限 (`read`, `write`, `delete`, `manage_users`) |
| **普通用户** | `normal_user` | 只读权限 (`read`) |

## 🔐 默认账户

```
用户名：admin
密码：admin123
角色：超级管理员
```

⚠️ **重要：** 请在生产环境中立即修改默认密码！

## 📁 文件结构

```
backend/app/
├── auth.py           # 认证模块（新增）
├── models.py         # 数据模型（已修改，添加用户相关模型）
├── main.py           # 主应用（已修改，添加用户 API）
└── admin_page.py     # 管理界面（已修改，添加登录界面）

backend/
├── migrate_auth.py   # 数据库迁移脚本（新增）
└── test_auth_api.py  # API 测试脚本（新增）
```

## 🚀 快速开始

### 1. 初始化数据库

```bash
cd /root/.openclaw/workspace/大学录取信息整理系统/backend
python3 migrate_auth.py
```

### 2. 启动服务

```bash
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 访问系统

打开浏览器访问：`http://localhost:8000`

系统会显示登录界面，使用默认账户登录即可。

## 🧪 测试 API

```bash
python3 test_auth_api.py
```

## 📡 API 接口

### 认证相关

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/api/auth/login` | 用户登录 | 公开 |
| GET | `/api/auth/me` | 获取当前用户信息 | 已认证 |
| POST | `/api/auth/register` | 注册用户 | manage_users |

### 用户管理

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/users` | 获取用户列表 | manage_users |
| PUT | `/api/users/{user_id}` | 更新用户信息 | manage_users |
| POST | `/api/users/{user_id}/deactivate` | 停用用户 | manage_users |
| POST | `/api/users/{user_id}/activate` | 激活用户 | manage_users |

### 角色管理

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/roles` | 获取角色列表 | 已认证 |

## 🔑 JWT Token 使用

登录后，服务器会返回一个 JWT Token：

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "full_name": "系统管理员",
    "role_name": "super_admin"
  }
}
```

后续请求需要在 Header 中添加：

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 💻 前端集成

### 1. 登录流程

```javascript
// 登录
async function login(username, password) {
  const res = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  
  const data = await res.json();
  localStorage.setItem('authToken', data.access_token);
  return data;
}

// 登出
function logout() {
  localStorage.removeItem('authToken');
  window.location.reload();
}
```

### 2. 权限检查

```javascript
// 检查权限
function hasPermission(permission) {
  const user = JSON.parse(localStorage.getItem('currentUser'));
  if (!user || !user.permissions) return false;
  
  const permissions = JSON.parse(user.permissions);
  return permissions.includes('*') || permissions.includes(permission);
}

// 使用示例
if (hasPermission('manage_users')) {
  // 显示用户管理功能
}
```

### 3. API 请求封装

```javascript
// 带认证的 API 请求
async function apiRequest(url, options = {}) {
  const token = localStorage.getItem('authToken');
  
  const res = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  if (res.status === 401) {
    // Token 过期，跳转到登录页
    logout();
    return;
  }
  
  return res.json();
}
```

## 🛡️ 安全建议

1. **修改默认密码**：首次登录后立即修改 admin 账户密码
2. **使用 HTTPS**：生产环境必须使用 HTTPS 传输
3. **定期更新密钥**：定期更换 `auth.py` 中的 `SECRET_KEY`
4. **密码策略**：实施密码强度要求（长度、复杂度等）
5. **登录限制**：实施登录失败次数限制
6. **Token 过期**：合理设置 Token 过期时间（当前为 24 小时）

## 📝 依赖安装

确保安装以下 Python 包：

```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

## ✅ 完成清单

- [x] 设计数据库表：users, roles, user_roles
- [x] 创建数据库迁移脚本
- [x] 实现用户认证（JWT token）
- [x] 实现权限中间件
- [x] 添加登录/注册界面
- [x] 实现用户管理界面
- [x] 新增 `auth.py` - 认证模块
- [x] 修改 `main.py` 添加用户 API
- [x] 修改 `models.py` 添加用户模型
- [x] 修改 `admin_page.py` 添加登录界面

## 🎉 完成状态

**Agent-10 完成：用户权限管理，支持 3 角色 + JWT 认证**
