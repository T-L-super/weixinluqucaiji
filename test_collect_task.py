#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试采集任务的完整流程"""

import asyncio
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/app'))

from async_worker import _fetch_html, _parse_html, _extract_title, _extract_school, _extract_records


async def test_collect():
    url = "https://mp.weixin.qq.com/s/GJqYm3DPekQgQiEyc9nL_g"
    
    print("=" * 80)
    print("采集任务测试")
    print("=" * 80)
    print(f"URL: {url}")
    print()
    
    # 1. 获取HTML
    print("步骤1: 获取HTML...")
    start_time = time.time()
    html = await _fetch_html(url)
    html_time = time.time() - start_time
    print(f"  完成！用时: {html_time:.2f} 秒")
    print(f"  HTML大小: {len(html)} 字符")
    
    # 2. 解析HTML
    print("\n步骤2: 解析HTML...")
    start_time = time.time()
    tree = _parse_html(html)
    parse_time = time.time() - start_time
    print(f"  完成！用时: {parse_time:.2f} 秒")
    
    # 3. 提取标题和学校
    print("\n步骤3: 提取标题和学校...")
    start_time = time.time()
    title = _extract_title(tree)
    school = _extract_school(tree)
    extract_info_time = time.time() - start_time
    print(f"  完成！用时: {extract_info_time:.2f} 秒")
    print(f"  标题: {title}")
    print(f"  来源学校: {school}")
    
    # 4. 提取录取记录
    print("\n步骤4: 提取录取记录...")
    start_time = time.time()
    records = _extract_records(tree, school, url, title)
    extract_records_time = time.time() - start_time
    print(f"  完成！用时: {extract_records_time:.2f} 秒")
    
    # 统计信息
    total_time = html_time + parse_time + extract_info_time + extract_records_time
    
    print("\n" + "=" * 80)
    print("采集统计")
    print("=" * 80)
    print(f"总用时: {total_time:.2f} 秒")
    print(f"提取记录数: {len(records)} 条")
    print()
    
    # 显示每条记录
    if records:
        print("录取记录详情:")
        print("-" * 80)
        for i, record in enumerate(records, 1):
            sname, uni, maj, country, source_school, article_url, article_title = record
            print(f"\n记录 {i}:")
            print(f"  学生: {sname or '未知'}")
            print(f"  大学: {uni}")
            print(f"  专业: {maj or '未知'}")
            print(f"  国家: {country or '未知'}")
            print(f"  来源: {source_school}")
    
    print("\n" + "=" * 80)
    print("测试完成！")
    
    return {
        "total_time": total_time,
        "record_count": len(records),
        "records": records
    }


if __name__ == "__main__":
    asyncio.run(test_collect())
