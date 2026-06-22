# 大学录取信息整理系统 - API 接口文档

## 📋 任务队列 API

### 1. 获取任务列表
**GET** `/api/tasks?status=pending`

**响应:**
```json
{
  "tasks": [{"id": 1, "url": "https://...", "status": "pending", "progress": 0}],
  "total": 1
}
```

### 2. 批量创建任务
**POST** `/api/tasks/batch`

**参数:** `urls` (每行一个 URL)

**响应:**
```json
{"success": true, "created": 2}
```

### 3. 执行单个任务
**POST** `/api/tasks/{id}/execute`

### 4. 执行全部任务
**POST** `/api/tasks/execute_all`

### 5. 删除任务
**DELETE** `/api/tasks/{id}`

### 6. 更新任务状态 (OpenClaw 调用)
**POST** `/api/tasks/{id}/status`

**请求体:**
```json
{"status": "processing", "progress": 50}
```

### 7. 写入采集结果 (OpenClaw 调用)
**POST** `/api/tasks/{id}/results`

**请求体:**
```json
{
  "records": [
    {"student_name_cn": "张明", "university_cn": "剑桥大学", ...}
  ]
}
```

---

## 🔄 OpenClaw 集成流程

```python
# 1. 拉取待处理任务
tasks = GET /api/tasks?status=pending

# 2. 更新状态为 processing
POST /api/tasks/{id}/status {"status": "processing", "progress": 10}

# 3. 执行采集
records = collect_from_url(task.url)

# 4. 写入结果
POST /api/tasks/{id}/results {"records": [...]}

# 5. 更新为 completed
POST /api/tasks/{id}/status {"status": "completed", "progress": 100}
```

---

## 📊 当前 API 状态

| API | 状态 | 说明 |
|-----|------|------|
| GET /api/tasks | ✅ | 获取任务列表 |
| POST /api/tasks/batch | ✅ | 批量创建 |
| POST /api/tasks/execute_all | ✅ | 执行全部 |
| DELETE /api/tasks/{id} | ✅ | 删除任务 |
| POST /api/tasks/{id}/status | ⏳ | 待添加 |
| POST /api/tasks/{id}/results | ⏳ | 待添加 |

---

**更新时间:** 2026-03-19 18:45 CST
