# 手动录入功能使用指南

## 功能概述

手动录入功能允许管理员通过 Web 界面直接添加录取记录，支持单条录入和批量录入两种模式。

## 访问方式

1. 启动后端服务：
```bash
cd /root/.openclaw/workspace/大学录取信息整理系统/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8765
```

2. 在浏览器中访问：`http://localhost:8765`

3. 点击顶部导航栏的 **"➕ 手动录入"** 按钮

## 单条录入

### 必填字段
- **学生姓名**：学生的中文姓名
- **录取大学**：录取的大学名称（支持自动创建）
- **国家**：大学所在国家（支持自动创建）

### 可选字段
- 英文名
- 专业 / 专业英文
- GPA（0-4.0）
- TOEFL（0-120）
- IELTS（0-9.0）
- SAT（400-1600）
- GRE（130-340）
- 奖学金信息 / 奖学金金额
- 学位（本科/硕士/博士）
- 申请年份 / 入学年份
- 来源学校
- 文章来源 URL
- 录取条件 / 作品集
- 已验证（复选框）

### 操作步骤
1. 点击"➕ 手动录入"按钮
2. 确保在"单条录入"标签页
3. 填写必填字段和需要的可选字段
4. 点击"提交录入"
5. 系统会自动创建不存在的国家和大学
6. 录入成功后自动刷新列表

## 批量录入

### 数据格式
支持 JSON 格式批量导入，示例：

```json
[
  {
    "student_name": "张三",
    "student_name_en": "San Zhang",
    "university": "University of California, Berkeley",
    "country": "美国",
    "major": "Computer Science",
    "gpa": 3.8,
    "toefl": 105,
    "is_verified": true
  },
  {
    "student_name": "李四",
    "university": "Stanford University",
    "country": "美国",
    "major": "Economics",
    "gpa": 3.9
  }
]
```

### 必填字段（每条记录）
- `student_name`: 学生姓名
- `university`: 录取大学
- `country`: 国家

### 可选字段
- `student_name_en`: 英文名
- `major`: 专业
- `major_en`: 专业英文
- `gpa`: GPA
- `toefl`: TOEFL 成绩
- `ielts`: IELTS 成绩
- `sat`: SAT 成绩
- `act`: ACT 成绩
- `gre`: GRE 成绩
- `gmat`: GMAT 成绩
- `scholarship`: 奖学金信息
- `scholarship_amount`: 奖学金金额
- `degree`: 学位
- `application_year`: 申请年份
- `admission_year`: 入学年份
- `source_school`: 来源学校
- `article_url`: 文章来源 URL
- `requirements`: 录取条件
- `portfolio`: 作品集
- `is_verified`: 是否已验证（true/false）

### 操作步骤
1. 点击"➕ 手动录入"按钮
2. 切换到"批量录入"标签页
3. 在文本框中粘贴 JSON 数据
4. 点击"批量提交"
5. 系统会显示成功和跳过的记录数

## API 端点

### 单条录入
```
POST /api/records/manual-entry
Content-Type: application/json

{
  "student_name": "张三",
  "university": "UC Berkeley",
  "country": "美国",
  ...
}
```

### 批量录入
```
POST /api/records/manual-entry/batch
Content-Type: application/json

{
  "records": [...]
}
```

### 辅助 API
- `GET /api/countries` - 获取国家列表
- `GET /api/universities?limit=500` - 获取大学列表
- `GET /api/source-schools` - 获取来源学校列表
- `POST /api/countries` - 创建新国家
- `POST /api/universities` - 创建新大学
- `POST /api/source-schools` - 创建新来源学校

## 数据验证

系统会自动进行以下验证：
- 必填字段检查
- 数值范围验证（GPA 0-4.0，TOEFL 0-120 等）
- 重复记录检测（学生 + 大学 + 年份）
- 自动创建不存在的国家/大学/来源学校

## 注意事项

1. **批量录入限制**：单次最多支持 100 条记录
2. **数据去重**：如果记录已存在（学生姓名 + 大学 + 年份相同），会跳过该记录
3. **错误处理**：批量录入时，单条记录失败不会影响其他记录
4. **自动关联**：国家和大学会自动创建并缓存，方便后续录入

## 故障排查

### 问题：录入失败，提示"数据冲突"
**原因**：记录已存在（学生姓名 + 大学 + 年份重复）
**解决**：检查是否已录入相同记录，或使用更新功能

### 问题：下拉列表为空
**原因**：首次使用，还没有任何数据
**解决**：直接输入文本即可，系统会自动创建

### 问题：批量录入部分失败
**原因**：某些记录缺少必填字段或格式错误
**解决**：查看返回的错误信息，修正后重新提交
