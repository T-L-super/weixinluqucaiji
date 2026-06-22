import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'backend', 'data', 'admission_system.db')
print(f"数据库路径: {db_path}")

conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in c.fetchall()]
print(f"数据库中的所有表: {tables}")

tables_to_clear = [
    'admission_records_staging',
    'admission_records',
    'collection_tasks',
    '_task_queue',
    '_seen_urls'
]

for table in tables_to_clear:
    if table in tables:
        c.execute(f"DELETE FROM {table}")
        count = c.execute("SELECT changes()").fetchone()[0]
        print(f"已清空 {table}，删除了 {count} 条记录")
    else:
        print(f"表 {table} 不存在")

conn.commit()
conn.close()
print("\n数据清空完成！可以重新采集了。")