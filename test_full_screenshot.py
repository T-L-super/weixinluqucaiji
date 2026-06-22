#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试整页截图识别"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/app'))

from image_extractor import _capture_page, _analyze_image_with_vision_model, _parse_vision_response


async def test_full_page_recognition():
    """测试整页截图识别"""
    url = "https://mp.weixin.qq.com/s/GJqYm3DPekQgQiEyc9nL_g"
    
    try:
        print(f"获取页面: {url}")
        page_data = await _capture_page(url, timeout=60)
        
        print(f"\n页面标题: {page_data['page_title']}")
        
        # 使用整页截图识别
        screenshot_data = page_data['full_screenshot']
        print(f"\n整页截图大小: {len(screenshot_data)} bytes")
        
        prompt = """你是一个专业的留学录取信息提取助手。请仔细识别图片中的所有录取信息，包括：
- 学生姓名（中文和英文）
- 录取大学（中文和英文）
- 专业（中文和英文）
- 国家/地区
- 录取年份
- 奖学金金额和货币
- 录取类型/状态
- 学生成绩（总分、英语分数等）
- 来源学校（高中）

请以 JSON 格式返回，每条记录一个对象，字段名使用：
student_name_cn, student_name_en, university_cn, university_en, 
major_cn, major_en, country, admission_year, scholarship_amount, 
scholarship_currency, admission_type, admission_status, source_school, notes

如果某些字段不确定，填"未知"。只返回 JSON 数组，不要其他文字。"""
        
        print("\n正在调用视觉模型识别整页截图...")
        vision_text = _analyze_image_with_vision_model(screenshot_data, prompt, "qwen-vl-max")
        print(f"\n视觉模型返回:\n{vision_text}")
        
        # 解析结果
        records = _parse_vision_response(vision_text)
        print(f"\n解析到 {len(records)} 条记录:")
        print("-" * 80)
        
        for i, record in enumerate(records, 1):
            print(f"\n记录 {i}:")
            print(f"  学生姓名: {record.student_name_cn}")
            print(f"  大学: {record.university_cn}")
            print(f"  大学(英): {record.university_en}")
            print(f"  国家: {record.country}")
            print(f"  奖学金: {record.scholarship_amount} {record.scholarship_currency}")
            print(f"  年份: {record.admission_year}")
            print(f"  备注: {record.source_school}")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    os.environ["DASHSCOPE_API_KEY"] = "sk-75673a5d99ee4958926294fafa233647"
    asyncio.run(test_full_page_recognition())