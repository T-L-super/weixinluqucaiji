#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""最终调试L同学识别"""

import asyncio
import sys
import os
import re
from lxml import etree

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/app'))

from async_worker import _fetch_html


async def debug_final():
    """最终调试"""
    url = "https://mp.weixin.qq.com/s/GJqYm3DPekQgQiEyc9nL_g"
    
    try:
        html = await _fetch_html(url)
        
        # 使用lxml解析
        parser = etree.HTMLParser(encoding='utf-8')
        tree = etree.fromstring(html, parser)
        
        text = " ".join(tree.xpath('//text()'))
        
        # 找所有同学名字
        student_pattern = re.compile(r'([A-Za-z]{1}(?:同学)|[\u4e00-\u9fa5]{2,3}(?:同学))')
        students = student_pattern.findall(text)
        
        print(f"找到 {len(students)} 个同学: {students}")
        
        # 对每个同学，详细检查
        for sname in students:
            if sname in ['于各位同学', '各位同学']:
                continue
                
            print(f"\n检查: {sname}")
            
            # 找到该同学在文本中的位置
            idx = text.find(sname)
            if idx == -1:
                print("  未找到位置")
                continue
            
            # 在该位置之后查找
            after_student = text[idx + len(sname):idx + len(sname) + 150]
            print(f"  after_student: {repr(after_student)}")
            
            # 找"获得"后面的大学
            uni_pattern = re.compile(r'(?:获得|斩获|收到|拿到|荣获)\s*([\u4e00-\u9fa5]+?(?:大学|学院|科大|理工|旅游|镜湖|澳大))')
            uni_match = uni_pattern.search(after_student)
            
            if uni_match:
                print(f"  匹配到大学: {uni_match.group(1)}")
            else:
                print(f"  未匹配到大学")
                # 检查是否包含"获得"
                if '获得' in after_student:
                    print("  包含'获得'")
                else:
                    print("  不包含'获得'")
                
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_final())