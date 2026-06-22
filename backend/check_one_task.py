import pymysql

conn = pymysql.connect(
    host='10.9.8.120', port=3306, user='python',
    password='YLcXkLEcYAihBitr', database='python',
    charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)
c = conn.cursor()

print("Task 256 status:")
c.execute("SELECT id, task_status, started_at, completed_at, error_message, extracted_count FROM collection_tasks WHERE id = 256")
t = c.fetchone()
if t:
    sm = {0:'待处理',2:'处理中',3:'已完成',4:'失败',5:'已终止'}
    print(f"  status={t['task_status']} ({sm.get(t['task_status'],'?')})")
    print(f"  started={t['started_at']}")
    print(f"  completed={t['completed_at']}")
    print(f"  error={t['error_message']}")
    print(f"  extracted={t['extracted_count']}")

print()
print("Overall status:")
c.execute("SELECT task_status, COUNT(*) as cnt FROM collection_tasks GROUP BY task_status ORDER BY task_status")
for r in c.fetchall():
    print(f"  status={r['task_status']}: {r['cnt']}")

conn.close()
