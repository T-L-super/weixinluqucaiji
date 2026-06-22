# -*- coding: utf-8 -*-
"""
OpenClaw 技能入口 - 大学录取信息整理系统
创建时间：2026-03-18 23:23 UTC
更新时间：2026-05-21 (纯图片识别模式)
功能：提供 OpenClaw 可调用的技能接口，支持单任务和批量任务处理
"""

import sys
import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/admission_collector.log', encoding='utf-8')
    ]
)
logger = logging.getLogger('SkillMain')

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wechat_collector import WeChatArticleCollector, ArticleResult
from extractor import WeChatArticleExtractor, AdmissionRecord
from queue_manager import TaskQueueManager, TaskResult, process_article_task


class AdmissionCollectorSkill:
    """
    OpenClaw 技能主类
    
    提供以下功能：
    - 单篇文章采集（纯图片识别）
    - 批量文章采集（纯图片识别）
    - 任务队列管理
    - 数据提取和格式化
    """
    
    def __init__(self, redis_url: str = 'redis://localhost:6379/0', use_queue: bool = True):
        """
        初始化技能
        
        Args:
            redis_url: Redis 连接 URL（用于任务队列）
            use_queue: 是否使用任务队列（默认使用）
        """
        self.use_queue = use_queue
        self.queue_manager = None
        
        if use_queue:
            try:
                self.queue_manager = TaskQueueManager(redis_url=redis_url)
                logger.info("任务队列已初始化")
            except Exception as e:
                logger.warning(f"任务队列初始化失败，将使用同步模式：{e}")
                self.use_queue = False
        
        self.collector = WeChatArticleCollector()
        self.extractor = WeChatArticleExtractor()
    
    def collect_single(self, url: str, article_title: str = '', source_school: str = '',
                      async_mode: bool = False) -> Dict[str, Any]:
        """
        采集单篇文章（使用纯图片识别模式）
        
        Args:
            url: 微信文章 URL
            article_title: 文章标题（可选）
            source_school: 来源学校（可选）
            async_mode: 是否异步执行（使用队列）
            
        Returns:
            Dict: 采集结果
        """
        logger.info(f"开始采集单篇文章（图片识别模式）：{url}")
        
        if async_mode and self.use_queue:
            task_id = self.queue_manager.enqueue_task(
                url=url,
                article_title=article_title,
                source_school=source_school
            )
            
            return {
                'success': True,
                'mode': 'async',
                'task_id': task_id,
                'message': '任务已加入队列，异步处理中',
                'url': url
            }
        else:
            try:
                records = self.extractor.extract(
                    html_content='',
                    article_title=article_title,
                    article_url=url,
                    source_school=source_school
                )
                
                return {
                    'success': True,
                    'mode': 'sync',
                    'url': url,
                    'article_title': article_title,
                    'source_school': source_school,
                    'extracted_count': len(records),
                    'records': [r.to_dict() for r in records],
                    'crawled_at': datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.exception(f"采集失败：{e}")
                return {
                    'success': False,
                    'mode': 'sync',
                    'error': str(e),
                    'url': url
                }
    
    def collect_batch(self, urls: List[str], article_title: str = '', source_school: str = '',
                     async_mode: bool = True, delay: int = 1) -> Dict[str, Any]:
        """
        批量采集文章（使用纯图片识别模式）
        
        Args:
            urls: URL 列表
            article_title: 文章标题（可选）
            source_school: 来源学校（可选）
            async_mode: 是否异步执行
            delay: 任务间隔秒数（异步模式）
            
        Returns:
            Dict: 采集结果
        """
        logger.info(f"开始批量采集（图片识别模式），共 {len(urls)} 篇文章")
        
        if async_mode and self.use_queue:
            task_ids = self.queue_manager.enqueue_batch(
                urls=urls,
                article_title=article_title,
                source_school=source_school,
                delay=delay
            )
            
            return {
                'success': True,
                'mode': 'async',
                'total': len(urls),
                'task_ids': task_ids,
                'message': f'已加入 {len(task_ids)} 个任务到队列'
            }
        else:
            results = []
            success_count = 0
            
            for i, url in enumerate(urls, 1):
                logger.info(f"进度：{i}/{len(urls)}")
                result = self.collect_single(url, article_title, source_school, async_mode=False)
                results.append(result)
                
                if result.get('success'):
                    success_count += 1
                
                if i < len(urls):
                    import time
                    time.sleep(2)
            
            return {
                'success': True,
                'mode': 'sync',
                'total': len(urls),
                'success_count': success_count,
                'failed_count': len(urls) - success_count,
                'results': results
            }
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        查询任务状态
        
        Args:
            task_id: 任务 ID
            
        Returns:
            Dict: 任务状态
        """
        if not self.use_queue:
            return {
                'success': False,
                'error': '未启用任务队列模式'
            }
        
        status = self.queue_manager.get_task_status(task_id)
        return {
            'success': True,
            'status': status
        }
    
    def get_task_result(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务结果
        
        Args:
            task_id: 任务 ID
            
        Returns:
            Dict: 任务结果
        """
        if not self.use_queue:
            return {
                'success': False,
                'error': '未启用任务队列模式'
            }
        
        result = self.queue_manager.get_task_result(task_id)
        
        if result:
            return {
                'success': True,
                'result': result.to_dict()
            }
        else:
            return {
                'success': False,
                'error': '任务未完成或不存在'
            }
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """
        获取队列统计信息
        
        Returns:
            Dict: 统计信息
        """
        if not self.use_queue:
            return {
                'success': False,
                'error': '未启用任务队列模式'
            }
        
        stats = self.queue_manager.get_queue_stats()
        return {
            'success': True,
            'stats': stats
        }


def main():
    """主函数 - OpenClaw 技能入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='大学录取信息采集器 - OpenClaw 技能')
    parser.add_argument('--action', required=True, 
                       choices=['collect', 'batch', 'status', 'result', 'stats'],
                       help='操作类型')
    parser.add_argument('--url', help='微信文章 URL（单篇采集）')
    parser.add_argument('--urls-file', help='URL 列表文件路径（批量采集）')
    parser.add_argument('--title', help='文章标题')
    parser.add_argument('--school', help='来源学校')
    parser.add_argument('--task-id', help='任务 ID（查询状态/结果）')
    parser.add_argument('--async', dest='async_mode', action='store_true', 
                       help='异步模式（使用队列）')
    parser.add_argument('--redis', default='redis://localhost:6379/0', 
                       help='Redis URL')
    parser.add_argument('--output', help='输出文件路径')
    
    args = parser.parse_args()
    
    skill = AdmissionCollectorSkill(redis_url=args.redis)
    
    result = None
    
    try:
        if args.action == 'collect':
            if not args.url:
                print(json.dumps({'success': False, 'error': '请提供 --url 参数'}, ensure_ascii=False, indent=2))
                return
            
            result = skill.collect_single(
                url=args.url,
                article_title=args.title,
                source_school=args.school,
                async_mode=args.async_mode
            )
        
        elif args.action == 'batch':
            urls = []
            
            if args.urls_file:
                with open(args.urls_file, 'r', encoding='utf-8') as f:
                    urls = [line.strip() for line in f if line.strip()]
            elif args.url:
                urls = [args.url]
            else:
                print(json.dumps({'success': False, 'error': '请提供 --url 或 --urls-file 参数'}, ensure_ascii=False, indent=2))
                return
            
            result = skill.collect_batch(
                urls=urls,
                article_title=args.title,
                source_school=args.school,
                async_mode=args.async_mode
            )
        
        elif args.action == 'status':
            if not args.task_id:
                print(json.dumps({'success': False, 'error': '请提供 --task-id 参数'}, ensure_ascii=False, indent=2))
                return
            
            result = skill.get_task_status(args.task_id)
        
        elif args.action == 'result':
            if not args.task_id:
                print(json.dumps({'success': False, 'error': '请提供 --task-id 参数'}, ensure_ascii=False, indent=2))
                return
            
            result = skill.get_task_result(args.task_id)
        
        elif args.action == 'stats':
            result = skill.get_queue_stats()
        
        output = json.dumps(result, ensure_ascii=False, indent=2)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"结果已保存到：{args.output}")
        else:
            print(output)
        
    except Exception as e:
        logger.exception(f"执行失败：{e}")
        print(json.dumps({'success': False, 'error': str(e)}, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == '__main__':
    main()