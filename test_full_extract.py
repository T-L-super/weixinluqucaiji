#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完整测试：文本+图片识别"""

import asyncio
import time
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/app'))

from async_worker import _fetch_html, _parse_html, _extract_title, _extract_school, _extract_records
from image_extractor import extract_from_url_with_model


async def test_full_extract():
    url = "https://mp.weixin.qq.com/s/GJqYm3DPekQgQiEyc9nL_g"
    
    print("=" * 80)
    print("完整采集测试：文本+图片识别")
    print("=" * 80)
    print(f"URL: {url}")
    print()
    
    # 1. 文本提取
    print("第一部分：文本提取")
    print("-" * 80)
    text_start = time.time()
    
    html = await _fetch_html(url)
    tree = _parse_html(html)
    title = _extract_title(tree)
    school = _extract_school(tree)
    text_records = _extract_records(tree, school, url, title)
    
    text_time = time.time() - text_start
    
    print(f"文本提取完成！用时: {text_time:.2f} 秒")
    print(f"文本提取记录数: {len(text_records)} 条")
    
    # 2. 图片识别
    print("\n第二部分：图片识别")
    print("-" * 80)
    img_start = time.time()
    
    try:
        img_result = await extract_from_url_with_model(url, "qwen-vl-max", timeout=120)
        img_time = time.time() - img_start
        
        print(f"图片识别完成！用时: {img_time:.2f} 秒")
        print(f"页面标题: {img_result.get('page_title', '未知')}")
        print(f"找到图片数: {len(img_result.get('page_images', []))}")
        print(f"提取记录数: {len(img_result.get('admission_records', []))}")
        
        img_records = img_result.get('admission_records', [])
        
    except Exception as e:
        print(f"图片识别失败: {e}")
        import traceback
        traceback.print_exc()
        img_records = []
        img_time = 0
    
    # 3. 合并结果
    print("\n" + "=" * 80)
    print("最终统计")
    print("=" * 80)
    
    total_time = text_time + img_time
    total_records = len(text_records) + len(img_records)
    
    print(f"总用时: {total_time:.2f} 秒")
    print(f"文本提取: {len(text_records)} 条, {text_time:.2f} 秒")
    print(f"图片识别: {len(img_records)} 条, {img_time:.2f} 秒")
    print(f"总记录数: {total_records} 条")
    
    print("\n文本提取记录:")
    for i, r in enumerate(text_records, 1):
        print(f"  {i}. {r[0] or '未知'} - {r[1]}")
    
    if img_records:
        print("\n图片识别记录:")
        for i, r in enumerate(img_records, 1):
            print(f"  {i}. {r.get('student_name_cn', '未知')} - {r.get('university_cn', '未知')}")
    
    print("\n" + "=" * 80)
    print("测试完成！")


if __name__ == "__main__":
    asyncio.run(test_full_extract())
