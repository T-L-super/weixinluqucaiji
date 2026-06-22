#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量创建采集任务到任务队列
"""
import requests
import json

API_BASE = "http://101.32.98.235:8000"

# 读取链接文件
with open('/root/.openclaw/workspace/大学录取信息整理系统/采集任务链接.txt', 'r', encoding='utf-8') as f:
    urls = [line.strip() for line in f if line.strip().startswith('http')]

print(f"📋 读取到 {len(urls)} 个 URL")

# 批量创建任务
response = requests.post(
    f"{API_BASE}/api/collection-tasks/batch",
    json={"urls": urls},
    headers={'Content-Type': 'application/json'}
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ 批量创建成功!")
    print(f"   新建：{result.get('created', 0)} 个")
    print(f"   跳过：{result.get('skipped', 0)} 个")
    print(f"   总计：{result.get('total', 0)} 个")
else:
    print(f"❌ 创建失败：{response.status_code}")
    print(response.text)
