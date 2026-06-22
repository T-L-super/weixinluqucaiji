#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调试图片提取问题"""

import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/app'))

from image_extractor import _capture_page


async def debug_image_extraction():
    url = "https://mp.weixin.qq.com/s/GJqYm3DPekQgQiEyc9nL_g"
    
    print("调试图片提取")
    print("=" * 60)
    print(f"URL: {url}")
    print()
    
    start_time = time.time()
    
    try:
        page_data = await _capture_page(url, timeout=60)
        
        capture_time = time.time() - start_time
        
        print(f"页面加载完成！用时: {capture_time:.2f} 秒")
        print(f"页面标题: {page_data['page_title']}")
        print(f"整页截图大小: {len(page_data['full_screenshot'])} bytes")
        print(f"提取图片数: {len(page_data['page_images'])}")
        
        if page_data['page_images']:
            print("\n图片详情:")
            for i, img in enumerate(page_data['page_images'], 1):
                print(f"  {i}. URL: {img['url'][:50]}...")
                print(f"     尺寸: {img['width']} x {img['height']}")
                print(f"     数据大小: {len(img['data'])} bytes")
        else:
            print("\n警告：没有提取到任何图片！")
            
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_image_extraction())
