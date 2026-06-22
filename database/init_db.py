#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
# 完成时间：2026-03-18 23:22 UTC
# 数据库初始化脚本 - 大学录取信息整理系统
# 功能：创建 SQLite 数据库、表结构、索引、视图和测试数据
# ============================================================

import sqlite3
import os
from datetime import datetime

# 数据库配置
DB_NAME = 'admission_system.db'
SCHEMA_FILE = 'schema.sql'
SAMPLE_DATA_FILE = 'sample_data.sql'

# 获取脚本所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, DB_NAME)


def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    # 启用外键约束
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_database():
    """初始化数据库 - 创建表结构"""
    print(f'📊 开始初始化数据库：{DB_PATH}')
    
    # 如果数据库已存在，先删除
    if os.path.exists(DB_PATH):
        print('⚠️  检测到已有数据库，正在删除...')
        os.remove(DB_PATH)
        print('✅ 旧数据库已删除')
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 读取并执行 schema.sql
        schema_path = os.path.join(BASE_DIR, SCHEMA_FILE)
        if not os.path.exists(schema_path):
            print(f'❌ 错误：找不到 schema.sql 文件：{schema_path}')
            return False
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        print('📝 正在执行建表语句...')
        cursor.executescript(schema_sql)
        conn.commit()
        print('✅ 表结构创建成功')
        
        return True
    
    except sqlite3.Error as e:
        print(f'❌ 数据库错误：{e}')
        return False
    
    finally:
        conn.close()


def load_sample_data():
    """加载测试数据"""
    print(f'\n📊 开始加载测试数据...')
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 读取并执行 sample_data.sql
        sample_path = os.path.join(BASE_DIR, SAMPLE_DATA_FILE)
        if not os.path.exists(sample_path):
            print(f'❌ 错误：找不到 sample_data.sql 文件：{sample_path}')
            return False
        
        with open(sample_path, 'r', encoding='utf-8') as f:
            sample_sql = f.read()
        
        print('📝 正在插入测试数据...')
        cursor.executescript(sample_sql)
        conn.commit()
        print('✅ 测试数据加载成功')
        
        return True
    
    except sqlite3.Error as e:
        print(f'❌ 数据库错误：{e}')
        return False
    
    finally:
        conn.close()


def verify_database():
    """验证数据库"""
    print(f'\n🔍 开始验证数据库...')
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 检查各表记录数
        tables = [
            'countries',
            'universities',
            'source_schools',
            'admission_records',
            'collection_tasks',
            'admission_requirements',
            'statistics_daily'
        ]
        
        print('\n📋 表数据统计:')
        print('-' * 50)
        
        for table in tables:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            print(f'  {table:30s} {count:5d} 条记录')
        
        # 检查视图
        print('\n📋 视图列表:')
        print('-' * 50)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
        views = cursor.fetchall()
        for view in views:
            print(f'  ✓ {view[0]}')
        
        # 检查索引
        print('\n📋 索引列表:')
        print('-' * 50)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
        indexes = cursor.fetchall()
        for index in indexes:
            print(f'  ✓ {index[0]}')
        
        # 测试视图查询
        print('\n🧪 测试视图查询:')
        print('-' * 50)
        
        # 测试 v_admission_records_full
        cursor.execute('SELECT COUNT(*) FROM v_admission_records_full')
        count = cursor.fetchone()[0]
        print(f'  v_admission_records_full: {count} 条记录')
        
        # 测试 v_stats_by_country
        cursor.execute('SELECT country, total_records FROM v_stats_by_country LIMIT 3')
        results = cursor.fetchall()
        print(f'  v_stats_by_country (前 3):')
        for row in results:
            print(f'    - {row[0]}: {row[1]} 条')
        
        # 测试 v_stats_by_university
        cursor.execute('SELECT university_cn, total_records FROM v_stats_by_university LIMIT 3')
        results = cursor.fetchall()
        print(f'  v_stats_by_university (前 3):')
        for row in results:
            print(f'    - {row[0]}: {row[1]} 条')
        
        # 测试 v_pending_tasks
        cursor.execute('SELECT COUNT(*) FROM v_pending_tasks')
        count = cursor.fetchone()[0]
        print(f'  v_pending_tasks: {count} 个待处理任务')
        
        print('\n✅ 数据库验证完成！')
        
        return True
    
    except sqlite3.Error as e:
        print(f'❌ 验证错误：{e}')
        return False
    
    finally:
        conn.close()


def show_sample_queries():
    """显示示例查询"""
    print('\n' + '=' * 60)
    print('📚 示例查询语句')
    print('=' * 60)
    
    queries = [
        ('查询所有录取记录', 'SELECT student_name_cn, university_cn, major_cn, admission_year FROM admission_records LIMIT 10'),
        ('按国家统计录取数量', 'SELECT country, COUNT(*) as count FROM admission_records GROUP BY country ORDER BY count DESC'),
        ('查询奖学金记录', 'SELECT student_name_cn, university_cn, scholarship_amount, scholarship_currency FROM admission_records WHERE scholarship_amount > 0 LIMIT 10'),
        ('查询待处理采集任务', 'SELECT article_url, source_school_name, priority FROM collection_tasks WHERE task_status = 0 ORDER BY priority DESC'),
        ('查询完整录取信息（视图）', 'SELECT student_name_cn, university_cn, major_cn, continent, avg_scholarship FROM v_admission_records_full LIMIT 10'),
    ]
    
    for i, (desc, query) in enumerate(queries, 1):
        print(f'\n{i}. {desc}')
        print(f'   SQL: {query}')


def main():
    """主函数"""
    print('=' * 60)
    print('🎓 大学录取信息整理系统 - 数据库初始化')
    print('=' * 60)
    print(f'⏰ 初始化时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'📁 数据库路径：{DB_PATH}')
    print('=' * 60)
    
    # 步骤 1: 初始化数据库
    if not init_database():
        print('\n❌ 数据库初始化失败')
        return False
    
    # 步骤 2: 加载测试数据
    if not load_sample_data():
        print('\n❌ 测试数据加载失败')
        return False
    
    # 步骤 3: 验证数据库
    if not verify_database():
        print('\n❌ 数据库验证失败')
        return False
    
    # 步骤 4: 显示示例查询
    show_sample_queries()
    
    print('\n' + '=' * 60)
    print('✅ 数据库初始化完成！')
    print('=' * 60)
    
    return True


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
