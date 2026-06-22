import sqlite3
import os

db_path = os.path.join('data', 'admission_system.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print('=== 检查 URL: https://mp.weixin.qq.com/s/Z10iL5ZpGpEEPs_YZEABpg ===')

cursor.execute('SELECT * FROM collection_tasks WHERE article_url LIKE ?', ('%Z10iL5ZpGpEEPs_YZEABpg%',))
rows = cursor.fetchall()
print('\n【任务记录】')
if rows:
    for row in rows:
        print(f"ID: {row[0]}, 状态: {row[5]}, 提取记录数: {row[8]}, 错误: {row[7]}")
else:
    print('未找到任务记录')

cursor.execute('SELECT * FROM admission_records_staging WHERE article_url LIKE ?', ('%Z10iL5ZpGpEEPs_YZEABpg%',))
rows = cursor.fetchall()
print('\n【暂存记录】')
if rows:
    for row in rows:
        print(f"ID: {row[0]}, 姓名: {row[1]}, 大学: {row[4]}")
else:
    print('未找到暂存记录')

cursor.execute('SELECT * FROM admission_records WHERE article_url LIKE ?', ('%Z10iL5ZpGpEEPs_YZEABpg%',))
rows = cursor.fetchall()
print('\n【主表记录】')
if rows:
    for row in rows:
        print(f"ID: {row[0]}, 姓名: {row[1]}, 大学: {row[4]}")
else:
    print('未找到主表记录')

conn.close()
