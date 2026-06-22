#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查特殊字符"""

import asyncio
import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/app'))

from async_worker import _fetch_html


async def debug_chars():
    """检查特殊字符"""
    url = "https://mp.weixin.qq.com/s/GJqYm3DPekQgQiEyc9nL_g"
    
    try:
        html = await _fetch_html(url)
        
        # 提取文本
        text = re.sub(r'<[^>]+>', ' ', html)
        
        # 查找包含"录"或"取"的行
        lines = text.split('。')
        for line in lines[:20]:
            if '录' in line or '取' in line:
                print(f"行: {repr(line[:100])}")
        
        # 检查"同学"字符
        if '同学' in text:
            print("\n找到'同学'")
        else:
            print("\n未找到'同学'")
            
        # 检查常见字符
        chars_to_check = ['同', '学', 'W', 'L', '录', '取']
        for char in chars_to_check:
            if char in text:
                print(f"  '{char}' 在文本中")
            else:
                print(f"  '{char}' 不在文本中")
                
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_chars())