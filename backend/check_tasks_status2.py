import pymysql

conn = pymysql.connect(
    host='10.9.8.120', port=3306, user='python',
    password='YLcXkLEcYAihBitr', database='python',
    charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)
c = conn.cursor()

print("=" * 60)
print("状态2任务详细信息")
print("=" * 60)
c.execute("SELECT id, article_url, task_status, retry_count, started_at, error_message, recognition_model FROM collection_tasks WHERE task_status = 2")
for t in c.fetchall():
    print(f"  ID={t['id']} | retry={t['retry_count']} | started={t['started_at']} | model={t['recognition_model']}")
    print(f"    URL={t['article_url'][:80] if t['article_url'] else 'N/A'}...")

print()
print("=" * 60)
print("检查MySQL中有哪些表")
print("=" * 60)
c.execute("SHOW TABLES")
for t in c.fetchall():
    print(f"  {list(t.values())[0]}")

conn.close()
