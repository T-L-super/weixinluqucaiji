import re

def _extract_major(text: str) -> str:
    """从文本中提取专业信息"""
    if not text:
        return ""
    
    print(f"DEBUG: 输入文本: {text}")
    
    # 方法0: 优先查找方括号格式：【XX专业】
    m = re.search(r'【([^\]]+)专业[^\]]*】', text)
    if m:
        maj = m.group(1).strip()
        print(f"DEBUG: 方法0(方括号)匹配到: {maj}")
        if maj and len(maj) >= 2:
            return maj
    # 也支持方括号格式：【XX专业】
    m = re.search(r'\[([^\]]+)专业[^\]]*\]', text)
    if m:
        maj = m.group(1).strip()
        print(f"DEBUG: 方法0(方括号)匹配到: {maj}")
        if maj and len(maj) >= 2:
            return maj
    
    # 方法1: 直接查找"XX专业"模式，这是最常见的格式
    m = re.search(r'([\u4e00-\u9fa-zA-Z\s]{2,15}?)专业', text)
    if m:
        maj = m.group(1).strip()
        print(f"DEBUG: 方法1匹配到: {maj}")
        if maj and len(maj) >= 2:
            return maj
    
    return ""

print("=" * 80)
print("测试新的专业提取功能")
print("=" * 80)

test_cases = [
    "获得 麦吉尔大学 【国际关系专业】录取",
    "获得 不列颠哥伦比亚大学 【国际关系专业】录取",
    "获得 伊拉斯姆斯大学鹿特丹管理学院 【国际工商管理专业】 录取",
    "获得 墨尔本大学 【商科专业】 录取",
    "获得 悉尼大学 【经济学专业】 录取",
    "获得 伦敦国王学院 【会计与金融专业】录取",
    "获得 华威大学 【经济学专业】录取",
    "获得 波士顿大学 【经济学专业】录取",
]

for test in test_cases:
    print(f"\n{'=' * 80}")
    result = _extract_major(test)
    print(f"输入: {test}")
    print(f"提取结果: {'✅ ' + result if result else '❌ 无'}")
