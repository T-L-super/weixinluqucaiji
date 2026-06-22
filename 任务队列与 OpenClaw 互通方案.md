# 任务队列与 OpenClaw 互通技术方案

## 📋 方案概述

实现管理后台任务队列与 OpenClaw 采集能力的双向互通。

---

## 🏗️ 技术架构

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   管理后台      │      │   数据库        │      │   OpenClaw      │
│   (Vue/HTML)    │─────▶│   SQLite/MySQL  │◀─────│   采集技能      │
│                 │      │                 │      │                 │
│ - 创建任务      │      │ - tasks 表      │      │ - 轮询任务      │
│ - 查看队列      │      │ - 状态更新      │      │ - 执行采集      │
│ - 监控进度      │      │ - 结果回写      │      │ - 更新状态      │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

---

## 🔗 互通方式

### 方案 1: 数据库轮询（推荐 ✅）

**原理:**
- OpenClaw 定期查询 `collection_tasks` 表
- 发现 `status='pending'` 的任务
- 执行采集并更新状态

**优点:**
- ✅ 简单可靠
- ✅ 无需额外服务
- ✅ 易于调试

**缺点:**
- ⚠️ 有延迟（轮询间隔）

**实现:**
```python
# OpenClaw 采集技能
async def poll_and_execute():
    while True:
        # 查询待处理任务
        tasks = db.query("SELECT * FROM collection_tasks WHERE status='pending' LIMIT 5")
        
        for task in tasks:
            # 更新状态
            db.execute("UPDATE collection_tasks SET status='processing', progress=10 WHERE id=?", task.id)
            
            # 执行采集
            try:
                records = collect_from_url(task.url)
                save_to_database(records)
                
                # 更新为完成
                db.execute("UPDATE collection_tasks SET status='completed', progress=100, records_count=? WHERE id=?", len(records), task.id)
            except Exception as e:
                # 更新为失败
                db.execute("UPDATE collection_tasks SET status='failed', error_message=? WHERE id=?", str(e), task.id)
        
        # 等待 30 秒
        await asyncio.sleep(30)
```

---

### 方案 2: Webhook 回调

**原理:**
- 创建任务时触发 webhook
- OpenClaw 接收 webhook 并执行

**优点:**
- ✅ 实时触发
- ✅ 低延迟

**缺点:**
- ⚠️ 需要额外服务
- ⚠️ 配置复杂

---

### 方案 3: OpenClaw Skill 直接调用

**原理:**
- 通过 OpenClaw 技能系统直接调用采集器
- 实时执行并返回结果

**优点:**
- ✅ 无缝集成
- ✅ 统一管理

---

## 📊 数据库表设计

```sql
CREATE TABLE collection_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,              -- 微信文章链接
    title TEXT,                      -- 任务标题
    status TEXT DEFAULT 'pending',   -- pending/processing/completed/failed
    progress INTEGER DEFAULT 0,      -- 进度 0-100
    records_count INTEGER DEFAULT 0, -- 提取记录数
    error_message TEXT,              -- 错误信息
    created_at DATETIME,             -- 创建时间
    started_at DATETIME,             -- 开始时间
    completed_at DATETIME,           -- 完成时间
    created_by TEXT DEFAULT 'admin'  -- 创建者
);

CREATE INDEX idx_task_status ON collection_tasks(status);
CREATE INDEX idx_task_created ON collection_tasks(created_at);
```

---

## 🔄 任务状态流转

```
pending ──▶ processing ──▶ completed
   │            │
   │            └──────▶ failed
   │
   └──────▶ deleted
```

**状态说明:**
- `pending`: 待处理（刚创建）
- `processing`: 执行中（OpenClaw 已接收）
- `completed`: 已完成（采集成功）
- `failed`: 失败（采集出错）

---

## 🚀 实施步骤

### 步骤 1: 数据库就绪 ✅
```bash
# 已创建 collection_tasks 表
```

### 步骤 2: API 就绪 ✅
```bash
# 任务队列 API 已添加
GET /api/tasks      - 获取任务列表
POST /api/tasks/batch - 批量创建任务
DELETE /api/tasks/{id} - 删除任务
POST /api/tasks/execute_all - 执行全部
```

### 步骤 3: OpenClaw 技能配置
创建 OpenClaw 技能文件，实现轮询逻辑。

### 步骤 4: 测试流程
1. 管理后台创建任务
2. OpenClaw 轮询到任务
3. 执行采集
4. 更新数据库
5. 管理后台显示结果

---

## 📝 推荐方案

**采用方案 1（数据库轮询）+ 方案 3（OpenClaw Skill）**

**理由:**
1. 简单可靠，无需额外服务
2. 与 OpenClaw 技能系统无缝集成
3. 支持批量处理和并发控制
4. 易于监控和调试

---

## 🌐 立即测试

**访问管理后台:** http://101.32.98.235:8000

**操作步骤:**
1. 点击「📝 任务队列」
2. 点击「+ 新建任务」
3. 批量粘贴微信文章链接
4. 点击「创建任务」
5. 查看任务列表
6. 点击「▶ 执行全部」

---

## 🔧 配置参数

```python
# 轮询间隔（秒）
POLL_INTERVAL = 30

# 并发任务数
MAX_CONCURRENT = 3

# 超时时间（秒）
TIMEOUT = 300

# 重试次数
MAX_RETRIES = 3
```
