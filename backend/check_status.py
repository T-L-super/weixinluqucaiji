import pymysql

conn = pymysql.connect(
    host='10.9.8.120', port=3306, user='python',
    password='YLcXkLEcYAihBitr', database='python',
    charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)
c = conn.cursor()

sm = {0:'待处理',2:'处理中',3:'已完成',4:'失败',5:'已终止'}
print("任务状态分布:")
c.execute("SELECT task_status, COUNT(*) as cnt FROM collection_tasks GROUP BY task_status ORDER BY task_status")
for r in c.fetchall():
    print(f"  status={r['task_status']} ({sm.get(r['task_status'],'?')}): {r['cnt']}")

print("\n最近完成的任务:")
c.execute("SELECT id, title, extracted_count, completed_at FROM collection_tasks WHERE task_status = 3 ORDER BY completed_at DESC LIMIT 5")
for d in c.fetchall():
    print(f"  ID={d['id']} | {d['title'][:30] if d['title'] else 'N/A'} | extracted={d['extracted_count']} | at={d['completed_at']}")

conn.close()
