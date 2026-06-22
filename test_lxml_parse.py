#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试lxml解析方式"""

import asyncio
import sys
import os
import re
from lxml import etree

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/app'))

from async_worker import _fetch_html


async def test_lxml_parse():
    """测试lxml解析"""
    url = "https://mp.weixin.qq.com/s/GJqYm3DPekQgQiEyc9nL_g"
    
    try:
        html = await _fetch_html(url)
        
        # 使用lxml解析
        parser = etree.HTMLParser(encoding='utf-8')
        tree = etree.fromstring(html, parser)
        
        # 获取文本（与async_worker相同方式）
        text = " ".join(tree.xpath('//text()'))
        print(f"文本长度: {len(text)}")
        
        # 查找同学
        student_pattern = re.compile(r'([A-Za-z]{1}[\u4e00-\u9fa5]?(?:同学)|[\u4e00-\u9fa5]{2,3}(?:同学))')
        students = student_pattern.findall(text)
        print(f"\n找到 {len(students)} 个同学: {students}")
        
        # 找包含"L同学"的句子
        sentences = re.split(r'[。！?；;\n]', text)
        for sentence in sentences[:30]:
            if 'L同学' in sentence or 'W同学' in sentence:
                print(f"\n找到: {repr(sentence[:80])}")
                
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_lxml_parse())