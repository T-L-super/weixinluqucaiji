#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查 MySQL 数据库中的表"""

import pymysql

conn = pymysql.connect(
    host='10.9.8.120',
    port=3306,
    user='python',
    password='YLcXkLEcYAihBitr',
    database='python',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

cursor = conn.cursor()
cursor.execute('SHOW TABLES')
tables = cursor.fetchall()

# 我们系统创建的表
system_tables = [
    'countries',
    'universities',
    'source_schools',
    'roles',
    'users',
    'admission_records',
    'collection_tasks',
    'admission_requirements',
    'statistics_daily',
    'admission_records_staging'
]

print('=' * 60)
print('录取采集系统 - MySQL 数据库表')
print('=' * 60)

found_tables = []
for table in tables:
    table_name = list(table.values())[0]
    if table_name in system_tables:
        cursor.execute(f'SELECT COUNT(*) as count FROM `{table_name}`')
        count = cursor.fetchone()['count']
        found_tables.append((table_name, count))

for i, (table_name, count) in enumerate(found_tables, 1):
    print(f'{i}. {table_name:<35} {count:>5} 条记录')

print('=' * 60)
print(f'系统表总计: {len(found_tables)} 个')
print('=' * 60)

conn.close()
