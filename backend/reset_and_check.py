import pymysql

conn = pymysql.connect(
    host='10.9.8.120', port=3306, user='python',
    password='YLcXkLEcYAihBitr', database='python',
    charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)
c = conn.cursor()

# Reset task 256 to pending
c.execute("UPDATE collection_tasks SET task_status = 0, started_at = NULL, error_message = '手动重置' WHERE id = 256")
conn.commit()
print("Task 256 reset to pending")

# Show overall status
c.execute("SELECT task_status, COUNT(*) as cnt FROM collection_tasks GROUP BY task_status ORDER BY task_status")
sm = {0:'待处理',2:'处理中',3:'已完成',4:'失败',5:'已终止'}
for r in c.fetchall():
    print(f"  status={r['task_status']} ({sm.get(r['task_status'],'?')}): {r['cnt']}")

conn.close()
