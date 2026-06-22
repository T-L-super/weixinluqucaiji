#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试L同学的正则匹配"""

import re

# 测试用例
test_cases = [
    "W同学：河南理科，总分665，英语127，获得澳大录取",
    "L同学：重庆物理组总分506，英语98，获得澳科大录取",
    "W同学：河南理科，总分665，英语127，获得澳门大学录取",
    "L同学：重庆物理组总分506，英语98，获得澳门科技大学录取",
]

# 当前的正则表达式
PAT_STUDENT_ADMISSION = re.compile(r'(?:^|[，,。！?；;\s])([A-Za-z]{1}[\u4e00-\u9fa5]?(?:同学)|[\u4e00-\u9fa5]{2,3}(?:同学))[\s，,:：、\-—–]*[\s\S]{0,60}?(?:获得|斩获|收到|拿到|荣获)\s*([\u4e00-\u9fa5]+?(?:大学|学院|科大|理工|旅游|镜湖))')

# 更宽松的版本
PAT_STUDENT_ADMISSION2 = re.compile(r'([A-Za-z]{1}同学|[\u4e00-\u9fa5]{2,3}同学)[\s，,:：、\-—–]*[\s\S]*?(?:获得|斩获|收到|拿到|荣获)\s*([\u4e00-\u9fa5]+?(?:大学|学院|科大|理工|旅游|镜湖))')

print("测试正则表达式")
print("=" * 80)

for i, text in enumerate(test_cases, 1):
    print(f"\n测试用例 {i}: {text}")
    print("-" * 60)
    
    # 测试当前正则
    match = PAT_STUDENT_ADMISSION.search(text)
    if match:
        print(f"  当前正则匹配: 姓名={match.group(1)}, 大学={match.group(2)}")
    else:
        print(f"  当前正则: 未匹配")
    
    # 测试宽松版本
    match2 = PAT_STUDENT_ADMISSION2.search(text)
    if match2:
        print(f"  宽松版本匹配: 姓名={match2.group(1)}, 大学={match2.group(2)}")
    else:
        print(f"  宽松版本: 未匹配")