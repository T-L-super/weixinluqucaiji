# 数据审核功能快速启动指南

## 快速开始（3 步启用）

### 步骤 1: 数据库迁移

```bash
cd /root/.openclaw/workspace/大学录取信息整理系统/backend
python3 migrations/add_review_system.py
```

预期输出：
```
✅ 添加字段：review_status
✅ 添加字段：reviewed_at
✅ 添加字段：reviewed_by
✅ 添加字段：review_comment
✅ 创建表：review_logs
✅ 创建审核日志索引
🎉 数据库迁移完成！
```

### 步骤 2: 重启后端服务

如果服务已在运行，先停止（Ctrl+C），然后重新启动：

```bash
cd /root/.openclaw/workspace/大学录取信息整理系统/backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 步骤 3: 访问审核界面

1. 打开浏览器访问：`http://localhost:8000`
2. 登录系统（默认账号：admin / admin123）
3. 点击顶部导航栏的 **"🔍 数据审核"** 标签
4. 开始审核数据！

## 功能验证清单

### ✅ 基础功能验证

- [ ] 能够看到"数据审核"标签页
- [ ] 能够查看待审核记录列表
- [ ] 能够对单条记录执行"通过"操作
- [ ] 能够对单条记录执行"拒绝"操作
- [ ] 能够填写审核意见
- [ ] 能够查看审核历史

### ✅ 批量操作验证

- [ ] 能够勾选多条记录
- [ ] 能够执行批量通过
- [ ] 能够执行批量拒绝
- [ ] 批量操作后列表自动刷新

### ✅ 权限验证

- [ ] 管理员账号可以看到审核标签
- [ ] 普通用户账号（无审核权限）看不到审核标签

## 常见问题排查

### 问题 1: 看不到"数据审核"标签

**原因**: 当前用户没有审核权限

**解决方案**:
1. 使用管理员账号登录（admin / admin123）
2. 或为用户分配 `review_records` 权限

### 问题 2: 审核操作失败（403 错误）

**原因**: Token 过期或权限不足

**解决方案**:
1. 重新登录获取新 token
2. 检查用户权限配置

### 问题 3: 数据库字段不存在

**原因**: 未执行数据库迁移

**解决方案**:
```bash
python3 migrations/add_review_system.py
```

### 问题 4: 待审核列表为空

**原因**: 所有记录都已审核

**解决方案**:
1. 这是正常状态，显示"✅ 没有待审核的记录"
2. 新录入的数据会自动进入待审核状态
3. 或手动修改现有记录状态为 pending：
   ```sql
   UPDATE admission_records SET review_status = 'pending' WHERE id = 1;
   ```

## API 测试示例

使用 curl 测试审核 API：

```bash
# 1. 登录获取 token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# 2. 获取待审核列表
curl -s "http://localhost:8000/api/records/pending-review" \
  -H "Authorization: Bearer $TOKEN" | jq

# 3. 审核通过单条记录
curl -s -X POST "http://localhost:8000/api/records/1/approve" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"comment":"测试审核通过"}' | jq

# 4. 查看审核日志
curl -s "http://localhost:8000/api/records/review-logs?limit=10" \
  -H "Authorization: Bearer $TOKEN" | jq
```

## 下一步

完成快速启动后，建议：

1. 📖 阅读完整功能文档：`docs/REVIEW_SYSTEM.md`
2. 🧪 运行自动化测试：`python3 tests/test_review_system.py`
3. 👥 为用户分配审核权限
4. 📊 开始实际审核工作

---

**技术支持**: 如有问题，请查看系统日志或联系开发团队
