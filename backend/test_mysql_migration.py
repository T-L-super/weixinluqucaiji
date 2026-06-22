#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 MySQL 迁移是否成功
"""

import os
import sys
from app.db_config import test_connection, DB_TYPE, get_db_connection

def test_database_connection():
    """测试数据库连接"""
    success, message = test_connection()
    print(f"🔌 数据库连接测试: {'✅' if success else '❌'} {message}")
    return success

def test_table_exists(table_name):
    """测试表是否存在"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if DB_TYPE == "mysql":
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        else:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        
        result = cursor.fetchone()
        conn.close()
        
        exists = result is not None
        print(f"   {table_name}: {'✅ 存在' if exists else '❌ 不存在'}")
        return exists
    except Exception as e:
        print(f"   {table_name}: ❌ 错误 - {e}")
        return False

def test_table_data(table_name, expected_min_count=0):
    """测试表数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()
        conn.close()
        
        count = count[0] if isinstance(count, tuple) else count.get('COUNT(*)') if isinstance(count, dict) else 0
        status = "✅" if count >= expected_min_count else "⚠️"
        print(f"   {table_name}: {status} {count} 条记录")
        return count
    except Exception as e:
        print(f"   {table_name}: ❌ 错误 - {e}")
        return -1

def main():
    print("=" * 60)
    print("🧪 MySQL 迁移测试")
    print("=" * 60)
    print(f"数据库类型: {DB_TYPE}")
    print()
    
    # 测试连接
    if not test_database_connection():
        sys.exit(1)
    
    print()
    print("📋 检查表结构:")
    
    tables = [
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
    
    all_exists = True
    for table in tables:
        if not test_table_exists(table):
            all_exists = False
    
    print()
    print("📊 检查数据:")
    
    total_records = 0
    for table in tables:
        count = test_table_data(table)
        if count >= 0:
            total_records += count
    
    print()
    print("=" * 60)
    if all_exists:
        print("🎉 所有表结构检查通过！")
        print(f"📈 数据库中共有 {total_records} 条记录")
    else:
        print("❌ 部分表不存在，请检查迁移脚本")
        sys.exit(1)
    
    print("=" * 60)

if __name__ == '__main__':
    main()
