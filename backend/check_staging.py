import sqlite3

conn = sqlite3.connect('data/admission_system.db')
cursor = conn.cursor()

# 检查 staging 表结构
cursor.execute("PRAGMA table_info(admission_records_staging)")
columns = cursor.fetchall()
print("admission_records_staging 表结构:")
for col in columns:
    print(f"  {col[1]}: {col[2]}")

# 检查是否有 data_source 字段
has_data_source = any(col[1] == 'data_source' for col in columns)
print(f"\n是否有 data_source 字段: {has_data_source}")

# 查看最近的 staging 记录
cursor.execute("SELECT id, student_name_cn, data_source, created_at FROM admission_records_staging ORDER BY id DESC LIMIT 3")
print("\n最近3条 staging 记录:")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, 姓名: {row[1]}, 数据来源: '{row[2]}', 创建时间: {row[3]}")

conn.close()