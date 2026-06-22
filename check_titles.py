#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查并修复任务标题字段"""

import sqlite3
import os

DB_PATH = r"d:\大学录取信息整理系统\backend\data\admission_system.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 查看表结构
cursor.execute("PRAGMA table_info(collection_tasks)")
columns = cursor.fetchall()

print("当前表结构:")
print("=" * 80)
for col in columns:
    print(f"{col[1]:<20} {col[2]:<15}")

# 检查是否有 title 字段
has_title = any(col[1] == 'title' for col in columns)
print(f"\n是否有 title 字段: {'是' if has_title else '否'}")

# 如果没有 title 字段，添加它
if not has_title:
    print("\n正在添加 title 字段...")
    cursor.execute("ALTER TABLE collection_tasks ADD COLUMN title TEXT")
    conn.commit()
    print("title 字段添加成功！")

conn.close()
