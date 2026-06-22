"""
统一数据库配置模块
支持 SQLite 和 MySQL 两种数据库
通过环境变量 DB_TYPE 切换数据库类型
"""
import os
from dotenv import load_dotenv

# 加载 .env 文件
env_path = os.path.join(os.path.dirname(__file__), "../.env")
if os.path.exists(env_path):
    load_dotenv(env_path)

import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sqlite3

# 数据库类型: sqlite 或 mysql
DB_TYPE = os.getenv("DB_TYPE", "sqlite")

# SQLite 配置
SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), "../data/admission_system.db")

# MySQL 配置
MYSQL_HOST = os.getenv("MYSQL_HOST", "10.9.8.120")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "python")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "YLcXkLEcYAihBitr")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "python")

# SQLAlchemy 引擎（用于 models.py）
_engine = None
_SessionLocal = None


def get_database_url():
    """获取数据库连接 URL"""
    if DB_TYPE == "mysql":
        return f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
    else:
        return f"sqlite:///{SQLITE_DB_PATH}"


def get_sqlalchemy_engine():
    """获取 SQLAlchemy 引擎"""
    global _engine
    if _engine is None:
        url = get_database_url()
        if DB_TYPE == "mysql":
            _engine = create_engine(
                url,
                pool_pre_ping=True,
                pool_recycle=3600,
                pool_size=10,
                max_overflow=20
            )
        else:
            _engine = create_engine(url, connect_args={"check_same_thread": False})
    return _engine


def get_sqlalchemy_session():
    """获取 SQLAlchemy 会话"""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_sqlalchemy_engine())
    return _SessionLocal()


def get_db_connection():
    """获取数据库连接（原生连接）"""
    if DB_TYPE == "mysql":
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
    else:
        conn = sqlite3.connect(SQLITE_DB_PATH, timeout=30.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA cache_size = 20000")
        conn.execute("PRAGMA temp_store = MEMORY")
        conn.execute("PRAGMA mmap_size = 67108864")
        conn.execute("PRAGMA busy_timeout = 30000")
        conn.execute("PRAGMA wal_autocheckpoint = 1000")
        conn.execute("PRAGMA journal_size_limit = 67108864")
        conn.execute("PRAGMA foreign_keys = ON")
        return conn


def get_db_cursor():
    """获取数据库游标"""
    conn = get_db_connection()
    return conn.cursor()


import re


def convert_sql_to_mysql(sql):
    """
    将 SQLite SQL 转换为 MySQL 兼容的 SQL
    - 将 ? 占位符转换为 %s
    - 移除 SQLite 特有的语法
    """
    if DB_TYPE != "mysql":
        return sql
    
    # 将 ? 替换为 %s
    converted = sql.replace("?", "%s")
    return converted


def exec_sql(cursor, sql, params=None):
    """
    执行 SQL 语句，自动处理占位符转换
    - SQLite 使用 ? 占位符
    - MySQL 使用 %s 占位符
    """
    if DB_TYPE == "mysql" and params:
        # 转换 SQL 中的 ? 为 %s
        sql = convert_sql_to_mysql(sql)
    
    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)


def fetch_count(cursor, query, params=None):
    """获取 COUNT 查询结果，兼容 MySQL DictCursor 和 SQLite Row"""
    exec_sql(cursor, query, params)
    result = cursor.fetchone()
    if isinstance(result, dict):
        # MySQL DictCursor
        return result.get('COUNT(*)', 0)
    else:
        # SQLite Row
        return result[0] if result else 0


def test_connection():
    """测试数据库连接"""
    try:
        if DB_TYPE == "mysql":
            conn = pymysql.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE,
                charset='utf8mb4'
            )
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
            conn.close()
            return True, f"MySQL 连接成功: {MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
        else:
            conn = sqlite3.connect(SQLITE_DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            return True, f"SQLite 连接成功: {SQLITE_DB_PATH}"
    except Exception as e:
        return False, str(e)


# 导出常用方法
engine = property(lambda self: get_sqlalchemy_engine())


def get_db():
    """FastAPI 依赖注入用的数据库会话"""
    db = get_sqlalchemy_session()
    try:
        yield db
    finally:
        db.close()
