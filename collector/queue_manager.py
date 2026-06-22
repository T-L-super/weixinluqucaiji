# -*- coding: utf-8 -*-
"""
任务队列管理器 - 大学录取信息整理系统
创建时间：2026-03-18 23:23 UTC
更新时间：2026-05-21 (纯图片识别模式)
功能：使用 RQ + Redis 管理采集任务队列，支持重试机制和错误处理
"""

import redis
import rq
from rq import Queue, Connection, Worker, get_current_job
from rq.job import Job
from rq.registry import FailedJobRegistry
import logging
import json
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import sys
import os

# 添加父目录到路径以导入采集器和提取器
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wechat_collector import WeChatArticleCollector
from extractor import WeChatArticleExtractor, AdmissionRecord

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('QueueManager')


@dataclass
class TaskResult:
    """任务执行结果"""
    task_id: str
    success: bool
    url: str = ''
    extracted_count: int = 0
    records: List[dict] = field(default_factory=list)
    error: str = ''
    started_at: str = ''
    completed_at: str = ''
    retry_count: int = 0
    
    def to_dict(self) -> dict:
        return asdict(self)


class TaskQueueManager:
    """
    任务队列管理器
    
    使用 RQ (Redis Queue) 管理采集任务：
    - 任务入队
    - 异步执行
    - 自动重试
    - 结果存储
    - 失败处理
    """
    
    def __init__(self, redis_url: str = 'redis://localhost:6379/0', queue_name: str = 'admission_collection'):
        """
        初始化队列管理器
        
        Args:
            redis_url: Redis 连接 URL
            queue_name: 队列名称
        """
        self.redis_url = redis_url
        self.queue_name = queue_name
        self.redis_conn = None
        self.queue = None
        
        self._connect()
    
    def _connect(self):
        """连接 Redis"""
        try:
            self.redis_conn = redis.from_url(self.redis_url)
            self.queue = Queue(self.queue_name, connection=self.redis_conn)
            logger.info(f"已连接到 Redis: {self.redis_url}")
        except redis.ConnectionError as e:
            logger.error(f"Redis 连接失败：{e}")
            raise
    
    def enqueue_task(self, url: str, article_title: str = '', source_school: str = '', 
                    timeout: int = 300, retry_count: int = 3) -> str:
        """
        将采集任务加入队列
        
        Args:
            url: 微信文章 URL
            article_title: 文章标题（可选）
            source_school: 来源学校（可选）
            timeout: 任务超时时间（秒）
            retry_count: 最大重试次数
            
        Returns:
            str: 任务 ID
        """
        job = self.queue.enqueue(
            process_article_task,
            url,
            article_title,
            source_school,
            job_timeout=timeout,
            retry_on_failure=True,
            failure_ttl=86400 * 7,
            result_ttl=86400 * 30,
            ttl=86400 * 30,
        )
        
        logger.info(f"任务入队：{job.id} - {url}")
        return job.id
    
    def enqueue_batch(self, urls: List[str], article_title: str = '', source_school: str = '',
                     delay: int = 0) -> List[str]:
        """
        批量入队任务
        
        Args:
            urls: URL 列表
            article_title: 文章标题（可选）
            source_school: 来源学校（可选）
            delay: 任务延迟秒数
            
        Returns:
            List[str]: 任务 ID 列表
        """
        job_ids = []
        
        for i, url in enumerate(urls):
            job = self.queue.enqueue_in(
                timedelta(seconds=delay * i),
                process_article_task,
                url,
                article_title,
                source_school,
                job_timeout=300,
                retry_on_failure=True,
            )
            job_ids.append(job.id)
            logger.info(f"批量任务 {i + 1}/{len(urls)} 入队：{job.id}")
        
        logger.info(f"批量入队完成：共 {len(job_ids)} 个任务")
        return job_ids
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务状态
        
        Args:
            task_id: 任务 ID
            
        Returns:
            Dict: 任务状态信息
        """
        try:
            job = Job.fetch(task_id, connection=self.redis_conn)
            
            status_info = {
                'task_id': task_id,
                'status': job.get_status(),
                'created_at': job.created_at.isoformat() if job.created_at else None,
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'ended_at': job.ended_at.isoformat() if job.ended_at else None,
                'retry_count': job.retries_left if hasattr(job, 'retries_left') else 0,
            }
            
            if job.get_status() == 'finished' and job.result:
                result = job.result
                if isinstance(result, TaskResult):
                    status_info['result'] = result.to_dict()
                else:
                    status_info['result'] = result
            
            if job.get_status() == 'failed':
                status_info['error'] = job.exc_info
            
            return status_info
            
        except rq.exceptions.NoSuchJobError:
            return {'task_id': task_id, 'status': 'not_found', 'error': '任务不存在'}
    
    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """
        获取任务结果
        
        Args:
            task_id: 任务 ID
            
        Returns:
            TaskResult: 任务结果，如果不存在则返回 None
        """
        try:
            job = Job.fetch(task_id, connection=self.redis_conn)
            
            if job.get_status() == 'finished' and job.result:
                return job.result
            
            return None
            
        except rq.exceptions.NoSuchJobError:
            return None
    
    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务 ID
            
        Returns:
            bool: 是否成功取消
        """
        try:
            job = Job.fetch(task_id, connection=self.redis_conn)
            job.cancel()
            logger.info(f"任务已取消：{task_id}")
            return True
        except rq.exceptions.NoSuchJobError:
            logger.warning(f"任务不存在，无法取消：{task_id}")
            return False
    
    def get_failed_tasks(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取失败任务列表
        
        Args:
            limit: 最大返回数量
            
        Returns:
            List[Dict]: 失败任务信息列表
        """
        registry = FailedJobRegistry(self.queue_name, connection=self.redis_conn)
        failed_jobs = registry.get_job_ids()[:limit]
        
        failed_tasks = []
        for job_id in failed_jobs:
            try:
                job = Job.fetch(job_id, connection=self.redis_conn)
                failed_tasks.append({
                    'task_id': job_id,
                    'status': 'failed',
                    'error': job.exc_info,
                    'created_at': job.created_at.isoformat() if job.created_at else None,
                })
            except Exception:
                continue
        
        return failed_tasks
    
    def retry_failed_task(self, task_id: str) -> Optional[str]:
        """
        重试失败任务
        
        Args:
            task_id: 任务 ID
            
        Returns:
            str: 新任务 ID，如果失败则返回 None
        """
        try:
            job = Job.fetch(task_id, connection=self.redis_conn)
            
            if job.get_status() != 'failed':
                logger.warning(f"任务未失败，无法重试：{task_id}")
                return None
            
            args = job.args
            new_job = self.queue.enqueue(
                process_article_task,
                *args,
                job_timeout=300,
                retry_on_failure=True,
            )
            
            logger.info(f"失败任务已重试：{task_id} -> {new_job.id}")
            return new_job.id
            
        except rq.exceptions.NoSuchJobError:
            logger.warning(f"任务不存在：{task_id}")
            return None
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """
        获取队列统计信息
        
        Returns:
            Dict: 统计信息
        """
        return {
            'queue_name': self.queue_name,
            'queued_count': len(self.queue),
            'started_count': self.queue.started_job_registry.count,
            'finished_count': self.queue.finished_job_registry.count,
            'failed_count': len(self.queue.failed_job_registry),
            'scheduled_count': self.queue.scheduled_job_registry.count,
        }
    
    def clear_queue(self):
        """清空队列"""
        self.queue.empty()
        logger.info("队列已清空")


def process_article_task(url: str, article_title: str = '', source_school: str = '') -> TaskResult:
    """
    处理单篇文章采集任务（RQ 任务函数）
    使用纯图片识别模式，不再使用文本/正则提取
    
    Args:
        url: 微信文章 URL
        article_title: 文章标题
        source_school: 来源学校
        
    Returns:
        TaskResult: 任务结果
    """
    job = get_current_job()
    task_id = job.id if job else 'unknown'
    
    logger.info(f"开始处理任务 {task_id}: {url}")
    
    result = TaskResult(
        task_id=task_id,
        success=False,
        url=url,
        started_at=datetime.now().isoformat(),
        retry_count=job.retries_left if job and hasattr(job, 'retries_left') else 0,
    )
    
    try:
        extractor = WeChatArticleExtractor()
        
        records = extractor.extract(
            html_content='',
            article_title=article_title,
            article_url=url,
            source_school=source_school
        )
        
        result.success = True
        result.extracted_count = len(records)
        result.records = [r.to_dict() for r in records]
        result.completed_at = datetime.now().isoformat()
        
        logger.info(f"任务 {task_id} 完成：提取 {len(records)} 条记录")
        
    except Exception as e:
        result.error = f"处理异常：{str(e)}"
        result.completed_at = datetime.now().isoformat()
        logger.exception(f"任务 {task_id} 处理异常：{e}")
        raise
    
    return result


def start_worker(redis_url: str = 'redis://localhost:6379/0', queue_name: str = 'admission_collection'):
    """
    启动工作进程
    
    Args:
        redis_url: Redis 连接 URL
        queue_name: 队列名称
    """
    logger.info(f"启动 RQ Worker，监听队列：{queue_name}")
    
    with Connection(redis.from_url(redis_url)):
        worker = Worker([queue_name])
        worker.work(burst=False)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='任务队列管理器')
    parser.add_argument('--redis', default='redis://localhost:6379/0', help='Redis URL')
    parser.add_argument('--queue', default='admission_collection', help='队列名称')
    parser.add_argument('--worker', action='store_true', help='启动 Worker')
    parser.add_argument('--stats', action='store_true', help='显示队列统计')
    
    args = parser.parse_args()
    
    if args.worker:
        start_worker(args.redis, args.queue)
    elif args.stats:
        manager = TaskQueueManager(args.redis, args.queue)
        stats = manager.get_queue_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    else:
        print("使用方法:")
        print("  python queue_manager.py --worker    # 启动 Worker")
        print("  python queue_manager.py --stats     # 查看队列统计")