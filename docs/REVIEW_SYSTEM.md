# 数据审核功能文档（Agent-15）

## 功能概述

为大学录取信息整理系统实现了完整的数据审核机制，支持单条/批量审核、审核意见记录和审核历史追溯。

## 核心功能

### 1. 审核状态管理

每条录取记录新增以下审核相关字段：

- `review_status`: 审核状态
  - `pending`: 待审核
  - `approved`: 已通过
  - `rejected`: 已拒绝
- `reviewed_at`: 审核时间
- `reviewed_by`: 审核人 ID
- `review_comment`: 审核意见

### 2. 后端 API

#### 单条审核

```http
POST /api/records/{record_id}/approve
Content-Type: application/json
Authorization: Bearer {token}

{
  "comment": "审核意见（选填）"
}

Response:
{
  "message": "审核通过成功",
  "record_id": 123,
  "new_status": "approved"
}
```

```http
POST /api/records/{record_id}/reject
Content-Type: application/json
Authorization: Bearer {token}

{
  "comment": "拒绝原因（选填）"
}

Response:
{
  "message": "审核拒绝成功",
  "record_id": 123,
  "new_status": "rejected"
}
```

#### 待审核列表

```http
GET /api/records/pending-review?page=1&page_size=50
Authorization: Bearer {token}

Response:
{
  "records": [...],
  "total": 100,
  "page": 1,
  "page_size": 50,
  "total_pages": 2
}
```

#### 批量审核

```http
POST /api/records/batch-review
Content-Type: application/json
Authorization: Bearer {token}

{
  "record_ids": [1, 2, 3, 4, 5],
  "action": "approve",  // 或 "reject"
  "comment": "批量审核意见（选填）"
}

Response:
{
  "message": "批量审核完成，成功 5 条",
  "processed_count": 5,
  "failed": [],
  "action": "approve",
  "new_status": "approved"
}
```

#### 审核日志

```http
# 获取单条记录的审核历史
GET /api/records/review-logs/{record_id}
Authorization: Bearer {token}

# 获取所有审核日志（最近 N 条）
GET /api/records/review-logs?limit=50
Authorization: Bearer {token}

Response:
{
  "logs": [
    {
      "id": 1,
      "record_id": 123,
      "action": "approve",
      "previous_status": "pending",
      "new_status": "approved",
      "comment": "数据完整，予以通过",
      "reviewer_id": 1,
      "reviewer_username": "admin",
      "reviewer_name": "管理员",
      "created_at": "2026-03-20 16:00:00"
    }
  ],
  "total": 1
}
```

### 3. 前端审核界面

#### 审核标签页

- 位置：管理后台顶部导航栏 → "🔍 数据审核"
- 显示所有待审核记录
- 支持单条审核操作（通过/拒绝）
- 支持批量审核操作
- 可查看审核历史

#### 审核操作流程

1. **单条审核**
   - 点击"✅ 通过"或"❌ 拒绝"按钮
   - 输入审核意见（选填）
   - 提交审核

2. **批量审核**
   - 勾选要审核的记录
   - 点击"批量通过"或"批量拒绝"
   - 输入批量审核意见（选填）
   - 确认执行

3. **查看审核历史**
   - 点击"📜 历史"按钮
   - 查看该记录的所有审核操作记录

### 4. 权限控制

审核功能需要以下权限之一：

- `review_records`: 审核记录权限
- `manage_users`: 管理员权限（自动拥有所有权限）

## 数据库迁移

执行以下命令应用数据库更改：

```bash
cd /root/.openclaw/workspace/大学录取信息整理系统/backend
python3 migrations/add_review_system.py
```

迁移内容：

1. 为 `admission_records` 表添加审核字段
2. 创建 `review_logs` 审核日志表
3. 为现有记录设置默认审核状态
4. 创建相关索引优化查询性能

## 测试验证

运行测试脚本验证功能：

```bash
# 确保后端服务已启动
python -m uvicorn app.main:app --reload

# 运行测试
python3 tests/test_review_system.py
```

## 文件清单

### 修改的文件

1. **backend/app/models.py**
   - 为 `AdmissionRecord` 模型添加审核字段
   - 新增 `ReviewLog` 模型

2. **backend/app/main.py**
   - 添加审核相关 Pydantic 模型
   - 实现审核 API 端点
   - 数据库初始化时创建审核日志表

3. **backend/app/admin_page.py**
   - 添加审核标签页 UI
   - 添加审核相关 CSS 样式
   - 实现审核相关 JavaScript 功能

### 新增的文件

1. **backend/migrations/add_review_system.py**
   - 数据库迁移脚本

2. **backend/tests/test_review_system.py**
   - 功能测试脚本

3. **docs/REVIEW_SYSTEM.md**
   - 功能文档（本文件）

## 使用场景

### 场景 1：新数据录入后审核

1. 用户手动录入或通过 Excel 导入新数据
2. 新记录默认状态为"待审核"
3. 审核员在"数据审核"标签页查看待审核记录
4. 审核员逐条或批量审核记录
5. 审核通过后记录自动标记为"已验证"

### 场景 2：数据质量检查

1. 定期查看待审核记录列表
2. 对数据完整性、准确性进行检查
3. 通过记录添加正面评价
4. 拒绝记录时说明原因，便于改进

### 场景 3：审核追溯

1. 查看单条记录的审核历史
2. 了解谁在何时做了什么审核决定
3. 查看审核意见，理解决策依据
4. 必要时可重新审核

## 注意事项

1. **权限管理**: 确保审核员拥有 `review_records` 权限
2. **审核意见**: 建议在拒绝时填写具体原因，便于数据改进
3. **批量操作**: 批量审核前请仔细检查选中的记录
4. **审核日志**: 所有审核操作都会记录，无法删除，确保可追溯

## 后续优化建议

1. 审核状态变更通知（邮件/消息）
2. 审核统计报表（审核数量、通过率等）
3. 审核撤回功能（允许撤销误操作）
4. 多级审核流程（初审、复审）
5. 审核规则自动化（符合特定条件自动通过）

---

**完成时间**: 2026-03-20  
**负责人**: Agent-15  
**版本**: v1.0
