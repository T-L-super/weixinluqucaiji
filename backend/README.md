# 大学录取信息整理系统 - 后端 API

## 📋 项目简介

大学录取信息整理系统的后端 API 服务，基于 FastAPI 框架开发，提供 RESTful 接口供前端调用。

**完成时间**: 2026-03-18 23:32 UTC

## 🚀 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 启动服务

**开发环境**（SQLite，热重载）：

```bash
python main.py
```

或使用 uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**生产环境**（MySQL，多 worker）：

```bash
# 修改 models.py 中的 DATABASE_URL 为 MySQL 连接字符串
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

### 3. 访问 API 文档

启动后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 健康检查：http://localhost:8000/health

## 📁 项目结构

```
backend/
├── main.py              # FastAPI 主应用
├── models.py            # SQLAlchemy 数据模型（7 张表）
├── schemas.py           # Pydantic 数据验证模式
├── requirements.txt     # Python 依赖
├── README.md            # 本文档
├── api/                 # API 路由目录
│   ├── __init__.py
│   ├── records.py       # 录取记录 API
│   ├── tasks.py         # 采集任务 API
│   └── stats.py         # 统计数据 API
└── static/              # 静态文件（前端）
    └── favicon.ico
```

## 🗄️ 数据库设计

### 7 张核心表

| 表名 | 说明 | 主要功能 |
|------|------|----------|
| `countries` | 国家/地区表 | 存储国家信息，支持洲、地区分类 |
| `universities` | 大学信息表 | 存储大学排名、类型、目标院校标记 |
| `source_schools` | 来源学校表 | 存储学生来源学校信息 |
| `admission_requirements` | 录取条件表 | 存储各大学专业的录取要求 |
| `admission_records` | 录取记录表 | **核心表**，存储录取数据 |
| `collection_tasks` | 采集任务表 | 存储数据采集任务队列 |
| `statistics_daily` | 每日统计表 | 存储预计算的统计数据 |

## 🔌 API 接口

### 录取记录 (`/api/records`)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/records` | 查询录取记录列表（支持分页和筛选） |
| GET | `/api/records/{id}` | 获取单条记录详情 |
| POST | `/api/records` | 创建新记录 |
| PUT | `/api/records/{id}` | 更新记录 |
| DELETE | `/api/records/{id}` | 删除记录 |

**筛选参数**：
- `student_name`: 学生姓名（模糊搜索）
- `university_id`: 大学 ID
- `country_id`: 国家 ID
- `application_year`: 申请年份
- `is_verified`: 验证状态

### 采集任务 (`/api/tasks`)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tasks` | 查询任务列表 |
| GET | `/api/tasks/{id}` | 获取任务详情 |
| POST | `/api/tasks` | 创建任务 |
| POST | `/api/tasks/batch` | 批量创建任务 |
| PUT | `/api/tasks/{id}` | 更新任务 |
| DELETE | `/api/tasks/{id}` | 删除任务 |
| POST | `/api/tasks/{id}/retry` | 重试失败任务 |

**任务状态**：`pending` → `processing` → `completed` / `failed`

### 统计数据 (`/api/stats`)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/stats/overview` | 总体统计概览 |
| GET | `/api/stats/by-country` | 按国家统计 |
| GET | `/api/stats/by-university` | 按大学统计 |
| GET | `/api/stats/by-year` | 按年份统计趋势 |
| GET | `/api/stats/recent` | 最近 N 天统计 |
| GET | `/api/stats/score-distribution` | 成绩分布分析 |

### 基础数据

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/countries` | 获取所有国家列表 |
| GET | `/api/universities` | 获取大学列表（支持筛选） |

### 系统接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/` | API 根路径信息 |

## 📊 数据验证

### 录取记录字段验证

| 字段 | 类型 | 范围/限制 | 必填 |
|------|------|-----------|------|
| student_name | String | 1-100 字符 | ✅ |
| university_id | Integer | - | ✅ |
| gpa | Float | 0-4.0 | ❌ |
| toefl | Integer | 0-120 | ❌ |
| ielts | Float | 0-9.0 | ❌ |
| sat | Integer | 400-1600 | ❌ |
| application_year | Integer | 2000-2100 | ❌ |
| data_completeness | Integer | 1-5 | ❌ |

### 采集任务字段验证

| 字段 | 类型 | 范围/限制 | 必填 |
|------|------|-----------|------|
| url | String | 必须以 http(s):// 开头 | ✅ |
| priority | Integer | 1-10，默认 5 | ❌ |
| title | String | 最大 300 字符 | ❌ |

## ⚙️ 配置说明

### 数据库配置

开发环境（SQLite）：
```python
DATABASE_URL = "sqlite:///./admission_system.db"
```

生产环境（MySQL）：
```python
DATABASE_URL = "mysql+pymysql://user:password@localhost/admission_system"
```

### CORS 配置

在 `main.py` 中修改 `allow_origins` 列表，添加前端域名。

## 🔒 安全设计

- ✅ 数据验证：Pydantic 严格验证所有输入
- ✅ 错误处理：统一异常处理，避免信息泄露
- ✅ SQL 注入防护：SQLAlchemy ORM 参数化查询
- ✅ CORS 控制：限制跨域访问来源
- ⏳ JWT 认证：待实现（后续版本）
- ⏳ RBAC 权限：待实现（后续版本）

## 🧪 测试

### 使用 Swagger UI 测试

访问 http://localhost:8000/docs，可交互式测试所有接口。

### 使用 curl 测试

```bash
# 健康检查
curl http://localhost:8000/health

# 获取国家列表
curl http://localhost:8000/api/countries

# 创建录取记录
curl -X POST "http://localhost:8000/api/records" \
  -H "Content-Type: application/json" \
  -d '{
    "student_name": "张三",
    "university_id": 1,
    "gpa": 3.8,
    "toefl": 105
  }'

# 查询记录列表
curl "http://localhost:8000/api/records?page=1&page_size=20"
```

## 📝 开发规范

### 代码风格

- 遵循 PEP 8 规范
- 使用 Black 格式化代码
- 使用 Flake8 进行代码检查

### 提交规范

```
feat: 添加新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建/工具链相关
```

## 🚧 后续优化

- [ ] JWT Token 认证
- [ ] RBAC 角色权限控制
- [ ] 操作日志记录
- [ ] 数据库连接池优化
- [ ] Redis 缓存热点数据
- [ ] 批量导出 Excel 功能
- [ ] WebSocket 实时推送

## 📞 技术支持

如有问题，请查看：
- API 文档：http://localhost:8000/docs
- 系统设计文档：`../设计方案/01-系统设计方案.html`

---

**版本**: v1.0.0  
**创建时间**: 2026-03-18  
**作者**: 909 运营助理
