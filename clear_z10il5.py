import sqlite3

DB_PATH = r'd:\大学录取信息整理系统\backend\data\admission_system.db'
URL_KEYWORD = 'Z10iL5ZpGpEEPs_YZEABpg'

print(f'正在清理包含 "{URL_KEYWORD}" 的记录...')

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# 删除暂存表记录
c.execute('DELETE FROM admission_records_staging WHERE article_url LIKE ?', (f'%{URL_KEYWORD}%',))
print(f'已删除暂存表记录: {c.rowcount} 条')

# 删除任务
c.execute('DELETE FROM collection_tasks WHERE article_url LIKE ?', (f'%{URL_KEYWORD}%',))
print(f'已删除任务: {c.rowcount} 个')

conn.commit()
conn.close()

print('清理完成！')
