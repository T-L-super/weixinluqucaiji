# 完成时间：2026-04-07
"""
MySQL 数据库连接配置
用于连接远程 bestieu_test2 数据库
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

_mysql_engine = None
MySQLSessionLocal = None

def get_mysql_engine():
    global _mysql_engine
    if _mysql_engine is None:
        from sqlalchemy import create_engine
        MYSQL_HOST = os.getenv("MYSQL_HOST", "rm-uf6733p2m724p898aho.mysql.rds.aliyuncs.com")
        MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
        MYSQL_USER = os.getenv("MYSQL_USER", "openclaw_select")
        MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "Bestu2026.")
        MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "bestus")
        
        MYSQL_DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
        
        _mysql_engine = create_engine(
            MYSQL_DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={
                "charset": "utf8mb4"
            }
        )
    return _mysql_engine

mysql_engine = property(lambda self: get_mysql_engine())


def get_mysql_db():
    """获取 MySQL 数据库会话"""
    global MySQLSessionLocal
    if MySQLSessionLocal is None:
        from sqlalchemy.orm import sessionmaker
        MySQLSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_mysql_engine())
    db = MySQLSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_mysql_connection():
    """测试 MySQL 连接"""
    try:
        with mysql_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return True, "MySQL 连接成功"
    except Exception as e:
        return False, f"MySQL 连接失败: {str(e)}"


# 源数据表名配置
WECHAT_ARTICLES_TABLE = "wechat_official_account_articles"

# 表名映射（兼容不同数据库名）
TABLE_MAPPING = {
    "bestieu_test2": "wechat_official_account_articles",
    "bestus": "wechat_official_account_articles"
}
