import sqlite3

conn = sqlite3.connect('data/admission_system.db')
cursor = conn.cursor()

# 统计记录数
cursor.execute('SELECT COUNT(*) FROM admission_records')
print('Total records:', cursor.fetchone()[0])

# 统计有数据来源的记录数
cursor.execute("SELECT COUNT(*) FROM admission_records WHERE source_school IS NOT NULL AND source_school != ''")
print('Records with source_school:', cursor.fetchone()[0])

# 查看前5条记录的数据来源
cursor.execute("SELECT id, student_name_cn, university_cn, source_school FROM admission_records LIMIT 10")
print('\nFirst 10 records:')
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Name: {row[1]}, University: {row[2]}, Source: '{row[3]}'")

conn.close()