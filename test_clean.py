#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试大学名称清理功能"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/app'))

from async_worker import _clean_university_name, _extract_records, _parse_html, _extract_title, _extract_school
import asyncio
from async_worker import _fetch_html


async def test_clean():
    test_cases = [
        "拱顶建筑便是同济大学",
        "级准同济同济大学",
        "年同济大学",
        "0001号！同济大学首封本科生录取通知书已送达",
        "喜获同济大学录取",
        "顺利拿到UCL录取",
        "斩获香港大学offer",
    ]
    
    print("测试大学名称清理功能:")
    print("=" * 60)
    for test in test_cases:
        result = _clean_university_name(test)
        print(f"原始: '{test}' -> 清理后: '{result}'")


async def test_full():
    url = "https://mp.weixin.qq.com/s/2IFX19AlXullo2wP36gcsg"
    
    print("\n\n测试完整采集流程:")
    print("=" * 60)
    
    html = await _fetch_html(url)
    tree = _parse_html(html)
    title = _extract_title(tree)
    school = _extract_school(tree)
    
    print(f"文章标题: {title}")
    print(f"来源学校: {school}")
    
    records = _extract_records(tree, school, url, title)
    print(f"\n提取到 {len(records)} 条记录:")
    for i, record in enumerate(records, 1):
        sname, uni, maj, country, source_school, article_url, article_title = record
        print(f"  {i}. 学生:{sname} | 大学:{uni} | 专业:{maj} | 国家:{country} | 来源:{source_school}")


if __name__ == "__main__":
    asyncio.run(test_clean())
    asyncio.run(test_full())
