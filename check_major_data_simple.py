import sqlite3
import os

DB_PATH = r'd:\大学录取信息整理系统\backend\data\admission_system.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 80)
print("检查专业数据提取和显示情况")
print("=" * 80)

cursor.execute("SELECT id, student_name_cn, university_cn, major_cn, major_en, article_url, article_title FROM admission_records ORDER BY id DESC LIMIT 10")
rows = cursor.fetchall()

print("\n最近10条录取记录：")
print(f"{'ID':<6} {'姓名':<12} {'大学':<20} {'专业(中)':<15} {'专业(英)':<15}")
print("-" * 80)

for row in rows:
    id_, name, uni, major_cn, major_en, url, title = row
    print(f"{id_:<6} {name[:12]:<12} {uni[:20]:<20} {major_cn[:15] if major_cn else '-':<15} {major_en[:15] if major_en else '-':<15}")

print("\n" + "=" * 80)

cursor.execute("SELECT COUNT(*) FROM admission_records WHERE major_cn IS NOT NULL AND major_cn != ''")
count_with_major = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM admission_records")
total_count = cursor.fetchone()[0]

print(f"总计 {count_with_major}/{total_count} 条记录有专业数据 ({(count_with_major/total_count*100):.1f}%)")

conn.close()
