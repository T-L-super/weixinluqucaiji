import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_path = os.path.join(os.path.dirname(__file__), 'data', 'admission_system.db')

conn = sqlite3.connect(db_path)
c = conn.cursor()

print("暂存表中的所有数据：\n")
c.execute("SELECT id, student_name_cn, university_cn, country FROM admission_records_staging")
rows = c.fetchall()

print(f"共 {len(rows)} 条记录：\n")
for row in rows:
    print(f"  ID: {row[0]}")
    print(f"    姓名: '{row[1]}'")
    print(f"    大学: {row[2]}")
    print(f"    国家: {row[3]}")
    print()

conn.close()
