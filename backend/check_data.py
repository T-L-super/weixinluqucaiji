import sqlite3

conn = sqlite3.connect('data/admission_system.db')
cursor = conn.cursor()

# 查看记录数
cursor.execute("SELECT COUNT(*) FROM admission_records")
count = cursor.fetchone()[0]
print(f"总记录数: {count}")

# 查看最近的记录
cursor.execute("SELECT id, student_name_cn, data_source, created_at FROM admission_records ORDER BY id DESC LIMIT 5")
print("\n最近5条记录:")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, 姓名: {row[1]}, 数据来源: '{row[2]}', 创建时间: {row[3]}")

conn.close()