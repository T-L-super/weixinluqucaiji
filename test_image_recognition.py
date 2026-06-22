#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试图片识别功能"""

import asyncio
import sys
import os
import base64
import io

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/app'))

from image_extractor import _analyze_image_with_vision_model, _parse_vision_response, _img_to_base64
from PIL import Image


async def test_image_file(image_path: str):
    """测试识别本地图片文件"""
    print(f"测试识别图片: {image_path}")
    print("=" * 80)
    
    try:
        # 读取图片文件
        with open(image_path, 'rb') as f:
            img_data = f.read()
        
        print(f"图片大小: {len(img_data)} bytes")
        
        # 检查图片
        img = Image.open(io.BytesIO(img_data))
        print(f"图片尺寸: {img.width} x {img.height}")
        
        # 使用视觉模型识别
        prompt = """你是一个专业的留学录取信息提取助手。请仔细识别图片中的所有录取信息，包括：
- 学生姓名（中文和英文）
- 录取大学（中文和英文）
- 专业（中文和英文）
- 国家/地区
- 录取年份
- 奖学金金额和货币
- 录取类型/状态
- 来源学校（高中）
- 学生成绩（如总分、英语分数等）

请以 JSON 格式返回，每条记录一个对象，字段名使用：
student_name_cn, student_name_en, university_cn, university_en, 
major_cn, major_en, country, admission_year, scholarship_amount, 
scholarship_currency, admission_type, admission_status, source_school, notes

如果某些字段不确定，填"未知"。只返回 JSON 数组，不要其他文字。"""
        
        print("\n正在调用视觉模型...")
        vision_text = _analyze_image_with_vision_model(img_data, prompt, "qwen-vl-max")
        print(f"\n视觉模型返回:\n{vision_text}")
        
        # 解析结果
        records = _parse_vision_response(vision_text)
        print(f"\n解析到 {len(records)} 条记录:")
        print("-" * 80)
        
        for i, record in enumerate(records, 1):
            print(f"\n记录 {i}:")
            print(f"  学生姓名(中): {record.student_name_cn}")
            print(f"  大学(中): {record.university_cn}")
            print(f"  大学(英): {record.university_en}")
            print(f"  国家: {record.country}")
            print(f"  备注: {record.source_school}")
        
        return records
        
    except Exception as e:
        print(f"识别失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_url_images():
    """测试从URL提取的图片识别"""
    from image_extractor import _capture_page
    
    url = "https://mp.weixin.qq.com/s/GJqYm3DPekQgQiEyc9nL_g"
    
    try:
        print(f"正在获取页面图片: {url}")
        page_data = await _capture_page(url, timeout=60)
        
        print(f"\n页面标题: {page_data['page_title']}")
        print(f"找到 {len(page_data['page_images'])} 张图片")
        
        # 测试每张图片
        for i, img_info in enumerate(page_data['page_images'][:3], 1):
            print(f"\n{'='*60}")
            print(f"图片 {i}: {img_info['url'][:60]}...")
            print(f"尺寸: {img_info['width']} x {img_info['height']}")
            
            img_data = img_info.get('data')
            if img_data:
                prompt = """你是一个专业的留学录取信息提取助手。请仔细识别图片中的所有录取信息，包括：
- 学生姓名（中文和英文）
- 录取大学（中文和英文）
- 学生成绩（总分、英语等）
- 录取类型

请以 JSON 格式返回，每条记录一个对象，字段名使用：
student_name_cn, university_cn, university_en, country, notes

如果某些字段不确定，填"未知"。只返回 JSON 数组，不要其他文字。"""
                
                try:
                    vision_text = _analyze_image_with_vision_model(img_data, prompt, "qwen-vl-max")
                    print(f"识别结果:\n{vision_text[:200]}...")
                    
                    records = _parse_vision_response(vision_text)
                    if records:
                        print(f"解析到 {len(records)} 条记录")
                        for r in records:
                            print(f"  - {r.student_name_cn}: {r.university_cn}")
                except Exception as e:
                    print(f"识别失败: {e}")
        
    except Exception as e:
        print(f"获取页面失败: {e}")


if __name__ == "__main__":
    print("图片识别测试")
    print("=" * 80)
    
    # 测试URL图片识别
    asyncio.run(test_url_images())
