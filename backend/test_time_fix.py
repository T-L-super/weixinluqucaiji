import sqlite3
from datetime import datetime

# 测试1: 使用默认连接（UTC时间）
print("测试1: 默认连接（UTC时间）")
conn1 = sqlite3.connect('data/admission_system.db')
cursor1 = conn1.cursor()
cursor1.execute("SELECT CURRENT_TIMESTAMP")
utc_time = cursor1.fetchone()[0]
print(f"CURRENT_TIMESTAMP (UTC): {utc_time}")
conn1.close()

# 测试2: 设置时区后（本地时间）
print("\n测试2: 设置时区后（本地时间）")
conn2 = sqlite3.connect('data/admission_system.db')
cursor2 = conn2.cursor()
cursor2.execute("PRAGMA timezone = 'localtime'")
cursor2.execute("SELECT CURRENT_TIMESTAMP")
local_time = cursor2.fetchone()[0]
print(f"CURRENT_TIMESTAMP (本地时间): {local_time}")

# 测试3: 当前系统时间
print(f"\n测试3: 当前系统时间")
print(f"系统本地时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 测试4: 插入一条记录并验证时间
print("\n测试4: 插入记录并验证时间")
cursor2.execute("""
    INSERT INTO admission_records (student_name_cn, university_cn, country, data_source, admission_year, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
""", ["时间测试2", "时间大学2", "中国", "时间公众号2", 2024])
conn2.commit()

# 查询刚插入的记录
cursor2.execute("SELECT id, student_name_cn, created_at FROM admission_records WHERE student_name_cn = '时间测试2'")
row = cursor2.fetchone()
print(f"插入的记录时间: {row[2]}")

conn2.close()

print("\n✓ 时间修复测试完成！")
print(f"UTC时间: {utc_time}")
print(f"本地时间: {local_time}")
print(f"两者相差约8小时（北京时区）")