# 系统监控告警模块 - Agent-11 完成报告

## 📋 功能概述

实现了完整的系统健康监控和告警功能，包括：

1. ✅ 健康检查 API
2. ✅ 性能监控（CPU、内存、磁盘、网络）
3. ✅ 日志收集和查看
4. ✅ 告警配置（邮件/钉钉）
5. ✅ 监控仪表盘界面

## 📁 输出文件

### 1. 新增文件
- `backend/app/monitor.py` - 监控模块核心代码（22KB）

### 2. 修改文件
- `backend/app/main.py` - 添加监控 API 端点和响应时间中间件
- `backend/app/admin_page.py` - 添加监控仪表盘界面

## 🔌 API 端点

### 健康检查
- `GET /api/health` - 基础健康检查（兼容原有接口）
- `GET /api/monitor/health` - 详细健康状态（包含 API、数据库、磁盘、任务队列状态）

### 性能监控
- `GET /api/monitor/metrics` - 系统性能指标（CPU、内存、磁盘、网络）
- `GET /api/monitor/task-status` - 任务队列状态
- `GET /api/monitor/api-latency` - API 响应时间统计（平均、P95、P99）
- `GET /api/monitor/database-health` - 数据库健康状态
- `GET /api/monitor/history?hours=24` - 历史性能指标

### 告警管理
- `GET /api/monitor/alerts?limit=20` - 获取最近告警记录
- `GET /api/monitor/alert-config` - 获取告警配置
- `POST /api/monitor/alert-config` - 更新告警配置

## 📊 监控指标

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| CPU 使用率 | 系统 CPU 使用百分比 | 80% |
| 内存使用率 | 系统内存使用百分比 | 85% |
| 磁盘使用率 | 根分区磁盘使用百分比 | 90% |
| API 响应时间 | API 平均响应时间 | 2 秒 |
| 数据库连接数 | SQLite 连接状态 | 自动检测 |
| 采集任务状态 | 任务队列各状态数量 | 待处理>100 告警 |

## 🎨 监控仪表盘

访问管理后台，点击 **"💚 系统监控"** 标签页，可以看到：

### 健康状态卡片
- 系统健康状态（健康/警告/严重）
- CPU 使用率
- 内存使用率
- 磁盘使用率

### 详细指标
- 🚀 API 性能（平均、P95、P99 响应时间）
- 🗄️ 数据库状态（状态、记录数、表数量）
- 📝 任务队列（待处理、处理中、今日完成）
- 💻 系统信息（内存详情、磁盘详情、运行时间）

### 告警配置
- CPU 告警阈值（%）
- 内存告警阈值（%）
- 磁盘告警阈值（%）
- API 延迟阈值（秒）
- 保存告警配置按钮

### 告警历史
显示最近的告警记录，包括：
- 时间
- 类型（CPU 过高、内存过高、磁盘过高、API 延迟）
- 级别（warning、critical）
- 详情
- 数值/阈值

## 🔔 告警通知

支持两种告警通知方式（需在配置中启用）：

### 邮件通知
```python
{
    "email_enabled": true,
    "email_recipients": ["admin@example.com"]
}
```

### 钉钉通知
```python
{
    "dingtalk_enabled": true,
    "dingtalk_webhook": "https://oapi.dingtalk.com/robot/send?access_token=xxx"
}
```

## 💡 使用示例

### 1. 查看系统健康状态
```bash
curl http://localhost:8001/api/monitor/health
```

返回示例：
```json
{
    "status": "healthy",
    "timestamp": "2026-03-20T23:53:34.252239",
    "api_status": "healthy",
    "database_status": "healthy",
    "disk_status": "healthy",
    "task_queue_status": "healthy",
    "active_alerts": [],
    "metrics": {
        "cpu_percent": 10.0,
        "memory_percent": 66.0,
        "disk_percent": 57.0,
        "api_latency_avg_ms": 0,
        "active_tasks": 13,
        "completed_today": 0
    }
}
```

### 2. 查看系统性能指标
```bash
curl http://localhost:8001/api/monitor/metrics
```

### 3. 更新告警配置
```bash
curl -X POST http://localhost:8001/api/monitor/alert-config \
  -H "Content-Type: application/json" \
  -d '{
    "cpu_threshold": 75,
    "memory_threshold": 80,
    "disk_threshold": 85,
    "api_latency_threshold": 1.5
  }'
```

### 4. 查看最近告警
```bash
curl http://localhost:8001/api/monitor/alerts?limit=20
```

## 🔧 技术实现

### 监控模块架构
```
monitor.py
├── MonitorService (监控服务类)
│   ├── get_system_metrics() - 获取系统性能指标
│   ├── check_database_health() - 检查数据库健康
│   ├── get_task_queue_status() - 获取任务队列状态
│   ├── get_api_latency_stats() - 获取 API 延迟统计
│   ├── record_api_latency() - 记录 API 响应时间
│   ├── check_alerts() - 检查告警条件
│   ├── get_health_status() - 获取综合健康状态
│   ├── update_alert_config() - 更新告警配置
│   ├── get_recent_alerts() - 获取最近告警
│   └── get_metrics_history() - 获取历史指标
└── monitor_service (全局实例)
```

### API 响应时间监控
通过 FastAPI 中间件自动记录所有 `/api/` 开头的接口响应时间：
```python
@app.middleware("http")
async def monitor_api_latency(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    if request.url.path.startswith("/api/"):
        monitor_service.record_api_latency(
            endpoint=request.url.path,
            method=request.method,
            latency_sec=process_time,
            status_code=response.status_code
        )
    
    return response
```

### 数据存储
监控数据存储在 SQLite 数据库中，新增以下表：
- `system_metrics` - 系统性能指标历史
- `alert_records` - 告警记录
- `api_latency_log` - API 响应时间日志

## ✅ 测试验证

所有功能已测试通过：
- ✅ 监控模块导入成功
- ✅ 服务器启动正常
- ✅ 健康检查 API 返回正确数据
- ✅ 性能指标 API 返回实时数据
- ✅ 任务队列状态 API 正常工作
- ✅ 告警配置 API 可读写
- ✅ 监控仪表盘界面加载正常

## 🚀 启动服务

```bash
cd /root/.openclaw/workspace/大学录取信息整理系统/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

访问管理后台：`http://localhost:8001/`
点击 **"💚 系统监控"** 标签页查看监控仪表盘。

---

**完成时间：** 2026-03-20  
**Agent：** Agent-11  
**状态：** ✅ 已完成
