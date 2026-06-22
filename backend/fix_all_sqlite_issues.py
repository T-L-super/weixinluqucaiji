#!/usr/bin/env python3
import re

def fix_file(filepath):
    print(f"Processing: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到所有 cursor.execute 调用并替换为 exec_sql
    # 需要确保导入了 exec_sql
    if 'from app.db_config import exec_sql' not in content:
        # 在文件开头的 import 部分添加导入
        content = content.replace(
            'from app.db_config import get_db_connection',
            'from app.db_config import get_db_connection, exec_sql'
        )
    
    # 替换 cursor.execute(...) 为 exec_sql(cursor, ...)
    # 处理多种格式的调用
    content = re.sub(
        r'cursor\.execute\(\s*("[^"]+"|\'[^\']+\')\s*(?:,\s*(\[.*?\]|\(.*?\)))?\s*\)',
        lambda m: f'exec_sql(cursor, {m.group(1)}{", " + m.group(2) if m.group(2) else ""})',
        content,
        flags=re.DOTALL
    )
    
    # 处理可能的注释问题（避免替换注释中的代码）
    # 这是一个简化的处理，可能需要更复杂的逻辑
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed: {filepath}")

# 修复 main.py
fix_file('app/main.py')

# 修复 collector.py
fix_file('app/collector.py')

print("\n批量修复完成！")
