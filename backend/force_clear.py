import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_path = os.path.join(os.path.dirname(__file__), 'data', 'admission_system.db')

conn = sqlite3.connect(db_path)
c = conn.cursor()

print("开始清空数据...\n")

tables_to_clear = [
    'admission_records_staging',
    'admission_records',
    'collection_tasks',
    'ai_rejected_log',
    'review_history',
    'review_history_new'
]

for table in tables_to_clear:
    try:
        c.execute(f"SELECT COUNT(*) FROM {table}")
        before_count = c.fetchone()[0]
        
        c.execute(f"DELETE FROM {table}")
        
        c.execute(f"SELECT COUNT(*) FROM {table}")
        after_count = c.fetchone()[0]
        
        status = "OK" if after_count == 0 else "FAIL"
        print(f"[{status}] {table}: {before_count} -> {after_count}")
    except Exception as e:
        print(f"[ERROR] {table}: {e}")

conn.commit()

print("\n最终验证：")
for table in tables_to_clear:
    try:
        c.execute(f"SELECT COUNT(*) FROM {table}")
        count = c.fetchone()[0]
        status = "CLEAN" if count == 0 else "HAS DATA"
        print(f"  [{status}] {table}: {count}")
    except:
        pass

conn.close()
print("\n数据清空完成！")
