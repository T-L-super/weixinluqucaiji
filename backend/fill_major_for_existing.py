import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(os.path.dirname(__file__), "data/admission_system.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 80)
print("检查现有记录的专业数据情况")
print("=" * 80)

cursor.execute("SELECT COUNT(*) FROM admission_records WHERE major_cn IS NULL OR major_cn = ''")
count_empty = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM admission_records")
total = cursor.fetchone()[0]

print(f"\n需要补全专业的记录数: {count_empty}/{total}")

cursor.execute("SELECT id, student_name_cn, university_cn, major_cn, article_title FROM admission_records ORDER BY id DESC LIMIT 10")
rows = cursor.fetchall()

print("\n最近10条记录：")
print(f"{'ID':<6} {'姓名':<12} {'大学':<20} {'专业':<15}")
print("-" * 80)

for row in rows:
    id_, name, uni, major, title = row
    print(f"{id_:<6} {name[:12]:<12} {uni[:20]:<20} {major[:15] if major else '-':<15}")

conn.close()

print("\n" + "=" * 80)
print("注意：现有数据的专业字段为空是因为这些数据是之前采集的")
print("新的专业提取逻辑只对新采集的数据生效")
print("要为现有数据补全专业，需要重新采集或批量处理")
print("=" * 80)
