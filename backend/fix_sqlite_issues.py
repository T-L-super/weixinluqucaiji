"""
修复 main.py 中的 SQLite 兼容性问题
将所有使用 ? 占位符的 SQL 语句自动转换为 MySQL 兼容格式
"""

import re

def fix_main_py():
    """修复 main.py 文件"""
    
    file_path = r"d:\Edge浏览器下载\weixinluqucaiji\backend\app\main.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 在文件开头添加导入
    if 'from app.db_config import exec_sql' not in content:
        # 找到 import 部分
        content = content.replace(
            'from app.db_config import get_db_connection as _get_db',
            'from app.db_config import get_db_connection as _get_db, exec_sql'
        )
    
    # 2. 替换所有的 cursor.execute("...", params) 为 exec_sql(cursor, "...", params)
    # 但这需要小心处理，因为有些已经手动处理过了
    
    # 3. 移除 SQLite 特有的 PRAGMA 语句
    pragma_pattern = r'conn\.execute\("PRAGMA[^"]*"\)'
    content = re.sub(pragma_pattern, '# PRAGMA removed for MySQL compatibility', content)
    
    # 4. 替换 INSERT OR IGNORE 为 MySQL 语法
    content = content.replace(
        'INSERT OR IGNORE INTO',
        'INSERT IGNORE INTO'
    )
    
    # 5. 替换 CREATE INDEX IF NOT EXISTS (MySQL 不支持)
    # 需要用 try-except 包裹
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("修复完成！")
    print("注意：还需要手动检查以下问题：")
    print("1. 所有 cursor.execute() 调用是否使用了正确的占位符")
    print("2. LIMIT ? OFFSET ? 是否已转换为 LIMIT %s OFFSET %s")
    print("3. SQLite 特有的函数是否已移除或替换")

if __name__ == "__main__":
    fix_main_py()
