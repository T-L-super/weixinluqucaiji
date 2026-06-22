#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试奖学金和姓名提取修复"""

import re
import sys

# 添加父目录到路径
sys.path.insert(0, 'backend')
from app.async_worker import PAT_SCHOLARSHIP, PAT_SCHOLARSHIP_AFTER, PAT_NAME_ENGLISH, _extract_name_from_text

# 测试文本
test_text = "热烈祝贺华东康桥首届毕业生中Jack Yang 已收到密歇根州立大学（Michigan State University）录取通知！并获得5,000美元的奖学金。"

print("=" * 60)
print("测试文本:")
print(test_text)
print("=" * 60)

# 测试奖学金提取
print("\n【奖学金提取测试】")
print("-" * 60)

sm1 = PAT_SCHOLARSHIP.search(test_text)
print(f"PAT_SCHOLARSHIP 匹配结果: {sm1}")

sm2 = PAT_SCHOLARSHIP_AFTER.search(test_text)
print(f"PAT_SCHOLARSHIP_AFTER 匹配结果: {sm2}")
if sm2:
    print(f"  提取金额: {sm2.group(1)}")

# 测试姓名提取
print("\n【姓名提取测试】")
print("-" * 60)

name = _extract_name_from_text(test_text)
print(f"提取的学生姓名: '{name}'")

# 测试英文名正则
m = PAT_NAME_ENGLISH.search(test_text)
print(f"PAT_NAME_ENGLISH 匹配结果: {m}")
if m:
    print(f"  提取姓名: '{m.group(1)}'")

print("\n" + "=" * 60)
print("测试结果总结:")
print(f"  学生姓名: {name if name else '❌ 提取失败'}")
print(f"  奖学金金额: {sm2.group(1) if sm2 else '❌ 提取失败'}")
print("=" * 60)
