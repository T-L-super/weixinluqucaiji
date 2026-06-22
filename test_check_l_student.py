#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查L同学的匹配情况"""

import asyncio
import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/app'))

from async_worker import _fetch_html


async def check_l_student():
    """检查网页中L同学的格式"""
    url = "https://mp.weixin.qq.com/s/GJqYm3DPekQgQiEyc9nL_g"
    
    try:
        html = await _fetch_html(url)
        
        # 提取文本
        import re
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text)
        
        # 搜索包含"同学"的行
        lines = text.split('。')
        for line in lines[:50]:
            if '同学' in line:
                print(f"包含同学的文本: {line[:100]}...")
        
        # 搜索L同学相关内容
        l_pattern = re.compile(r'[Ll]同学[^。！?；;\n]*')
        matches = l_pattern.findall(text)
        print(f"\n找到 {len(matches)} 个L同学匹配:")
        for match in matches:
            print(f"  - {match}")
            
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    asyncio.run(check_l_student())