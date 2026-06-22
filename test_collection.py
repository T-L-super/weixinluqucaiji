#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试微信文章采集功能"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/app'))

from image_extractor import extract_from_url_with_model


async def test_collection(url: str):
    """测试采集指定URL"""
    print(f"开始测试采集: {url}")
    print("=" * 80)
    
    try:
        result = await extract_from_url_with_model(url, "qwen-vl-max", timeout=60)
        
        print(f"页面标题: {result.get('page_title', 'N/A')}")
        print(f"页面URL: {result.get('page_url', 'N/A')}")
        print(f"采集状态: {'成功' if result.get('success') else '失败'}")
        print(f"分析图片数: {result.get('images_analyzed', 0)}")
        
        if result.get('error'):
            print(f"错误信息: {result.get('error')}")
        
        records = result.get('records', [])
        print(f"\n提取到 {len(records)} 条录取记录:")
        print("-" * 80)
        
        for i, record in enumerate(records, 1):
            print(f"\n记录 {i}:")
            print(f"  学生姓名(中): {record.student_name_cn}")
            print(f"  学生姓名(英): {record.student_name_en}")
            print(f"  大学(中): {record.university_cn}")
            print(f"  大学(英): {record.university_en}")
            print(f"  专业(中): {record.major_cn}")
            print(f"  专业(英): {record.major_en}")
            print(f"  国家: {record.country}")
            print(f"  录取年份: {record.admission_year}")
            print(f"  奖学金金额: {record.scholarship_amount}")
            print(f"  奖学金货币: {record.scholarship_currency}")
            print(f"  录取类型: {record.admission_type}")
            print(f"  录取状态: {record.admission_status}")
            print(f"  来源学校: {record.source_school}")
            print(f"  文章URL: {record.article_url}")
            print(f"  图片索引: {record.source_image_index}")
        
        return result
        
    except Exception as e:
        print(f"采集过程发生异常: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    url = "https://mp.weixin.qq.com/s/GJqYm3DPekQgQiEyc9nL_g"
    
    print("微信文章采集测试")
    print("=" * 80)
    
    # 运行测试
    result = asyncio.run(test_collection(url))
    
    if result and result.get('success'):
        print("\n" + "=" * 80)
        print("测试完成: 采集成功！")
    else:
        print("\n" + "=" * 80)
        print("测试完成: 采集失败")
