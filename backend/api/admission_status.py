# 完成时间：2026-04-07
"""
录取信息处理状态查询 API
用于查询 MySQL 源数据中录取相关文章的处理状态
"""

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.mysql_connection import mysql_engine
from app.models import engine as sqlite_engine

router = APIRouter(prefix="/admission-status", tags=["录取信息处理状态"])


class MonthStatusResponse(BaseModel):
    """月份状态响应模型"""
    month: str
    status: str  # all_processed, partial, none, no_data
    total: int
    processed: int
    unprocessed: int


class AdmissionStatusResponse(BaseModel):
    """录取信息状态响应模型"""
    data: List[MonthStatusResponse]
    start_time: str
    end_time: str
    keywords: List[str]


class ProcessRequest(BaseModel):
    """处理请求模型"""
    month: Optional[str] = None
    start_time: str
    end_time: str
    keywords: List[str] = ["录取", "offer"]


class ProcessResponse(BaseModel):
    """处理响应模型"""
    success: bool
    message: str
    processed_count: int = 0


def get_processed_urls() -> set:
    """获取 SQLite 中已处理的 URL 集合"""
    with sqlite_engine.connect() as conn:
        result = conn.execute(text("SELECT article_url FROM admission_records WHERE article_url IS NOT NULL"))
        return set(row[0] for row in result.fetchall())


def query_source_articles(start_time: str, end_time: str, keywords: List[str]):
    """
    从 MySQL 查询源数据
    
    Args:
        start_time: 开始时间，格式 YYYY-MM-DD HH:MM:SS
        end_time: 结束时间，格式 YYYY-MM-DD HH:MM:SS
        keywords: 关键词列表
    
    Returns:
        文章列表，包含 id, title, url, create_time
    """
    # 构建关键词条件
    keyword_conditions = []
    for keyword in keywords:
        if keyword.lower() == 'offer':
            keyword_conditions.append(f"LOWER(title) LIKE '%{keyword.lower()}%'")
        else:
            keyword_conditions.append(f"title LIKE '%{keyword}%'")
    
    keyword_sql = " OR ".join(keyword_conditions) if keyword_conditions else "1=1"
    
    sql = f"""
    SELECT
        id,
        title,
        url,
        create_time
    FROM wechat_official_account_articles
    WHERE create_time >= '{start_time}'
      AND create_time < '{end_time}'
      AND ({keyword_sql})
    ORDER BY create_time ASC
    """
    
    with mysql_engine.connect() as conn:
        result = conn.execute(text(sql))
        articles = []
        for row in result.fetchall():
            articles.append({
                "id": row[0],
                "title": row[1],
                "url": row[2],
                "create_time": row[3]
            })
        return articles


def aggregate_by_month(articles: List[dict], processed_urls: set) -> List[dict]:
    """
    按月份聚合文章数据
    
    Args:
        articles: 文章列表
        processed_urls: 已处理的 URL 集合
    
    Returns:
        按月聚合的状态列表
    """
    from collections import defaultdict
    
    # 按月份分组
    month_data = defaultdict(lambda: {"total": 0, "processed": 0, "unprocessed": 0, "urls": []})
    
    for article in articles:
        create_time = article["create_time"]
        if isinstance(create_time, str):
            create_time = datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")
        
        month_key = create_time.strftime("%Y-%m")
        month_data[month_key]["total"] += 1
        month_data[month_key]["urls"].append(article["url"])
        
        if article["url"] in processed_urls:
            month_data[month_key]["processed"] += 1
        else:
            month_data[month_key]["unprocessed"] += 1
    
    # 转换为列表并排序
    result = []
    for month in sorted(month_data.keys()):
        data = month_data[month]
        
        # 确定状态
        if data["total"] == 0:
            status = "no_data"
        elif data["processed"] == data["total"]:
            status = "all_processed"
        elif data["processed"] == 0:
            status = "none"
        else:
            status = "partial"
        
        result.append({
            "month": month,
            "status": status,
            "total": data["total"],
            "processed": data["processed"],
            "unprocessed": data["unprocessed"]
        })
    
    return result


@router.get("/status", response_model=AdmissionStatusResponse)
def get_admission_status(
    start_time: str = Query(default="2026-04-01 00:00:00", description="开始时间，格式：YYYY-MM-DD HH:MM:SS"),
    end_time: Optional[str] = Query(default=None, description="结束时间，格式：YYYY-MM-DD HH:MM:SS"),
    keywords: str = Query(default="录取,offer", description="关键词，用逗号分隔")
):
    """
    获取录取信息处理状态
    
    按月展示每个时间段的处理状态
    
    - **start_time**: 开始时间，默认 2026-04-01 00:00:00
    - **end_time**: 结束时间，默认当前时间
    - **keywords**: 关键词，默认 "录取,offer"
    
    返回状态说明：
    - all_processed: 该月数据全部已处理
    - partial: 该月数据部分已处理
    - none: 该月数据均未处理
    - no_data: 该月无数据
    """
    try:
        # 处理参数
        if end_time is None:
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
        if not keyword_list:
            keyword_list = ["录取", "offer"]
        
        # 获取已处理的 URL
        processed_urls = get_processed_urls()
        
        # 查询源数据
        articles = query_source_articles(start_time, end_time, keyword_list)
        
        # 按月聚合
        month_status = aggregate_by_month(articles, processed_urls)
        
        return AdmissionStatusResponse(
            data=[MonthStatusResponse(**item) for item in month_status],
            start_time=start_time,
            end_time=end_time,
            keywords=keyword_list
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/articles")
def get_month_articles(
    month: str = Query(..., description="月份，格式：YYYY-MM"),
    keywords: str = Query(default="录取,offer", description="关键词，用逗号分隔")
):
    """
    获取指定月份的详细文章列表
    
    - **month**: 月份，格式 YYYY-MM
    - **keywords**: 关键词，默认 "录取,offer"
    
    返回文章列表及处理状态
    """
    try:
        # 构建时间范围
        start_time = f"{month}-01 00:00:00"
        if month[5:7] == "12":
            end_year = int(month[:4]) + 1
            end_time = f"{end_year}-01-01 00:00:00"
        else:
            end_month = int(month[5:7]) + 1
            end_time = f"{month[:4]}-{end_month:02d}-01 00:00:00"
        
        keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
        if not keyword_list:
            keyword_list = ["录取", "offer"]
        
        # 获取已处理的 URL
        processed_urls = get_processed_urls()
        
        # 查询源数据
        articles = query_source_articles(start_time, end_time, keyword_list)
        
        # 添加处理状态
        for article in articles:
            article["is_processed"] = article["url"] in processed_urls
        
        return {
            "month": month,
            "total": len(articles),
            "processed": sum(1 for a in articles if a["is_processed"]),
            "unprocessed": sum(1 for a in articles if not a["is_processed"]),
            "articles": articles
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.post("/process", response_model=ProcessResponse)
def trigger_processing(request: ProcessRequest):
    """
    触发录取信息处理任务
    
    对符合条件且未处理的数据执行处理
    
    - **month**: 指定月份（可选，格式 YYYY-MM）
    - **start_time**: 开始时间
    - **end_time**: 结束时间
    - **keywords**: 关键词列表
    
    返回处理结果
    """
    try:
        # 如果指定了月份，则使用该月份的时间范围
        if request.month:
            start_time = f"{request.month}-01 00:00:00"
            if request.month[5:7] == "12":
                end_year = int(request.month[:4]) + 1
                end_time = f"{end_year}-01-01 00:00:00"
            else:
                end_month = int(request.month[5:7]) + 1
                end_time = f"{request.month[:4]}-{end_month:02d}-01 00:00:00"
        else:
            start_time = request.start_time
            end_time = request.end_time
        
        # 获取已处理的 URL
        processed_urls = get_processed_urls()
        
        # 查询源数据
        articles = query_source_articles(start_time, end_time, request.keywords)
        
        # 筛选未处理的文章
        unprocessed_articles = [a for a in articles if a["url"] not in processed_urls]
        
        # TODO: 调用处理流程
        # 这里可以调用现有的处理脚本或创建新的处理任务
        # 目前先返回待处理的数量
        
        return ProcessResponse(
            success=True,
            message=f"找到 {len(unprocessed_articles)} 条待处理数据",
            processed_count=len(unprocessed_articles)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")