"""
数据库兼容层 - 自动处理 SQLite 到 MySQL 的转换
"""
import re
from app.db_config import DB_TYPE


class MySQLCompatibleCursor:
    """
    包装原始游标，自动将 SQLite SQL 转换为 MySQL SQL
    """
    
    def __init__(self, cursor):
        self.cursor = cursor
        self.lastrowid = None
    
    def execute(self, sql, params=None):
        """执行 SQL，自动转换占位符"""
        if DB_TYPE == "mysql" and params:
            # 将 ? 转换为 %s
            sql = sql.replace("?", "%s")
        
        self.cursor.execute(sql, params)
        self.lastrowid = self.cursor.lastrowid
        return self.cursor
    
    def executemany(self, sql, params_list):
        """批量执行 SQL"""
        if DB_TYPE == "mysql" and params_list:
            sql = sql.replace("?", "%s")
        
        return self.cursor.executemany(sql, params_list)
    
    def fetchone(self):
        return self.cursor.fetchone()
    
    def fetchall(self):
        return self.cursor.fetchall()
    
    def fetchmany(self, size=None):
        return self.cursor.fetchmany(size)
    
    @property
    def rowcount(self):
        return self.cursor.rowcount
    
    def __getattr__(self, name):
        return getattr(self.cursor, name)


def get_compatible_cursor(conn):
    """获取兼容的游标"""
    cursor = conn.cursor()
    if DB_TYPE == "mysql":
        return MySQLCompatibleCursor(cursor)
    return cursor


def sqlite_to_mysql_sql(sql):
    """将 SQLite SQL 转换为 MySQL SQL"""
    if DB_TYPE != "mysql":
        return sql
    
    # 转换占位符
    sql = sql.replace("?", "%s")
    
    # 转换 INSERT OR IGNORE
    sql = sql.replace("INSERT OR IGNORE", "INSERT IGNORE")
    
    # 转换 INTEGER PRIMARY KEY AUTOINCREMENT
    sql = sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "INT AUTO_INCREMENT PRIMARY KEY")
    
    # 转换 TEXT 为 LONGTEXT（如果需要）
    # sql = sql.replace("TEXT", "LONGTEXT")
    
    # 转换 BOOLEAN
    sql = sql.replace("BOOLEAN", "TINYINT(1)")
    
    return sql
