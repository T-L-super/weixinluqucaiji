# -*- coding: utf-8 -*-
"""
测试文本格式提取器
使用指定的 3 个微信文章链接进行测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extractor import WeChatArticleExtractor
import requests
import re


def fetch_article(url: str) -> tuple[str, str]:
    """获取微信文章内容"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 提取标题
        title_match = re.search(r'<title[^>]*>(.*?)</title>', response.text, re.IGNORECASE)
        title = title_match.group(1) if title_match else "未知标题"
        
        return response.text, title.strip()
    except Exception as e:
        print(f"获取文章失败：{e}")
        return "", ""


def test_article(url: str, extractor: WeChatArticleExtractor):
    """测试单篇文章"""
    print(f"\n{'='*60}")
    print(f"测试文章：{url}")
    print('='*60)
    
    html, title = fetch_article(url)
    
    if not html:
        print("❌ 无法获取文章内容")
        return 0
    
    print(f"文章标题：{title}")
    
    # 提取数据
    records = extractor.extract(html, article_title=title, article_url=url)
    
    print(f"\n✅ 提取到 {len(records)} 条记录:")
    print('-'*60)
    
    for i, record in enumerate(records, 1):
        print(f"\n【记录 {i}】")
        print(f"  姓名：{record.student_name_cn}")
        print(f"  大学：{record.university_cn}")
        if record.major_cn:
            print(f"  专业：{record.major_cn}")
        if record.scholarship_amount:
            print(f"  奖学金：{record.scholarship_currency} {record.scholarship_amount}")
        if record.country:
            print(f"  国家：{record.country}")
    
    return len(records)


def main():
    """主测试函数"""
    print("="*60)
    print("大学录取信息提取器 - 文本格式测试")
    print("="*60)
    
    # 测试链接
    test_urls = [
        "https://mp.weixin.qq.com/s/n0qZSkqMT1JcfuEuta_KuA",
        "https://mp.weixin.qq.com/s/Co9qIpzhwkRcIQFNuFSg0g",
        "https://mp.weixin.qq.com/s/G8tuG-VfjdJiplUbUpf4DQ"
    ]
    
    extractor = WeChatArticleExtractor()
    
    total_records = 0
    success_count = 0
    
    for url in test_urls:
        try:
            count = test_article(url, extractor)
            total_records += count
            if count > 0:
                success_count += 1
        except Exception as e:
            print(f"\n❌ 测试失败：{e}")
    
    print(f"\n{'='*60}")
    print("测试总结")
    print('='*60)
    print(f"测试文章数：{len(test_urls)}")
    print(f"成功提取：{success_count}/{len(test_urls)}")
    print(f"总记录数：{total_records}")
    
    if total_records >= 3:
        print("\n✅ 测试通过！至少提取到 3 条记录")
    else:
        print(f"\n⚠️ 测试未达标：仅提取到 {total_records} 条记录（需要至少 3 条）")


if __name__ == '__main__':
    main()
