# -*- coding: utf-8 -*-
"""
数据提取器 - 大学录取信息整理系统 (图片识别版)
创建时间:2026-03-18 23:23 UTC
更新时间:2026-05-21 (纯图片识别模式)
功能：通过 Playwright 截图 + 大模型视觉识别提取录取信息
"""

import logging
import sys
import os
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DataExtractor')


@dataclass
class AdmissionRecord:
    """录取记录数据模型"""
    student_name_cn: str = ''
    student_name_en: str = ''
    university_cn: str = ''
    university_en: str = ''
    major_cn: str = ''
    major_en: str = ''
    scholarship_amount: Optional[float] = None
    scholarship_currency: str = 'USD'
    admission_year: int = 0
    country: str = ''
    source_school: str = ''
    article_title: str = ''
    article_url: str = ''
    notes: str = ''
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    def is_valid(self) -> bool:
        """验证记录是否有效"""
        if self.university_cn and any(kw in self.university_cn for kw in ['大学', '学院', '学校', 'University', 'College']):
            if self.student_name_cn and self.student_name_cn != '[汇总]':
                if len(self.student_name_cn) < 2 or len(self.student_name_cn) > 5:
                    return False
                if self.student_name_cn in ['学生', '同学', '他们', '我们', '获得', '录取']:
                    return False
            return True
        return False


class WeChatArticleExtractor:
    """
    微信文章录取信息提取器 (纯图片识别模式)
    
    使用 Playwright 截图 + 大模型视觉识别提取录取信息，
    不再使用正则表达式或 HTML 解析。
    """
    
    def __init__(self):
        """初始化提取器"""
        self.image_extractor = None
        self._init_image_extractor()
    
    def _init_image_extractor(self):
        """延迟初始化图片提取器"""
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'app'))
            from image_extractor import extract_from_url_with_model
            self.image_extractor = extract_from_url_with_model
            logger.info("图片提取器初始化成功")
        except Exception as e:
            logger.warning(f"图片提取器初始化失败: {e}")
    
    def extract(self, html_content: str, article_title: str = '', article_url: str = '', 
                source_school: str = '', model: str = 'qwen3.6-plus') -> List[AdmissionRecord]:
        """
        从文章提取录取信息（使用图片识别）
        
        Args:
            html_content: HTML内容（不再使用，保留兼容接口）
            article_title: 文章标题
            article_url: 文章URL（用于截图识别）
            source_school: 来源学校
            model: 大模型名称
        
        Returns:
            List[AdmissionRecord]: 提取的录取记录列表
        """
        if not self.image_extractor:
            self._init_image_extractor()
        
        if not self.image_extractor or not article_url:
            logger.warning("图片提取器未初始化或缺少URL，无法进行图片识别")
            return []
        
        logger.info(f"开始图片识别提取: {article_url}")
        
        try:
            import asyncio
            result = asyncio.run(self.image_extractor(article_url, model, timeout=30))
            
            if result.get('success') and result.get('records'):
                records = []
                for r in result['records']:
                    record = AdmissionRecord(
                        student_name_cn=r.get('student_name_cn', ''),
                        student_name_en=r.get('student_name_en', ''),
                        university_cn=r.get('university_cn', ''),
                        university_en=r.get('university_en', ''),
                        major_cn=r.get('major_cn', ''),
                        major_en=r.get('major_en', ''),
                        country=r.get('country', ''),
                        admission_year=int(r.get('admission_year', 0)) if r.get('admission_year') else 0,
                        source_school=source_school,
                        article_title=article_title or result.get('page_title', ''),
                        article_url=article_url,
                        notes=r.get('notes', '')
                    )
                    
                    # 处理奖学金
                    if r.get('scholarship_amount'):
                        try:
                            record.scholarship_amount = float(r.get('scholarship_amount'))
                        except:
                            pass
                    record.scholarship_currency = r.get('scholarship_currency', 'USD')
                    
                    if record.is_valid():
                        records.append(record)
                
                logger.info(f"图片识别完成: {len(records)} 条记录")
                return records
            else:
                logger.warning(f"图片识别未提取到有效数据: {result.get('error', '未知错误')}")
                return []
                
        except Exception as e:
            logger.error(f"图片识别失败: {e}")
            return []