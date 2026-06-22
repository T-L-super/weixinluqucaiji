import sqlite3
from datetime import datetime, timezone

conn = sqlite3.connect('data/admission_system.db')
cursor = conn.cursor()

# 设置 SQLite 使用本地时间
cursor.execute("PRAGMA timezone = 'localtime'")
conn.commit()

print("已设置 SQLite 使用本地时间")

# 测试插入一条新记录
test_data = {
    'student_name_cn': '时间测试',
    'university_cn': '时间大学',
    'country': '中国',
    'data_source': '时间测试公众号',
    'admission_year': 2024
}

# 使用 Python 的本地时间
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

cursor.execute("""
    INSERT INTO admission_records (student_name_cn, university_cn, country, data_source, admission_year, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", [test_data['student_name_cn'], test_data['university_cn'], test_data['country'], 
      test_data['data_source'], test_data['admission_year'], now, now])
conn.commit()

print(f"插入时间: {now}")

# 验证结果
cursor.execute("SELECT id, student_name_cn, created_at, updated_at FROM admission_records WHERE student_name_cn = '时间测试'")
row = cursor.fetchone()
print(f"数据库时间: {row[2]}")

conn.close()