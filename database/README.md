# 🎓 大学录取信息整理系统 - 数据库使用说明

> **完成时间：** 2026-03-18 23:22 UTC  
> **数据库类型：** SQLite 3.x  
> **表数量：** 7 张核心表  
> **测试数据：** 55 条录取记录 + 配套数据

---

## 📁 文件结构

```
database/
├── init_db.py          # 数据库初始化脚本（Python）
├── schema.sql          # 完整 SQL 建表语句
├── sample_data.sql     # 测试数据（50+ 条记录）
└── README.md           # 本说明文档
```

---

## 🚀 快速开始

### 方法一：使用 Python 脚本（推荐）

```bash
# 进入数据库目录
cd /root/.openclaw/workspace/大学录取信息整理系统/database

# 运行初始化脚本
python3 init_db.py
```

脚本将自动完成：
1. 创建/重置数据库文件 `admission_system.db`
2. 执行建表语句（7 张表 + 索引 + 视图 + 触发器）
3. 插入测试数据（55 条录取记录 + 配套数据）
4. 验证数据库完整性
5. 显示示例查询

### 方法二：手动执行 SQL

```bash
# 使用 sqlite3 命令行
sqlite3 admission_system.db

# 在 SQLite 提示符中执行
.read schema.sql
.read sample_data.sql
```

---

## 📊 数据库结构

### 核心表说明

| 表名 | 说明 | 记录数 |
|------|------|--------|
| `admission_records` | 录取记录表（核心） | 55 |
| `collection_tasks` | 采集任务队列 | 10 |
| `countries` | 国家/地区表 | 8 |
| `universities` | 大学信息表 | 20 |
| `source_schools` | 来源学校表 | 15 |
| `admission_requirements` | 录取条件详情 | 20 |
| `statistics_daily` | 每日统计表 | 5 |

### ER 关系图

```
countries (1) ──< admission_records (N) >── universities (1)
                          │
                          │
                    source_schools (1)
                          │
                          │
                    admission_requirements (0..1)
```

---

## 🔍 常用查询示例

### 1. 查询所有录取记录

```sql
SELECT 
    student_name_cn,
    university_cn,
    major_cn,
    country,
    admission_year,
    scholarship_amount
FROM admission_records
ORDER BY admission_year DESC, created_at DESC
LIMIT 20;
```

### 2. 按国家统计录取数量

```sql
SELECT 
    country,
    COUNT(*) as total_records,
    COUNT(DISTINCT university_cn) as unique_universities,
    AVG(scholarship_amount) as avg_scholarship
FROM admission_records
WHERE status = 1
GROUP BY country
ORDER BY total_records DESC;
```

### 3. 查询奖学金记录

```sql
SELECT 
    student_name_cn,
    university_cn,
    major_cn,
    scholarship_amount,
    scholarship_currency,
    scholarship_type
FROM admission_records
WHERE scholarship_amount > 0
ORDER BY scholarship_amount DESC;
```

### 4. 查询待处理采集任务

```sql
SELECT 
    id,
    article_url,
    source_school_name,
    priority,
    task_status,
    scheduled_at
FROM collection_tasks
WHERE task_status = 0
ORDER BY priority DESC, created_at ASC;
```

### 5. 使用完整视图查询

```sql
SELECT 
    student_name_cn,
    university_cn,
    major_cn,
    country,
    continent,
    ranking_us_news,
    scholarship_amount
FROM v_admission_records_full
WHERE admission_year = 2026
ORDER BY university_ranking ASC
LIMIT 20;
```

### 6. 按大学统计

```sql
SELECT 
    university_cn,
    country,
    COUNT(*) as total_records,
    COUNT(DISTINCT student_name_cn) as unique_students,
    AVG(scholarship_amount) as avg_scholarship
FROM admission_records
WHERE status = 1
GROUP BY university_cn, country
HAVING COUNT(*) >= 2
ORDER BY total_records DESC;
```

### 7. 按年份统计趋势

```sql
SELECT 
    admission_year,
    COUNT(*) as total_records,
    COUNT(DISTINCT country) as countries_count,
    COUNT(DISTINCT university_cn) as universities_count,
    ROUND(AVG(scholarship_amount), 2) as avg_scholarship
FROM admission_records
WHERE status = 1
GROUP BY admission_year
ORDER BY admission_year DESC;
```

---

## 📈 视图说明

### v_admission_records_full
录取记录完整视图，关联大学、来源学校、国家信息。

**字段：** 包含 admission_records 所有字段 + 大学详情 + 学校城市 + 大洲信息

### v_stats_by_country
按国家统计视图。

**字段：** country, total_records, unique_universities, unique_students, avg_scholarship

### v_stats_by_university
按大学统计视图。

**字段：** university_cn, university_en, country, total_records, unique_students, avg_scholarship

### v_stats_by_year
按年份统计视图。

**字段：** admission_year, total_records, countries_count, universities_count, avg_scholarship

### v_pending_tasks
待处理任务视图。

**字段：** id, article_url, source_school_name, priority, task_status, scheduled_at

---

## 🔧 数据库配置

### 连接参数

```python
import sqlite3

# 数据库路径
DB_PATH = '/root/.openclaw/workspace/大学录取信息整理系统/database/admission_system.db'

# 获取连接
conn = sqlite3.connect(DB_PATH)
conn.execute('PRAGMA foreign_keys = ON')  # 启用外键
```

### 重要 PRAGMA 设置

```sql
-- 启用外键约束
PRAGMA foreign_keys = ON;

-- 检查外键完整性
PRAGMA foreign_key_check;

-- 优化查询性能
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 10000;
```

---

## 📝 数据字典

### admission_records 核心字段

| 字段 | 类型 | 说明 |
|------|------|------|
| student_name_cn | VARCHAR(100) | 学生姓名（中文） |
| university_cn | VARCHAR(200) | 大学名称（中文） |
| major_cn | VARCHAR(200) | 专业名称（中文） |
| country | VARCHAR(50) | 国家/地区 |
| admission_year | INTEGER | 录取年份 |
| scholarship_amount | DECIMAL(10,2) | 奖学金金额 |
| source_school | VARCHAR(200) | 来源学校 |
| article_url | VARCHAR(500) | 文章链接 |

### collection_tasks 状态码

| 值 | 说明 |
|----|------|
| 0 | 待处理 |
| 1 | 处理中 |
| 2 | 完成 |
| 3 | 失败 |

---

## ⚠️ 注意事项

1. **外键约束：** SQLite 默认不启用外键，连接后需执行 `PRAGMA foreign_keys = ON`
2. **字符编码：** 所有文本字段使用 UTF-8 编码
3. **日期格式：** 日期字段使用 `YYYY-MM-DD` 格式
4. **时间戳：** 使用 `DATETIME DEFAULT CURRENT_TIMESTAMP`
5. **数据质量：** `data_quality` 字段 1-5 分，5 分为最高质量

---

## 🛠️ 维护命令

### 检查数据库完整性

```sql
PRAGMA integrity_check;
```

### 检查外键约束

```sql
PRAGMA foreign_key_check;
```

### 查看表结构

```sql
.schema admission_records
```

### 查看索引

```sql
SELECT name, tbl_name FROM sqlite_master WHERE type='index';
```

### 优化数据库

```sql
VACUUM;
ANALYZE;
```

---

## 📞 技术支持

如有问题，请检查：
1. SQLite 版本（建议 3.35+）
2. 文件权限（确保可读写）
3. 磁盘空间（确保充足）
4. SQL 语法（SQLite 特有语法）

---

**最后更新：** 2026-03-18 23:22 UTC  
**文档版本：** v1.0
