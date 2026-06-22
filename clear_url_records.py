import sqlite3
import os

DB_PATH = r'd:\大学录取信息整理系统\backend\data\admission_system.db'
URL_KEYWORD = 'Z10iL5ZpGpEEPs_YZEABpg'

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# 1. 查找相关任务ID
c.execute('SELECT id FROM collection_tasks WHERE article_url LIKE ?', (f'%{URL_KEYWORD}%',))
task_ids = [row[0] for row in c.fetchall()]
print(f'找到任务ID: {task_ids}')

if task_ids:
    # 2. 删除暂存表中相关的记录
    c.execute('DELETE FROM admission_records_staging WHERE article_url LIKE ?', (f'%{URL_KEYWORD}%',))
    print(f'已删除暂存表记录')
    
    # 3. 删除相关任务
    c.execute('DELETE FROM collection_tasks WHERE id IN ({})'.format(','.join(['?']*len(task_ids))), task_ids)
    print(f'已删除 {len(task_ids)} 个任务')
    
    conn.commit()
    print('清理完成！')
else:
    print('未找到相关任务')

conn.close()
