import sqlite3
import os

DB_PATH = r'd:\大学录取信息整理系统\backend\data\admission_system.db'

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute('SELECT id, extracted_count, recognition_model FROM collection_tasks WHERE id = (SELECT MAX(id) FROM collection_tasks)')
row = c.fetchone()
print(f'最新任务: ID={row[0]}, 提取数={row[1]}, 模型={row[2]}')

c.execute('SELECT COUNT(*) FROM admission_records_staging WHERE article_url LIKE ?', ('%0-MWT6oyIOZqJpCFCR_I2g%',))
print(f'暂存表记录: {c.fetchone()[0]}')

conn.close()
