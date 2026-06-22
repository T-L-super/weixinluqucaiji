import sqlite3
from datetime import datetime

conn = sqlite3.connect('data/admission_system.db')
cursor = conn.cursor()

# 查看时间字段
cursor.execute("SELECT id, student_name_cn, created_at, updated_at FROM admission_records ORDER BY id DESC LIMIT 5")
print("数据库中的时间数据:")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, 姓名: {row[1]}, 创建时间: {row[2]}, 更新时间: {row[3]}")

# 查看当前系统时间
print(f"\n当前本地时间: {datetime.now()}")
print(f"当前UTC时间: {datetime.utcnow()}")

conn.close()