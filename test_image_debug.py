#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调试图片识别问题"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/app'))

from image_extractor import _capture_page


async def debug_page_images():
    """调试页面图片提取"""
    url = "https://mp.weixin.qq.com/s/GJqYm3DPekQgQiEyc9nL_g"
    
    try:
        print(f"获取页面: {url}")
        page_data = await _capture_page(url, timeout=60)
        
        print(f"\n页面标题: {page_data['page_title']}")
        print(f"找到 {len(page_data['page_images'])} 张图片")
        
        # 打印所有图片信息
        for i, img_info in enumerate(page_data['page_images'], 1):
            print(f"\n图片 {i}:")
            print(f"  URL: {img_info['url']}")
            print(f"  尺寸: {img_info['width']} x {img_info['height']}")
            print(f"  索引: {img_info['index']}")
            print(f"  数据大小: {len(img_info.get('data', b''))} bytes")
        
        # 如果图片太少，检查页面结构
        if len(page_data['page_images']) < 3:
            print("\n图片数量较少，检查页面内容...")
            # 保存整页截图查看
            screenshot_data = page_data['full_screenshot']
            screenshot_path = os.path.join(os.path.dirname(__file__), 'full_page.png')
            with open(screenshot_path, 'wb') as f:
                f.write(screenshot_data)
            print(f"整页截图已保存到: {screenshot_path}")
            
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_page_images())