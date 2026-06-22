#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用 source_school_name 填充 title 字段"""

import sqlite3
import os

DB_PATH = r"d:\大学录取信息整理系统\backend\data\admission_system.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 用 source_school_name 填充 title
cursor.execute("UPDATE collection_tasks SET title = source_school_name WHERE title IS NULL OR title = ''")
updated = cursor.rowcount
conn.commit()

print(f"已更新 {updated} 条任务的标题字段")

# 验证结果
cursor.execute("SELECT COUNT(*) FROM collection_tasks WHERE title IS NULL OR title = ''")
empty_count = cursor.fetchone()[0]
print(f"更新后标题为空的任务数: {empty_count}")

conn.close()
