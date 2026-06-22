#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试完整的文本提取流程"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/app'))

from async_worker import _fetch_html, _parse_html, _extract_title, _extract_school, _extract_records


async def test_full_extraction():
    """测试完整的HTML提取流程"""
    url = "https://mp.weixin.qq.com/s/GJqYm3DPekQgQiEyc9nL_g"
    
    print("完整文本提取测试")
    print("=" * 80)
    
    try:
        # 抓取HTML
        print(f"\n正在抓取页面: {url}")
        html = await _fetch_html(url)
        print(f"HTML长度: {len(html)} 字符")
        
        # 解析HTML
        tree = _parse_html(html)
        
        # 提取标题和学校
        title = _extract_title(tree)
        school = _extract_school(tree)
        print(f"\n页面标题: {title}")
        print(f"来源学校: {school}")
        
        # 提取录取记录
        print("\n正在提取录取记录...")
        records = _extract_records(tree, school, url, title)
        
        print(f"\n提取到 {len(records)} 条录取记录:")
        print("-" * 80)
        
        for i, record in enumerate(records, 1):
            sname, uni, maj, country, source_school, article_url, article_title = record
            print(f"\n记录 {i}:")
            print(f"  学生姓名: {sname}")
            print(f"  录取大学: {uni}")
            print(f"  专业: {maj}")
            print(f"  国家: {country}")
            print(f"  来源: {source_school}")
        
    except Exception as e:
        print(f"提取失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_full_extraction())