#!/usr/bin/env python3
# 快速修复脚本 - 更新 API_BASE
import re

file_path = '/root/.openclaw/workspace/大学录取信息整理系统/backend/app/main.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 替换 API_BASE
content = content.replace("const API_BASE = ''", "const API_BASE = '/api'")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 已更新 API_BASE 为 '/api'")
