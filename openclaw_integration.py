#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 集成接口
功能：通过 OpenClaw 技能调用采集能力，实现微信文章自动采集
创建时间：2026-03-19 18:30 CST
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / 'collector'))

from extractor import WeChatArticleExtractor
from wechat_collector import WeChatArticleCollector


def collect_from_url(url: str) -> dict:
    """
    从微信文章 URL 采集录取信息
    
    Args:
        url: 微信文章链接
    
    Returns:
        dict: 采集结果
    """
    print(f"🔄 开始采集：{url}")
    
    result = {
        'success': False,
        'url': url,
        'records': [],
        'error': None,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        # 使用采集器获取文章
        collector = WeChatArticleCollector()
        html = collector.fetch_article(url)
        
        if not html:
            result['error'] = '无法获取文章内容'
            return result
        
        # 使用提取器解析数据
        extractor = WeChatArticleExtractor()
        records = extractor.extract(html, url)
        
        if not records:
            result['error'] = '未提取到录取信息'
            return result
        
        # 转换记录格式
        result['records'] = [r.to_dict() for r in records]
        result['success'] = True
        
        print(f"✅ 采集成功：{len(records)} 条记录")
        for r in records:
            print(f"  - {r.student_name_cn} → {r.university_cn} ({r.major_cn})")
        
    except Exception as e:
        result['error'] = str(e)
        print(f"❌ 采集失败：{e}")
    
    return result


def save_to_database(records: list) -> dict:
    """
    保存录取记录到数据库
    
    Args:
        records: 录取记录列表
    
    Returns:
        dict: 保存结果
    """
    import sqlite3
    
    db_path = Path(__file__).parent / 'data' / 'admission_system.db'
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    result = {
        'success': False,
        'saved': 0,
        'skipped': 0,
        'error': None
    }
    
    try:
        for record in records:
            # 检查是否已存在
            cursor.execute(
                "SELECT id FROM admission_records WHERE article_url = ? AND student_name = ?",
                [record.get('article_url', ''), record.get('student_name_cn', '')]
            )
            
            if cursor.fetchone():
                result['skipped'] += 1
                continue
            
            # 插入新记录
            cursor.execute('''
                INSERT INTO admission_records (
                    student_name, student_name_en, source_school, country,
                    university, university_en, major, major_en,
                    scholarship_type, scholarship_amount,
                    admission_year, article_url, article_title, is_verified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', [
                record.get('student_name_cn', ''),
                record.get('student_name_en', ''),
                record.get('source_school', ''),
                record.get('country', ''),
                record.get('university_cn', ''),
                record.get('university_en', ''),
                record.get('major_cn', ''),
                record.get('major_en', ''),
                'Merit-based',
                record.get('scholarship_amount'),
                record.get('admission_year', datetime.now().year),
                record.get('article_url', ''),
                record.get('article_title', ''),
                0
            ])
            
            result['saved'] += 1
        
        conn.commit()
        result['success'] = True
        print(f"✅ 保存成功：{result['saved']} 条新增，{result['skipped']} 条跳过")
        
    except Exception as e:
        result['error'] = str(e)
        conn.rollback()
        print(f"❌ 保存失败：{e}")
    finally:
        conn.close()
    
    return result


def main():
    """主函数 - 支持命令行调用"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python openclaw_integration.py <微信文章 URL>")
        print("  python openclaw_integration.py --batch  # 从采集任务链接.txt 批量采集")
        sys.exit(1)
    
    if sys.argv[1] == '--batch':
        # 批量采集模式
        tasks_file = Path(__file__).parent / '采集任务链接.txt'
        if not tasks_file.exists():
            print(f"❌ 任务文件不存在：{tasks_file}")
            sys.exit(1)
        
        with open(tasks_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip().startswith('http')]
        
        print(f"📋 找到 {len(urls)} 个采集任务")
        
        all_records = []
        for url in urls:
            result = collect_from_url(url)
            if result['success']:
                all_records.extend(result['records'])
        
        if all_records:
            save_result = save_to_database(all_records)
            print(f"\n📊 总计：{len(all_records)} 条记录，保存 {save_result['saved']} 条")
        else:
            print("❌ 未采集到任何记录")
    
    else:
        # 单条采集模式
        url = sys.argv[1]
        result = collect_from_url(url)
        
        if result['success']:
            save_result = save_to_database(result['records'])
            print(f"\n📊 保存结果：{save_result['saved']} 条新增")
        else:
            print(f"❌ 采集失败：{result['error']}")


if __name__ == '__main__':
    main()
