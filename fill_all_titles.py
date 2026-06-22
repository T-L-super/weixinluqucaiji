#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""填充所有任务的标题字段"""

import sqlite3
import os

DB_PATH = r"d:\大学录取信息整理系统\backend\data\admission_system.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM collection_tasks WHERE title IS NULL OR title = ''")
null_count = cursor.fetchone()[0]
print(f"发现 {null_count} 条标题为空的任务")

if null_count > 0:
    cursor.execute("""
        UPDATE collection_tasks 
        SET title = CASE 
            WHEN title IS NULL OR title = '' THEN SUBSTR(article_url, 1, 100) 
            ELSE title 
        END
        WHERE title IS NULL OR title = ''
    """)
    updated = cursor.rowcount
    conn.commit()
    print(f"已填充 {updated} 条任务的标题字段")
else:
    print("没有需要填充的标题")

cursor.execute("SELECT COUNT(*) FROM collection_tasks WHERE title IS NULL OR title = ''")
remaining_null = cursor.fetchone()[0]
print(f"剩余空标题任务数: {remaining_null}")

cursor.execute("SELECT id, title, article_url FROM collection_tasks ORDER BY id DESC LIMIT 5")
tasks = cursor.fetchall()
print("\n最新5条任务:")
for task in tasks:
    tid, title, url = task
    print(f"ID: {tid}, 标题: {title[:50] if title else '(空)'}, URL: {url[:50]}...")

conn.close()
