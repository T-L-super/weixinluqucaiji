import sqlite3

conn = sqlite3.connect('data/admission_system.db')
cursor = conn.cursor()

# 查看当前数据
cursor.execute("SELECT id, student_name_cn, university_cn, data_source FROM admission_records LIMIT 10")
print("当前记录:")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, 姓名: {row[1]}, 大学: {row[2]}, 数据来源: '{row[3]}'")

# 插入测试数据
test_data = {
    'student_name_cn': '测试学生',
    'university_cn': '测试大学',
    'country': '中国',
    'data_source': '测试公众号',
    'admission_year': 2024
}

cursor.execute("""
    INSERT INTO admission_records (student_name_cn, university_cn, country, data_source, admission_year)
    VALUES (?, ?, ?, ?, ?)
""", [test_data['student_name_cn'], test_data['university_cn'], test_data['country'], 
      test_data['data_source'], test_data['admission_year']])
conn.commit()

print("\n插入测试数据成功！")

# 验证插入
cursor.execute("SELECT id, student_name_cn, university_cn, data_source FROM admission_records WHERE student_name_cn = '测试学生'")
row = cursor.fetchone()
print(f"验证结果 - ID: {row[0]}, 姓名: {row[1]}, 大学: {row[2]}, 数据来源: '{row[3]}'")

conn.close()