import re

# 读取文件
with open('app/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换所有 CURRENT_TIMESTAMP（不包括表定义中的 DEFAULT CURRENT_TIMESTAMP）
# 只替换 VALUES 子句和 SET 子句中的 CURRENT_TIMESTAMP

# 替换 VALUES 中的 CURRENT_TIMESTAMP
content = re.sub(r"VALUES \(([^)]*?)CURRENT_TIMESTAMP([^)]*?)\)", 
                lambda m: f"VALUES ({m.group(1)}?, {m.group(2)}?)", 
                content)

# 替换 SET 中的 CURRENT_TIMESTAMP
content = re.sub(r"SET ([^=]+)=CURRENT_TIMESTAMP", 
                r"SET \1=?", 
                content)

# 替换 VALUES 中连续的 CURRENT_TIMESTAMP
content = re.sub(r"CURRENT_TIMESTAMP,\s*CURRENT_TIMESTAMP", "?, ?", content)
content = re.sub(r"CURRENT_TIMESTAMP,\s*CURRENT_TIMESTAMP,\s*CURRENT_TIMESTAMP", "?, ?, ?", content)

# 替换 VALUES (..., CURRENT_TIMESTAMP)
content = re.sub(r", CURRENT_TIMESTAMP\s*\)", ", ?)", content)

# 写回文件
with open('app/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("已完成替换")