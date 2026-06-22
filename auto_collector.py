#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量采集任务执行器
功能：从任务列表读取微信文章链接 → 自动采集 → 识别提取 → 存入数据库
创建时间：2026-03-19 18:30 CST
"""

import asyncio
import aiohttp
import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import sys

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / 'collector'))

from extractor import WeChatArticleExtractor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('BatchCollector')

# 数据库路径
DB_PATH = Path(__file__).parent / 'data' / 'admission_system.db'

# 任务列表文件
TASKS_FILE = Path(__file__).parent / '采集任务链接.txt'


class BatchCollector:
    """批量采集器"""
    
    def __init__(self):
        self.extractor = WeChatArticleExtractor()
        self.db_path = DB_PATH
        self.session = None
        
    async def init_session(self):
        """初始化 HTTP 会话"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                },
                timeout=aiohttp.ClientTimeout(total=30)
            )
    
    async def close_session(self):
        """关闭 HTTP 会话"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def get_db_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def save_record(self, record: dict):
        """保存录取记录到数据库"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 检查是否已存在（根据 URL 和学生姓名）
            cursor.execute(
                "SELECT id FROM admission_records WHERE article_url = ? AND student_name = ?",
                [record.get('article_url', ''), record.get('student_name_cn', '')]
            )
            if cursor.fetchone():
                logger.info(f"⏭️  跳过已存在记录：{record.get('student_name_cn')} - {record.get('university_cn')}")
                return False
            
            # 插入新记录
            cursor.execute('''
                INSERT INTO admission_records (
                    student_name, student_name_en, source_school, country,
                    university, university_en, major, major_en,
                    scholarship_type, scholarship_amount, requirements, portfolio,
                    admission_year, article_url, article_title, is_verified, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', [
                record.get('student_name_cn', ''),
                record.get('student_name_en', ''),
                record.get('source_school', ''),
                record.get('country', ''),
                record.get('university_cn', ''),
                record.get('university_en', ''),
                record.get('major_cn', ''),
                record.get('major_en', ''),
                'Merit-based',  # 默认奖学金类型
                record.get('scholarship_amount'),
                '',  # 录取条件（待提取）
                '',  # 作品集（待提取）
                record.get('admission_year', datetime.now().year),
                record.get('article_url', ''),
                record.get('article_title', ''),
                0,  # 待验证
                datetime.now()
            ])
            
            conn.commit()
            logger.info(f"✅ 保存记录：{record.get('student_name_cn')} → {record.get('university_cn')} ({record.get('major_cn')})")
            return True
            
        except Exception as e:
            logger.error(f"❌ 保存记录失败：{e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    async def fetch_article(self, url: str) -> Optional[str]:
        """获取微信文章 HTML"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text(encoding='utf-8')
                    logger.info(f"📄 获取文章成功：{url[:50]}...")
                    return html
                else:
                    logger.warning(f"⚠️  获取文章失败 ({response.status}): {url[:50]}...")
                    return None
        except Exception as e:
            logger.error(f"❌ 获取文章异常：{e}")
            return None
    
    async def process_task(self, task: dict) -> dict:
        """处理单个采集任务"""
        url = task.get('url', '')
        task_id = task.get('id', 0)
        
        logger.info(f"🔄 开始处理任务 #{task_id}: {url[:50]}...")
        
        result = {
            'id': task_id,
            'url': url,
            'status': 'failed',
            'progress': 0,
            'records_count': 0,
            'error': None
        }
        
        try:
            # 步骤 1: 获取文章 HTML (20%)
            result['progress'] = 20
            html = await self.fetch_article(url)
            if not html:
                result['error'] = '无法获取文章内容'
                result['progress'] = 100
                return result
            
            # 步骤 2: 提取录取信息 (50%)
            result['progress'] = 50
            records = self.extractor.extract(html, url)
            
            if not records:
                result['error'] = '未提取到录取信息'
                result['progress'] = 100
                return result
            
            logger.info(f"📊 提取到 {len(records)} 条记录")
            
            # 步骤 3: 保存到数据库 (80% → 100%)
            result['progress'] = 80
            saved_count = 0
            for record in records:
                if self.save_record(record):
                    saved_count += 1
            
            result['records_count'] = saved_count
            result['status'] = 'completed'
            result['progress'] = 100
            
            logger.info(f"✅ 任务完成：{saved_count} 条记录已保存")
            
        except Exception as e:
            result['error'] = str(e)
            result['progress'] = 100
            logger.error(f"❌ 任务失败：{e}")
        
        return result
    
    def load_tasks(self) -> List[dict]:
        """从文件加载任务列表"""
        tasks = []
        
        if not TASKS_FILE.exists():
            logger.warning(f"⚠️  任务文件不存在：{TASKS_FILE}")
            return tasks
        
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and line.startswith('http'):
                tasks.append({
                    'id': i,
                    'url': line,
                    'status': 'pending',
                    'progress': 0
                })
        
        logger.info(f"📋 加载 {len(tasks)} 个采集任务")
        return tasks
    
    def update_task_status(self, result: dict):
        """更新任务状态（可选：写入数据库或文件）"""
        # 这里可以扩展到写入数据库的 tasks 表
        pass
    
    async def run(self, max_concurrent: int = 3):
        """执行批量采集"""
        logger.info("🚀 开始批量采集任务")
        
        # 加载任务
        tasks = self.load_tasks()
        if not tasks:
            logger.warning("⚠️  没有任务需要执行")
            return
        
        # 初始化 HTTP 会话
        await self.init_session()
        
        try:
            # 创建信号量控制并发
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def process_with_semaphore(task):
                async with semaphore:
                    return await self.process_task(task)
            
            # 并发执行任务
            results = await asyncio.gather(*[process_with_semaphore(task) for task in tasks])
            
            # 统计结果
            total = len(results)
            success = sum(1 for r in results if r['status'] == 'completed')
            failed = total - success
            total_records = sum(r['records_count'] for r in results)
            
            logger.info("=" * 50)
            logger.info(f"📊 采集完成统计:")
            logger.info(f"  总任务数：{total}")
            logger.info(f"  成功：{success}")
            logger.info(f"  失败：{failed}")
            logger.info(f"  新增记录：{total_records}")
            logger.info("=" * 50)
            
        finally:
            await self.close_session()


async def main():
    """主函数"""
    collector = BatchCollector()
    await collector.run(max_concurrent=3)


if __name__ == '__main__':
    asyncio.run(main())
