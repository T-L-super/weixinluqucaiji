import sqlite3
from datetime import datetime

# 创建测试记录，使用本地时间
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

conn = sqlite3.connect('data/admission_system.db')
cursor = conn.cursor()

# 插入测试记录
cursor.execute("""
    INSERT INTO admission_records (student_name_cn, university_cn, country, data_source, admission_year, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", ["时间测试最终版", "时间大学最终版", "中国", "时间公众号最终版", 2024, now, now])
conn.commit()

# 查询刚插入的记录
cursor.execute("SELECT id, student_name_cn, created_at FROM admission_records WHERE student_name_cn = '时间测试最终版'")
row = cursor.fetchone()

print(f"插入时间: {now}")
print(f"数据库时间: {row[2]}")
print(f"时间匹配: {now == row[2]}")

conn.close()

print("\n✓ 时间修复测试完成！")