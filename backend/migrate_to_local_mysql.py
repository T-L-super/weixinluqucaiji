#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整数据迁移脚本 - 将 SQLite 迁移到本地 Navicat MySQL
支持：
1. 自动创建 MySQL 表结构
2. 迁移所有数据
3. 处理数据类型转换
4. 保留自增ID
"""

import os
import sys
import sqlite3
import pymysql
from datetime import datetime

# SQLite 源数据库路径
SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), "data/admission_system.db")

# MySQL 目标数据库配置（本地 Navicat）
MYSQL_CONFIG = {
    'host': '10.9.8.120',
    'port': 3306,
    'user': 'python',
    'password': 'YLcXkLEcYAihBitr',
    'database': 'python',
    'charset': 'utf8mb4'
}

def get_sqlite_connection():
    """获取 SQLite 连接"""
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_mysql_connection():
    """获取 MySQL 连接"""
    conn = pymysql.connect(
        host=MYSQL_CONFIG['host'],
        port=MYSQL_CONFIG['port'],
        user=MYSQL_CONFIG['user'],
        password=MYSQL_CONFIG['password'],
        database=MYSQL_CONFIG['database'],
        charset=MYSQL_CONFIG['charset'],
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

def create_mysql_tables(mysql_conn):
    """创建 MySQL 表结构"""
    cursor = mysql_conn.cursor()
    
    # 表定义
    tables = {
        'countries': '''
            CREATE TABLE IF NOT EXISTS countries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name_cn VARCHAR(100) NOT NULL UNIQUE,
                name_en VARCHAR(100),
                continent VARCHAR(50),
                region VARCHAR(50),
                currency VARCHAR(10),
                is_popular TINYINT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''',
        'universities': '''
            CREATE TABLE IF NOT EXISTS universities (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name_cn VARCHAR(191) NOT NULL,
                name_en VARCHAR(191),
                country VARCHAR(50),
                type VARCHAR(50),
                ranking_us_news INT,
                ranking_qs INT,
                is_target TINYINT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uk_universities_name_cn (name_cn)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''',
        'source_schools': '''
            CREATE TABLE IF NOT EXISTS source_schools (
                id INT AUTO_INCREMENT PRIMARY KEY,
                school_name VARCHAR(191) NOT NULL,
                school_type VARCHAR(50),
                city VARCHAR(100),
                province VARCHAR(100),
                country VARCHAR(50),
                is_international TINYINT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uk_source_schools_name (school_name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''',
        'roles': '''
            CREATE TABLE IF NOT EXISTS roles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL UNIQUE,
                description VARCHAR(200),
                permissions TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''',
        'users': '''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                hashed_password VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                full_name VARCHAR(100),
                role_id INT DEFAULT 3,
                is_active TINYINT DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''',
        'admission_records': '''
            CREATE TABLE IF NOT EXISTS admission_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_name_cn VARCHAR(100) NOT NULL,
                student_name_en VARCHAR(100),
                student_grade VARCHAR(20),
                country VARCHAR(50) NOT NULL,
                country_en VARCHAR(50),
                university_cn VARCHAR(191) NOT NULL,
                university_en VARCHAR(191),
                university_type VARCHAR(50),
                university_ranking INT,
                major_cn VARCHAR(191),
                major_en VARCHAR(191),
                major_category VARCHAR(50),
                admission_type VARCHAR(50),
                admission_status VARCHAR(50),
                conditional_offer TINYINT DEFAULT 0,
                admission_date DATE,
                admission_year INT NOT NULL,
                language_requirement_type VARCHAR(50),
                language_score_required VARCHAR(50),
                language_score_actual VARCHAR(50),
                language_waived TINYINT DEFAULT 0,
                sat_required VARCHAR(50),
                sat_actual VARCHAR(50),
                test_optional TINYINT DEFAULT 0,
                scholarship_amount DECIMAL(10,2),
                scholarship_currency VARCHAR(10),
                scholarship_type VARCHAR(50),
                source_school VARCHAR(200) NOT NULL,
                article_url VARCHAR(500) NOT NULL,
                article_title VARCHAR(300),
                publish_date DATE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TINYINT DEFAULT 1,
                data_quality TINYINT DEFAULT 3,
                notes TEXT,
                review_status VARCHAR(20) DEFAULT 'pending',
                review_note TEXT,
                reviewed_by VARCHAR(100),
                reviewed_at DATETIME,
                promoted_at DATETIME,
                recognition_model VARCHAR(50),
                data_source VARCHAR(200)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''',
        'collection_tasks': '''
            CREATE TABLE IF NOT EXISTS collection_tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                article_url VARCHAR(500) NOT NULL,
                source_school_id INT,
                source_school_name VARCHAR(191),
                priority INT DEFAULT 5,
                task_status TINYINT DEFAULT 0,
                retry_count INT DEFAULT 0,
                max_retry INT DEFAULT 3,
                extracted_count INT DEFAULT 0,
                error_message TEXT,
                scheduled_at DATETIME,
                started_at DATETIME,
                completed_at DATETIME,
                processor VARCHAR(50),
                title VARCHAR(191),
                recognition_model VARCHAR(50),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uk_collection_tasks_url (article_url(191))
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''',
        'admission_requirements': '''
            CREATE TABLE IF NOT EXISTS admission_requirements (
                id INT AUTO_INCREMENT PRIMARY KEY,
                record_id INT NOT NULL,
                gpa_required VARCHAR(50),
                toefl_total INT,
                ielts_total DECIMAL(3,1),
                sat_total INT,
                act_total INT,
                essay_required TINYINT DEFAULT 0,
                portfolio_required TINYINT DEFAULT 0,
                interview_required TINYINT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (record_id) REFERENCES admission_records(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''',
        'statistics_daily': '''
            CREATE TABLE IF NOT EXISTS statistics_daily (
                id INT AUTO_INCREMENT PRIMARY KEY,
                stat_date DATE NOT NULL UNIQUE,
                total_records INT DEFAULT 0,
                records_by_country TEXT,
                records_by_university TEXT,
                records_by_major TEXT,
                avg_scholarship DECIMAL(10,2),
                top_countries TEXT,
                top_universities TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''',
        'admission_records_staging': '''
            CREATE TABLE IF NOT EXISTS admission_records_staging (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_name_cn VARCHAR(100),
                student_name_en VARCHAR(100),
                student_grade VARCHAR(20),
                country VARCHAR(50),
                country_en VARCHAR(50),
                university_cn VARCHAR(191),
                university_en VARCHAR(191),
                university_type VARCHAR(50),
                university_ranking INT,
                major_cn VARCHAR(191),
                major_en VARCHAR(191),
                major_category VARCHAR(50),
                admission_type VARCHAR(50),
                admission_status VARCHAR(50),
                conditional_offer TINYINT DEFAULT 0,
                admission_date DATE,
                admission_year INT,
                language_requirement_type VARCHAR(50),
                language_score_required VARCHAR(50),
                language_score_actual VARCHAR(50),
                language_waived TINYINT DEFAULT 0,
                sat_required VARCHAR(50),
                sat_actual VARCHAR(50),
                test_optional TINYINT DEFAULT 0,
                scholarship_amount DECIMAL(10,2),
                scholarship_currency VARCHAR(10),
                scholarship_type VARCHAR(50),
                source_school VARCHAR(191),
                article_url VARCHAR(500),
                article_title VARCHAR(191),
                publish_date DATE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TINYINT DEFAULT 1,
                data_quality TINYINT DEFAULT 3,
                notes TEXT,
                review_status VARCHAR(20) DEFAULT 'pending',
                recognition_model VARCHAR(50),
                data_source VARCHAR(200)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        '''
    }
    
    for table_name, create_sql in tables.items():
        try:
            cursor.execute(create_sql)
            print(f"创建表: {table_name}")
        except Exception as e:
            print(f"创建表失败 {table_name}: {e}")
    
    mysql_conn.commit()

def migrate_table(sqlite_conn, mysql_conn, table_name):
    """迁移单个表的数据"""
    sqlite_cursor = sqlite_conn.cursor()
    mysql_cursor = mysql_conn.cursor()
    
    # 获取 SQLite 表结构
    sqlite_cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in sqlite_cursor.fetchall()]
    
    if not columns:
        print(f"⚠️  表 {table_name} 没有列信息")
        return 0
    
    # 获取数据
    sqlite_cursor.execute(f"SELECT {', '.join(columns)} FROM {table_name}")
    rows = sqlite_cursor.fetchall()
    
    if not rows:
        print(f"   表 {table_name} 没有数据")
        return 0
    
    # 构建 INSERT 语句（保留自增ID）
    placeholders = ', '.join(['%s'] * len(columns))
    insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
    
    # 批量插入
    migrated = 0
    batch_size = 100
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        values_list = []
        
        for row in batch:
            values = []
            for col in columns:
                val = row[col]
                # 处理特殊类型
                if isinstance(val, bytes):
                    val = val.decode('utf-8', errors='ignore')
                elif val == 'None' or val is None:
                    val = None
                values.append(val)
            values_list.append(values)
        
        try:
            mysql_cursor.executemany(insert_sql, values_list)
            migrated += len(values_list)
        except Exception as e:
            print(f"    插入失败: {e}")
    
    mysql_conn.commit()
    print(f"   迁移完成: {migrated} 条记录")
    return migrated

def main():
    print("=" * 60)
    print("数据迁移脚本 - SQLite -> Navicat MySQL")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 连接 MySQL 数据库
    try:
        mysql_conn = get_mysql_connection()
        print(f"MySQL 连接成功: {MYSQL_CONFIG['host']}/{MYSQL_CONFIG['database']}")
    except Exception as e:
        print(f"MySQL 连接失败: {e}")
        print("请确保：")
        print("   1. MySQL 服务已启动")
        print("   2. 数据库 'python' 已创建")
        print("   3. 用户 python 有权限访问")
        sys.exit(1)
    
    print()
    
    # 创建表结构
    print("创建 MySQL 表结构...")
    create_mysql_tables(mysql_conn)
    
    print()
    
    # 检查 SQLite 数据库是否存在
    if os.path.exists(SQLITE_DB_PATH):
        try:
            sqlite_conn = get_sqlite_connection()
            print("SQLite 连接成功")
            
            # 获取 SQLite 中的表列表
            sqlite_cursor = sqlite_conn.cursor()
            sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            sqlite_tables = [row[0] for row in sqlite_cursor.fetchall()]
            
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
                'admission_records_staging'
            ]
            
            total_migrated = 0
            
            print("开始迁移数据...")
            for table_name in tables_to_migrate:
                if table_name in sqlite_tables:
                    print(f"\n迁移表: {table_name}")
                    count = migrate_table(sqlite_conn, mysql_conn, table_name)
                    total_migrated += count
                else:
                    print(f"\n跳过不存在的表: {table_name}")
            
            print("\n" + "=" * 60)
            print(f"迁移完成！共迁移 {total_migrated} 条记录")
            print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("\n迁移的表:")
            for table in tables_to_migrate:
                print(f"   {table}")
            print("\n提示：")
            print("   1. 打开 Navicat 连接到本地 MySQL")
            print("   2. 选择数据库 'python'")
            print("   3. 刷新左侧列表即可看到所有表")
            print("=" * 60)
            
            sqlite_conn.close()
        except Exception as e:
            print(f"SQLite 操作失败: {e}")
    else:
        print(f"SQLite 数据库不存在: {SQLITE_DB_PATH}")
        print("已创建 MySQL 表结构，但没有数据可迁移")
        print("\n提示：")
        print("   1. 打开 Navicat 连接到本地 MySQL")
        print("   2. 选择数据库 'python'")
        print("   3. 刷新左侧列表即可看到所有表")
    
    mysql_conn.close()

if __name__ == '__main__':
    main()
