import sqlite3

conn = sqlite3.connect('data/admission_system.db')
cursor = conn.cursor()

# 检查 source_data 字段是否已存在
cursor.execute("PRAGMA table_info(admission_records)")
columns = [col[1] for col in cursor.fetchall()]

if 'source_data' not in columns:
    # 添加 source_data 字段
    cursor.execute("ALTER TABLE admission_records ADD COLUMN source_data TEXT")
    
    # 如果有 source_school 数据，迁移到 source_data
    if 'source_school' in columns:
        cursor.execute("UPDATE admission_records SET source_data = source_school WHERE source_school IS NOT NULL AND source_school != ''")
    
    conn.commit()
    print("已添加 source_data 字段并迁移数据")
else:
    print("source_data 字段已存在")

# 查看结果
cursor.execute("PRAGMA table_info(admission_records)")
print("\n当前表结构:")
for col in cursor.fetchall():
    print(col)

conn.close()