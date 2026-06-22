#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查数据库表结构"""

import sqlite3

DB_PATH = r"d:\大学录取信息整理系统\backend\data\admission_system.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 检查所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("数据库表:")
for table in tables:
    print(f"  - {table[0]}")
    
print("\n" + "=" * 60)

# 检查每个表的结构
for table in tables:
    table_name = table[0]
    print(f"\n表 {table_name} 的结构:")
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # 如果有数据，显示前几行
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
    if cursor.description:
        print(f"  列名: {[desc[0] for desc in cursor.description]}")

conn.close()
