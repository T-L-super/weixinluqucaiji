#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量采集微信文章并写入数据库 - 修复版
"""

import sys
import os
from datetime import datetime

# 添加路径
COLLECTOR_DIR = '/root/.openclaw/workspace/大学录取信息整理系统/collector'
BACKEND_DIR = '/root/.openclaw/workspace/大学录取信息整理系统/backend'
sys.path.insert(0, COLLECTOR_DIR)
sys.path.insert(0, BACKEND_DIR)

from wechat_collector import WeChatArticleCollector
from extractor import WeChatArticleExtractor
from app.models import engine, AdmissionRecord, Country, University, SourceSchool
from sqlalchemy.orm import sessionmaker

# 链接列表
URLS = [
    'https://mp.weixin.qq.com/s/n0qZSkqMT1JcfuEuta_KuA',
    'https://mp.weixin.qq.com/s/dD43FQMBAv8ZWOCee_HQcQ',
    'https://mp.weixin.qq.com/s/sBOL-KpP9iwDGlUgbVZvHQ',
    'https://mp.weixin.qq.com/s/Xk_UkOiDuS0DsZBYfP1-eQ',
    'https://mp.weixin.qq.com/s/n9wLMcsi8ISUhd_IlM8dSQ',
    'https://mp.weixin.qq.com/s/IEiEdJUNMWe59I806p0sHg',
    'https://mp.weixin.qq.com/s/5F_ilOxMUVjVY6CkeznxIA',
    'https://mp.weixin.qq.com/s/No4dcs0CzwznuLH8W2Qwdw',
    'https://mp.weixin.qq.com/s/Co9qIpzhwkRcIQFNuFSg0g',
    'https://mp.weixin.qq.com/s/OhRBnXQCEpwQ_WtnXJAANg',
    'https://mp.weixin.qq.com/s/3K7di8ooQy2zts1gMmKS_Q',
    'https://mp.weixin.qq.com/s/BuxfeJPFYm4Y6OTv_FVbig',
    'https://mp.weixin.qq.com/s/G8tuG-VfjdJiplUbUpf4DQ'
]

def main():
    print(f"🚀 开始批量采集，共 {len(URLS)} 个链接")
    print("=" * 60)
    
    # 创建数据库会话
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    # 创建提取器
    extractor = WeChatArticleExtractor()
    
    total_records = 0
    success_count = 0
    fail_count = 0
    all_records = []
    
    for i, url in enumerate(URLS, 1):
        print(f"\n[{i}/{len(URLS)}] 采集：{url}")
        
        try:
            # 抓取文章
            collector = WeChatArticleCollector()
            article_result = collector.fetch_article(url)
            
            if not article_result:
                print(f"  ❌ 抓取失败")
                fail_count += 1
                continue
            
            # 获取 HTML 内容
            if hasattr(article_result, 'html'):
                html = article_result.html
            elif hasattr(article_result, 'content'):
                html = article_result.content
            else:
                html = str(article_result)
            
            if not html:
                print(f"  ❌ 内容为空")
                fail_count += 1
                continue
            
            # 提取数据
            result = extractor.extract(html, url)
            
            # 兼容返回格式
            if isinstance(result, list):
                records = result
                article_title = getattr(article_result, 'title', '')
            elif isinstance(result, dict):
                records = result.get('records', [])
                article_title = result.get('article_title', '')
            else:
                records = []
            
            if not records:
                print(f"  ⚠️  未提取到数据")
                fail_count += 1
                continue
            
            print(f"  ✅ 提取到 {len(records)} 条记录")
            
            # 先收集所有记录，稍后统一写入
            for record_data in records:
                if hasattr(record_data, 'to_dict'):
                    record_data = record_data.to_dict()
                
                if isinstance(record_data, dict):
                    all_records.append({
                        'data': record_data,
                        'article_title': article_title,
                        'url': url
                    })
                else:
                    all_records.append({
                        'data': {
                            'student_name': getattr(record_data, 'student_name_cn', '') or getattr(record_data, 'student_name', ''),
                            'student_name_en': getattr(record_data, 'student_name_en', ''),
                            'university': getattr(record_data, 'university_cn', '') or getattr(record_data, 'university', ''),
                            'university_en': getattr(record_data, 'university_en', ''),
                            'major': getattr(record_data, 'major_cn', '') or getattr(record_data, 'major', ''),
                            'major_en': getattr(record_data, 'major_en', ''),
                            'scholarship_amount': getattr(record_data, 'scholarship_amount', None),
                            'scholarship_currency': getattr(record_data, 'scholarship_currency', 'USD'),
                            'admission_year': getattr(record_data, 'admission_year', datetime.now().year),
                            'country': getattr(record_data, 'country', ''),
                            'source_school': getattr(record_data, 'source_school', ''),
                        },
                        'article_title': article_title,
                        'url': url
                    })
            
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ 错误：{str(e)}")
            fail_count += 1
    
    # 统一写入数据库
    print(f"\n{'='*60}")
    print(f"📝 开始写入数据库，共 {len(all_records)} 条记录...")
    
    for item in all_records:
        record_data = item['data']
        article_title = item['article_title']
        url = item['url']
        
        try:
            # 查找或创建国家
            country_name = record_data.get('country', '')
            country = db.query(Country).filter(Country.name == country_name).first()
            if not country and country_name:
                country = Country(name=country_name)
                db.add(country)
                db.flush()
            
            # 查找或创建大学
            uni_name = record_data.get('university', '')
            university = db.query(University).filter(University.name == uni_name).first()
            if not university and uni_name:
                university = University(
                    name=uni_name,
                    name_en=record_data.get('university_en', ''),
                    country_id=country.id if country else None
                )
                db.add(university)
                db.flush()
            
            # 查找或创建来源学校
            source_name = record_data.get('source_school', '')
            source_school = db.query(SourceSchool).filter(SourceSchool.name == source_name).first()
            if not source_school and source_name:
                source_school = SourceSchool(name=source_name)
                db.add(source_school)
                db.flush()
            
            # 跳过没有大学的记录
            uni_name = record_data.get('university', '')
            if not uni_name:
                print(f"  ⚠️  跳过无效记录（无大学信息）")
                continue
            
            # 创建录取记录
            scholarship_info = ''
            if record_data.get('scholarship_amount'):
                scholarship_info = f"${record_data['scholarship_amount']}"
            
            record = AdmissionRecord(
                student_name=record_data.get('student_name', ''),
                student_name_en=record_data.get('student_name_en', ''),
                university_id=university.id if university else None,
                major=record_data.get('major', ''),
                scholarship=scholarship_info,
                scholarship_amount=record_data.get('scholarship_amount'),
                admission_year=record_data.get('admission_year', datetime.now().year),
                country_id=country.id if country else None,
                source_school_id=source_school.id if source_school else None,
                article_url=url,
                article_title=article_title,
                is_verified=False
            )
            db.add(record)
            total_records += 1
            print(f"  📝 写入：{record_data.get('student_name', 'Unknown')} -> {uni_name}")
            
        except Exception as e:
            print(f"  ⚠️  写入失败：{str(e)}")
            db.rollback()
    
    db.commit()
    db.close()
    
    print("\n" + "=" * 60)
    print(f"✅ 采集完成！")
    print(f"   总链接数：{len(URLS)}")
    print(f"   成功：{success_count}")
    print(f"   失败：{fail_count}")
    print(f"   写入数据库：{total_records} 条记录")

if __name__ == '__main__':
    main()
