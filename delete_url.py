import sqlite3

db_path = r'd:\大学录取信息整理系统\backend\data\admission_system.db'
url = 'https://mp.weixin.qq.com/s/tSldUp3cvZPP_zb2ejdyWg'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('DELETE FROM collection_tasks WHERE article_url = ?', (url,))
tasks_deleted = cursor.rowcount

cursor.execute('DELETE FROM admission_records_staging WHERE article_url = ?', (url,))
staging_deleted = cursor.rowcount

cursor.execute('DELETE FROM admission_records WHERE article_url = ?', (url,))
records_deleted = cursor.rowcount

conn.commit()
conn.close()

print(f'Tasks: {tasks_deleted}, Staging: {staging_deleted}, Records: {records_deleted}')
