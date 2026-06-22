import sqlite3

conn = sqlite3.connect('data/admission_system.db')
c = conn.cursor()

# 获取所有表名
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in c.fetchall()]
print(f"数据库中的表: {tables}")

# 清空数据
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
        print(f"已清空 {table}")
    else:
        print(f"表 {table} 不存在")

conn.commit()
conn.close()
print("数据清空完成！")
