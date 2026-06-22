import sqlite3

DB_PATH = r'd:\大学录取信息整理系统\backend\data\admission_system.db'
URL_KEYWORD = '0-MWT6oyIOZqJpCFCR_I2g'

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# 查询采集任务
print('='*80)
print('采集任务信息')
print('='*80)
c.execute('SELECT id, article_url, title, task_status, extracted_count, recognition_model FROM collection_tasks WHERE article_url LIKE ?', (f'%{URL_KEYWORD}%',))
tasks = c.fetchall()
for task in tasks:
    print(f"任务ID: {task['id']}")
    print(f"URL: {task['article_url'][:80]}...")
    print(f"标题: {task['title']}")
    print(f"状态: {task['task_status']}")
    print(f"提取记录数: {task['extracted_count']}")
    print(f"识别模型: {task['recognition_model']}")
    print()

if tasks:
    task_id = tasks[0]['id']
    
    # 查询暂存表记录
    print('='*80)
    print(f'暂存表记录 (任务ID: {task_id})')
    print('='*80)
    c.execute('SELECT id, student_name_cn, university_cn, major_cn, country, source_school, review_status, article_url FROM admission_records_staging WHERE article_url LIKE ?', (f'%{URL_KEYWORD}%',))
    staging_records = c.fetchall()
    print(f'暂存表记录数: {len(staging_records)}')
    print()
    for i, rec in enumerate(staging_records, 1):
        print(f"{i}. ID={rec['id']}, 学生={rec['student_name_cn']}, 大学={rec['university_cn']}, 专业={rec['major_cn']}, 国家={rec['country']}, 审核状态={rec['review_status']}")
    
    print()
    print('='*80)
    print('按审核状态统计')
    print('='*80)
    c.execute('SELECT review_status, COUNT(*) as count FROM admission_records_staging WHERE article_url LIKE ? GROUP BY review_status', (f'%{URL_KEYWORD}%',))
    status_counts = c.fetchall()
    for sc in status_counts:
        print(f"状态: {sc['review_status']}, 数量: {sc['count']}")
    
    print()
    print('='*80)
    print('AI拒绝记录')
    print('='*80)
    c.execute('SELECT id, student_name_cn, university_cn, major_cn, country, reject_reason FROM ai_rejected_log WHERE article_url LIKE ?', (f'%{URL_KEYWORD}%',))
    rejected = c.fetchall()
    print(f'AI拒绝记录数: {len(rejected)}')
    print()
    for i, rec in enumerate(rejected, 1):
        print(f"{i}. 学生={rec['student_name_cn']}, 大学={rec['university_cn']}, 专业={rec['major_cn']}, 拒绝原因={rec['reject_reason']}")

conn.close()
