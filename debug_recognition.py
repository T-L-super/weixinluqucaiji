"""
调试识别流程
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'backend', 'data', 'admission_system.db')
URL_KEYWORD = '0-MWT6oyIOZqJpCFCR_I2g'

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# 查询任务配置
c.execute('''
    SELECT id, article_url, title, task_status, extracted_count, recognition_model, created_at 
    FROM collection_tasks 
    WHERE article_url LIKE ? 
    ORDER BY created_at DESC
''', (f'%{URL_KEYWORD}%',))

tasks = c.fetchall()

if not tasks:
    print(f'未找到包含关键词 "{URL_KEYWORD}" 的任务')
    conn.close()
    exit()

print('='*100)
print('采集任务详情')
print('='*100)

for task in tasks[:3]:
    print(f'\n任务ID: {task["id"]}')
    print(f'标题: {task["title"]}')
    print(f'状态: {task["task_status"]} (0=待处理, 2=处理中, 3=已完成, 4=失败)')
    print(f'提取数量: {task["extracted_count"]}')
    print(f'识别模型: {repr(task["recognition_model"])}')
    print(f'创建时间: {task["created_at"]}')

# 查询暂存表记录
print('\n' + '='*100)
print('暂存表记录')
print('='*100)
c.execute('''
    SELECT id, student_name_cn, university_cn, major_cn, country, review_status, article_url 
    FROM admission_records_staging 
    WHERE article_url LIKE ? 
    ORDER BY created_at DESC
''', (f'%{URL_KEYWORD}%',))

staging_records = c.fetchall()
print(f'暂存表记录数: {len(staging_records)}')

for rec in staging_records[:10]:
    print(f'\nID: {rec["id"]}')
    print(f'学生姓名: {repr(rec["student_name_cn"])}')
    print(f'大学: {repr(rec["university_cn"])}')
    print(f'专业: {repr(rec["major_cn"])}')
    print(f'国家: {repr(rec["country"])}')
    print(f'审核状态: {rec["review_status"]}')

conn.close()

print('\n' + '='*100)
print('问题分析')
print('='*100)

if tasks[0]['recognition_model'] is None:
    print('❌ 识别模型未配置！大模型识别不会执行')
else:
    print('✅ 识别模型已配置')

if tasks[0]['task_status'] != 3:
    print(f'❌ 任务未完成，当前状态: {tasks[0]["task_status"]}')
else:
    print('✅ 任务已完成')

if tasks[0]['extracted_count'] == 0:
    print('❌ 提取数量为0，大模型识别可能失败或返回空结果')
else:
    print(f'✅ 提取到 {tasks[0]["extracted_count"]} 条记录')
