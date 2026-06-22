"""
排查任务数据过滤问题
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'backend', 'data', 'admission_system.db')
URL_KEYWORD = '0-MWT6oyIOZqJpCFCR_I2g'

print('='*100)
print('数据采集过滤分析工具')
print('='*100)
print()

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# 1. 查询采集任务
c.execute('SELECT id, article_url, title, task_status, extracted_count, recognition_model FROM collection_tasks WHERE article_url LIKE ?', (f'%{URL_KEYWORD}%',))
tasks = c.fetchall()

if not tasks:
    print(f'❌ 未找到包含关键词 "{URL_KEYWORD}" 的采集任务')
    conn.close()
    exit()

print(f'✅ 找到 {len(tasks)} 个相关采集任务')
print()

for task in tasks:
    task_id = task['id']
    print('-'*100)
    print(f'任务 ID: {task_id}')
    print(f'标题: {task["title"]}')
    print(f'状态: {task["task_status"]} (0=待处理, 2=处理中, 3=已完成, 4=失败)')
    print(f'识别模型: {task["recognition_model"] or "无"}')
    print()
    
    # 2. 查询暂存表记录
    c.execute('''
        SELECT id, student_name_cn, university_cn, major_cn, country, source_school, 
               review_status, article_url, created_at
        FROM admission_records_staging 
        WHERE article_url LIKE ?
        ORDER BY created_at
    ''', (f'%{URL_KEYWORD}%',))
    staging_records = c.fetchall()
    
    print(f'📊 暂存表记录数: {len(staging_records)}')
    print()
    
    # 按审核状态分组
    status_groups = {}
    for rec in staging_records:
        status = rec['review_status']
        if status not in status_groups:
            status_groups[status] = []
        status_groups[status].append(rec)
    
    for status, recs in status_groups.items():
        status_name = {'pending': '待审核', 'ai_passed': 'AI通过', 'approved': '已通过', 'rejected': '已拒绝'}.get(status, status)
        print(f'  [{status_name}] {len(recs)} 条')
        for i, rec in enumerate(recs, 1):
            print(f'    {i}. ID={rec["id"]} | 学生={rec["student_name_cn"]} | 大学={rec["university_cn"]} | 专业={rec["major_cn"] or "-"} | 国家={rec["country"] or "-"}')
    
    print()
    
    # 3. 查询AI拒绝记录
    c.execute('''
        SELECT id, student_name_cn, university_cn, major_cn, country, reject_reason, created_at
        FROM ai_rejected_log 
        WHERE article_url LIKE ?
        ORDER BY created_at
    ''', (f'%{URL_KEYWORD}%',))
    rejected = c.fetchall()
    
    if rejected:
        print(f'❌ AI拒绝记录数: {len(rejected)}')
        print()
        for i, rec in enumerate(rejected, 1):
            print(f'  {i}. 学生={rec["student_name_cn"]} | 大学={rec["university_cn"]} | 专业={rec["major_cn"] or "-"} | 原因={rec["reject_reason"]}')
        print()
    
    # 4. 分析过滤原因
    print('='*100)
    print('📈 过滤分析')
    print('='*100)
    
    extracted_count = task['extracted_count'] or 0
    staging_count = len(staging_records)
    rejected_count = len(rejected)
    
    print(f'提取记录总数: {extracted_count}')
    print(f'进入暂存表: {staging_count}')
    print(f'被AI拒绝: {rejected_count}')
    print(f'缺失记录: {extracted_count - staging_count - rejected_count}')
    print()
    
    missing = extracted_count - staging_count - rejected_count
    if missing > 0:
        print(f'⚠️  有 {missing} 条记录既不在暂存表，也不在AI拒绝日志中')
        print('   可能原因：')
        print('   1. 学生姓名为空或"未知"')
        print('   2. 大学名称为空')
        print('   3. 必填字段（学生姓名、国家、大学）缺失')
        print('   4. SmartCorrector修正失败')
    else:
        print('✅ 所有记录都有明确的去向')

conn.close()
