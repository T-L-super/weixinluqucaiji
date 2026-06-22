import pymysql

conn = pymysql.connect(
    host='10.9.8.120', port=3306, user='python',
    password='YLcXkLEcYAihBitr', database='python',
    charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)
c = conn.cursor()

status_map = {0: '待处理', 1: '待处理(重试)', 2: '处理中', 3: '已完成', 4: '失败', 5: '已终止'}

print("=" * 60)
print("1. 任务状态分布")
print("=" * 60)
c.execute("SELECT task_status, COUNT(*) as cnt FROM collection_tasks GROUP BY task_status ORDER BY task_status")
for r in c.fetchall():
    label = status_map.get(r['task_status'], '未知')
    print(f"  状态{r['task_status']} ({label}): {r['cnt']}个")

print()
print("=" * 60)
print("2. 卡在执行中(status=2)的任务")
print("=" * 60)
c.execute("SELECT id, article_url, title, started_at, TIMESTAMPDIFF(MINUTE, started_at, NOW()) as stuck_min, error_message FROM collection_tasks WHERE task_status = 2 ORDER BY started_at")
stuck = c.fetchall()
if stuck:
    for s in stuck:
        print(f"  ID={s['id']} | 卡住{s['stuck_min']}分钟 | URL={s['article_url'][:60] if s['article_url'] else 'N/A'}...")
else:
    print("  无卡住任务")

print()
print("=" * 60)
print("3. 最近完成的任务(status=3)")
print("=" * 60)
c.execute("SELECT id, article_url, extracted_count, completed_at FROM collection_tasks WHERE task_status = 3 ORDER BY completed_at DESC LIMIT 5")
for d in c.fetchall():
    print(f"  ID={d['id']} | 提取{d['extracted_count']}条 | 完成于{d['completed_at']}")

print()
print("=" * 60)
print("4. 待处理任务(status=0) 前10个")
print("=" * 60)
c.execute("SELECT id, article_url, priority, created_at FROM collection_tasks WHERE task_status = 0 ORDER BY priority ASC, created_at ASC LIMIT 10")
for t in c.fetchall():
    print(f"  ID={t['id']} | P{t['priority']} | URL={t['article_url'][:60] if t['article_url'] else 'N/A'}...")

conn.close()
