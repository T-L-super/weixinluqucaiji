# -*- coding: utf-8 -*-
"""
微信文章采集器 - 大学录取信息整理系统
创建时间：2026-03-18 23:23 UTC
功能：从微信公众号文章抓取 HTML 内容，支持批量 URL 处理
"""

import requests
import re
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('WeChatCollector')


@dataclass
class ArticleResult:
    """文章采集结果"""
    url: str
    success: bool
    title: str = ''
    school: str = ''
    content: str = ''
    html: str = ''
    error: str = ''
    crawled_at: str = ''
    
    def to_dict(self) -> dict:
        return asdict(self)


class WeChatArticleCollector:
    """
    微信文章采集器
    
    支持：
    - 单篇文章抓取
    - 批量文章抓取
    - 自动重试机制
    - 反爬处理（User-Agent 伪装）
    """
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        """
        初始化采集器
        
        Args:
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        
        # 微信文章专用 User-Agent（移动端伪装）
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36 MicroMessenger/8.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    def fetch_article(self, url: str) -> ArticleResult:
        """
        抓取单篇微信文章
        
        Args:
            url: 微信文章链接
            
        Returns:
            ArticleResult: 采集结果
        """
        result = ArticleResult(
            url=url,
            success=False,
            crawled_at=datetime.now().isoformat()
        )
        
        # 验证 URL 格式
        if not self._validate_url(url):
            result.error = '无效的 URL 格式'
            logger.error(f"无效 URL: {url}")
            return result
        
        # 带重试的抓取
        for attempt in range(self.max_retries):
            try:
                logger.info(f"抓取文章 (尝试 {attempt + 1}/{self.max_retries}): {url}")
                response = self.session.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout,
                    allow_redirects=True
                )
                response.raise_for_status()
                
                # 设置编码
                response.encoding = self._detect_encoding(response)
                
                # 提取标题
                result.title = self._extract_title(response.text)
                
                # 提取学校（从标题）
                result.school = self._extract_school(result.title)
                
                # 保存内容
                result.html = response.text
                result.content = self._extract_text_content(response.text)
                result.success = True
                
                logger.info(f"抓取成功：{result.title}")
                break
                
            except requests.exceptions.Timeout:
                result.error = f'请求超时（{self.timeout}秒）'
                logger.warning(f"请求超时：{url}")
            except requests.exceptions.ConnectionError as e:
                result.error = f'连接错误：{str(e)}'
                logger.warning(f"连接错误：{url}")
            except requests.exceptions.HTTPError as e:
                result.error = f'HTTP 错误：{e.response.status_code}'
                logger.error(f"HTTP 错误：{url} - {e.response.status_code}")
                break  # HTTP 错误通常重试无效
            except Exception as e:
                result.error = f'未知错误：{str(e)}'
                logger.exception(f"未知错误：{url}")
            
            if attempt < self.max_retries - 1:
                import time
                time.sleep(2 ** attempt)  # 指数退避
        
        return result
    
    def fetch_batch(self, urls: List[str], delay: float = 1.0) -> List[ArticleResult]:
        """
        批量抓取文章
        
        Args:
            urls: URL 列表
            delay: 请求间隔（秒），避免反爬
            
        Returns:
            List[ArticleResult]: 采集结果列表
        """
        results = []
        total = len(urls)
        
        logger.info(f"开始批量抓取，共 {total} 篇文章")
        
        for i, url in enumerate(urls, 1):
            logger.info(f"进度：{i}/{total}")
            result = self.fetch_article(url)
            results.append(result)
            
            # 请求间隔（避免反爬）
            if i < total and delay > 0:
                import time
                time.sleep(delay)
        
        # 统计结果
        success_count = sum(1 for r in results if r.success)
        logger.info(f"批量抓取完成：成功 {success_count}/{total}")
        
        return results
    
    def _validate_url(self, url: str) -> bool:
        """验证 URL 格式"""
        if not url:
            return False
        
        # 微信文章 URL 模式
        wechat_pattern = r'^https?://mp\.weixin\.qq\.com/s/'
        if re.match(wechat_pattern, url):
            return True
        
        # 也允许其他 URL（可能是短链接）
        general_pattern = r'^https?://'
        return bool(re.match(general_pattern, url))
    
    def _detect_encoding(self, response: requests.Response) -> str:
        """检测网页编码"""
        # 优先使用响应头指定的编码
        if response.encoding:
            return response.encoding
        
        # 从 HTML meta 标签检测
        import re
        meta_pattern = r'<meta[^>]+charset=["\']?([^"\'>\s]+)'
        match = re.search(meta_pattern, response.text, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # 默认 UTF-8
        return 'utf-8'
    
    def _extract_title(self, html: str) -> str:
        """从 HTML 提取文章标题"""
        # 方法 1: Open Graph 标题
        og_match = re.search(r'og:title" content="([^"]*)"', html)
        if og_match:
            return og_match.group(1).strip()
        
        # 方法 2: HTML title 标签
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip()
        
        # 方法 3: 微信文章专用标题标签
        wx_match = re.search(r'rich_media_title[^>]*>([^<]+)</', html)
        if wx_match:
            return wx_match.group(1).strip()
        
        return '未知标题'
    
    def _extract_school(self, title: str) -> str:
        """从标题提取学校名称"""
        if not title or title == '未知标题':
            return '未知学校'
        
        # 常见模式：学校名 | 公众号名
        patterns = [
            r'([^\|]+)\|',           # XX 学校 | XX 公众号
            r'^(.+?) 喜报',            # XX 学校喜报
            r'^(.+?) 录取',            # XX 学校录取
            r'^(.+?) 升学',            # XX 学校升学
            r'^(.+?) offer',          # XX 学校 offer
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return '未知学校'
    
    def _extract_text_content(self, html: str) -> str:
        """从 HTML 提取纯文本内容"""
        # 移除 script 和 style 标签
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # 移除 HTML 标签
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # 清理空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 提取前 5000 字符（避免过长）
        return text[:5000].strip()


def test_collector():
    """测试采集器功能"""
    collector = WeChatArticleCollector()
    
    # 测试 URL（示例）
    test_url = 'https://mp.weixin.qq.com/s/example'
    
    print("测试微信文章采集器...")
    result = collector.fetch_article(test_url)
    print(f"结果：{result.to_dict()}")


if __name__ == '__main__':
    test_collector()
