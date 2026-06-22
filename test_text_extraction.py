#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试文本提取功能"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/app'))

from async_worker import _extract_name_from_text, _find_university


def test_text_extraction():
    """测试文本提取"""
    test_cases = [
        "W同学: 河南理科, 总分665, 英语127, 获得澳大录取",
        "L同学: 重庆物理组总分506, 英语98, 获得澳科大录取",
        "张三同学获得了哈佛大学的录取通知",
        "李四斩获牛津大学offer",
        "恭喜王五同学收到剑桥大学录取",
    ]
    
    print("文本提取测试")
    print("=" * 80)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {text}")
        print("-" * 60)
        
        name = _extract_name_from_text(text)
        print(f"  提取姓名: {name}")
        
        uni = _find_university(text)
        print(f"  提取大学: {uni}")


if __name__ == "__main__":
    test_text_extraction()