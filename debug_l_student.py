#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调试L同学识别问题"""

import asyncio
import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/app'))

from async_worker import _fetch_html, PAT_STUDENT_ADMISSION


async def debug_l_student():
    """调试L同学识别"""
    url = "https://mp.weixin.qq.com/s/GJqYm3DPekQgQiEyc9nL_g"
    
    try:
        html = await _fetch_html(url)
        
        # 提取文本
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text)
        
        # 找到包含"L同学"和"W同学"的上下文
        patterns = [
            (r'W同学[\s\S]{0,100}获得', 'W同学上下文'),
            (r'L同学[\s\S]{0,100}获得', 'L同学上下文'),
        ]
        
        for pattern, label in patterns:
            matches = re.findall(pattern, text)
            print(f"\n{label}:")
            for i, match in enumerate(matches[:3], 1):
                print(f"  {i}. {repr(match)}")
        
        # 测试正则匹配
        print("\n测试正则匹配:")
        matches = PAT_STUDENT_ADMISSION.findall(text)
        print(f"找到 {len(matches)} 个匹配:")
        for sname, uni in matches:
            print(f"  - {sname} -> {uni}")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_l_student())