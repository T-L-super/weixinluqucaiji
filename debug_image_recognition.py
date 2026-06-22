#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""详细调试图片识别问题"""

import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/app'))

from image_extractor import _capture_page, _analyze_image_with_vision_model, _parse_vision_response


async def debug_image_recognition():
    url = "https://mp.weixin.qq.com/s/GJqYm3DPekQgQiEyc9nL_g"
    
    print("详细调试图片识别")
    print("=" * 60)
    print(f"URL: {url}")
    print()
    
    # 1. 采集页面
    print("步骤1: 采集页面...")
    page_data = await _capture_page(url, timeout=60)
    print(f"页面标题: {page_data['page_title']}")
    print(f"整页截图大小: {len(page_data['full_screenshot'])} bytes")
    print(f"提取图片数: {len(page_data['page_images'])}")
    
    # 2. 测试整页截图识别
    print("\n步骤2: 测试整页截图识别...")
    prompt = """你是一个专业的留学录取信息提取助手。请仔细识别图片中的所有录取信息，包括：
- 学生姓名（中文和英文）
- 录取大学（中文和英文）
- 国家/地区
- 奖学金金额

请以 JSON 格式返回，每条记录一个对象，字段名使用：
student_name_cn, university_cn, country, scholarship_amount

如果某些字段不确定，填"未知"。只返回 JSON 数组，不要其他文字。"""
    
    try:
        start_time = time.time()
        vision_text = _analyze_image_with_vision_model(page_data['full_screenshot'], prompt, "qwen-vl-max")
        elapsed = time.time() - start_time
        print(f"整页识别完成！用时: {elapsed:.2f} 秒")
        print(f"模型返回: {vision_text[:300]}...")
        
        records = _parse_vision_response(vision_text)
        print(f"解析到 {len(records)} 条记录")
        for r in records:
            print(f"  - {r.student_name_cn} - {r.university_cn} - {r.country}")
            
    except Exception as e:
        print(f"整页识别失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. 测试单张图片识别
    print("\n步骤3: 测试单张图片识别...")
    for i, img_info in enumerate(page_data['page_images'], 1):
        img_data = img_info.get('data')
        if not img_data or len(img_data) < 1000:
            continue
            
        print(f"\n图片 {i}: {img_info['url'][:50]}...")
        print(f"  尺寸: {img_info['width']} x {img_info['height']}")
        print(f"  数据大小: {len(img_data)} bytes")
        
        try:
            start_time = time.time()
            vision_text = _analyze_image_with_vision_model(img_data, prompt, "qwen-vl-max")
            elapsed = time.time() - start_time
            print(f"  识别完成！用时: {elapsed:.2f} 秒")
            print(f"  模型返回: {vision_text[:200]}...")
            
            records = _parse_vision_response(vision_text)
            print(f"  解析到 {len(records)} 条记录")
            
        except Exception as e:
            print(f"  识别失败: {e}")


if __name__ == "__main__":
    os.environ["DASHSCOPE_API_KEY"] = "sk-75673a5d99ee4958926294fafa233647"
    asyncio.run(debug_image_recognition())
