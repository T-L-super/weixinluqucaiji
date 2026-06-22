#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试图片识别（使用正确的字段名）"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/app'))

from image_extractor import extract_from_url_with_model


async def test_image_recognition():
    url = "https://mp.weixin.qq.com/s/GJqYm3DPekQgQiEyc9nL_g"
    
    print("测试图片识别")
    print("=" * 60)
    print(f"URL: {url}")
    print()
    
    result = await extract_from_url_with_model(url, "qwen-vl-max", timeout=120)
    
    print(f"页面标题: {result.get('page_title', '未知')}")
    print(f"识别状态: {'成功' if result.get('success') else '失败'}")
    print(f"分析图片数: {result.get('images_analyzed', 0)}")
    print(f"提取记录数: {len(result.get('records', []))}")
    print(f"错误信息: {result.get('error', '无')}")
    
    print("\n提取的记录:")
    for i, r in enumerate(result.get('records', []), 1):
        print(f"\n记录 {i}:")
        print(f"  学生: {r.student_name_cn or '未知'}")
        print(f"  大学: {r.university_cn}")
        print(f"  国家: {r.country}")
        print(f"  奖学金: {r.scholarship_amount} {r.scholarship_currency}")


if __name__ == "__main__":
    os.environ["DASHSCOPE_API_KEY"] = "sk-75673a5d99ee4958926294fafa233647"
    asyncio.run(test_image_recognition())
