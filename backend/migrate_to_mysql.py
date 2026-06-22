#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据迁移脚本 - 将 SQLite 数据迁移到 MySQL
"""

import os
import sys
import sqlite3
import pymysql
from datetime import datetime

# SQLite 源数据库路径
SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), "data/admission_system.db")

# MySQL 目标数据库配置
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "admission_system")


def get_sqlite_connection():
    """获取 SQLite 连接"""
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_mysql_connection():
    """获取 MySQL 连接"""
    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn


def migrate_table(sqlite_conn, mysql_conn, table_name, columns=None):
    """迁移单个表"""
    sqlite_cursor = sqlite_conn.cursor()
    mysql_cursor = mysql_conn.cursor()
    
    # 获取表结构
    sqlite_cursor.execute(f"PRAGMA table_info({table_name})")
    sqlite_columns = [col[1] for col in sqlite_cursor.fetchall()]
    
    if columns:
        cols_to_select = columns
    else:
        cols_to_select = sqlite_columns
    
    # 获取数据
    sqlite_cursor.execute(f"SELECT {', '.join(cols_to_select)} FROM {table_name}")
    rows = sqlite_cursor.fetchall()
    
    if not rows:
        print(f"  表 {table_name} 没有数据，跳过")
        return 0
    
    # 构建 INSERT 语句
    placeholders = ', '.join(['%s'] * len(cols_to_select))
    insert_sql = f"INSERT INTO {table_name} ({', '.join(cols_to_select)}) VALUES ({placeholders})"
    
    # 转换数据并插入
    migrated = 0
    for row in rows:
        try:
            values = []
            for col in cols_to_select:
                val = row[col]
                # SQLite 的 datetime 类型转换
                if isinstance(val, str) and val.startswith('datetime.datetime('):
                    val = None
                values.append(val)
            
            mysql_cursor.execute(insert_sql, values)
            migrated += 1
        except Exception as e:
            print(f"    插入失败: {e}")
    
    mysql_conn.commit()
    print(f"  迁移完成: {migrated} 条记录")
    return migrated


def main():
    print("=" * 60)
    print("🎓 数据迁移脚本 - SQLite -> MySQL")
    print("=" * 60)
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 检查 SQLite 数据库是否存在
    if not os.path.exists(SQLITE_DB_PATH):
        print(f"❌ SQLite 数据库不存在: {SQLITE_DB_PATH}")
        sys.exit(1)
    
    # 连接数据库
    try:
        sqlite_conn = get_sqlite_connection()
        print("✅ SQLite 连接成功")
    except Exception as e:
        print(f"❌ SQLite 连接失败: {e}")
        sys.exit(1)
    
    try:
        mysql_conn = get_mysql_connection()
        print("✅ MySQL 连接成功")
    except Exception as e:
        print(f"❌ MySQL 连接失败: {e}")
        sys.exit(1)
    
    print()
    
    # 获取 SQLite 中的表列表
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    sqlite_tables = [row[0] for row in sqlite_cursor.fetchall()]
    
    print(f"📋 SQLite 中找到 {len(sqlite_tables)} 个表:")
    for table in sqlite_tables:
        print(f"  - {table}")
    
    print()
    
    # 需要迁移的表（按依赖顺序）
    tables_to_migrate = [
        'countries',
        'universities',
        'source_schools',
        'roles',
        'users',
        'admission_records',
        'collection_tasks',
        'admission_requirements',
        'statistics_daily',
        'admission_records_staging',
        '_task_queue',
        '_seen_urls'
    ]
    
    total_migrated = 0
    
    for table_name in tables_to_migrate:
        if table_name in sqlite_tables:
            print(f"🔄 迁移表: {table_name}")
            count = migrate_table(sqlite_conn, mysql_conn, table_name)
            total_migrated += count
        else:
            print(f"⚠️  跳过不存在的表: {table_name}")
    
    print()
    print(f"🎉 迁移完成！共迁移 {total_migrated} 条记录")
    print(f"⏰ 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 关闭连接
    sqlite_conn.close()
    mysql_conn.close()


if __name__ == '__main__':
    main()
