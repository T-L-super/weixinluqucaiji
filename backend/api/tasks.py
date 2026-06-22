# 完成时间：2026-03-18 23:28 UTC
"""
采集任务 API 路由
提供采集任务的创建、查询、更新功能
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))
from models import get_db, CollectionTask as DBCollectionTask
from schemas import (
    CollectionTaskCreate, CollectionTaskUpdate, CollectionTask,
    PaginatedResponse
)

router = APIRouter(prefix="/tasks", tags=["采集任务"])


@router.get("", response_model=PaginatedResponse)
def get_tasks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="任务状态：pending/processing/completed/failed"),
    priority: Optional[int] = Query(None, ge=1, le=10, description="优先级"),
    source: Optional[str] = Query(None, description="来源公众号"),
    db: Session = Depends(get_db)
):
    """
    查询采集任务列表
    
    - **page**: 页码，从 1 开始
    - **page_size**: 每页数量，最大 100
    - **status**: 按状态筛选（pending/processing/completed/failed）
    - **priority**: 按优先级筛选（1-10）
    - **source**: 按来源公众号筛选
    """
    query = db.query(DBCollectionTask)
    
    # 应用筛选条件
    if status:
        query = query.filter(DBCollectionTask.status == status)
    if priority:
        query = query.filter(DBCollectionTask.priority == priority)
    if source:
        query = query.filter(DBCollectionTask.source.contains(source))
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    offset = (page - 1) * page_size
    tasks = query.order_by(DBCollectionTask.priority.desc(), DBCollectionTask.created_at.desc()).offset(offset).limit(page_size).all()
    
    # 计算总页数
    total_pages = (total + page_size - 1) // page_size
    
    # 转换为字典列表，移除 SQLAlchemy 内部状态
    tasks_data = []
    for task in tasks:
        task_dict = task.__dict__.copy()
        task_dict.pop('_sa_instance_state', None)
        tasks_data.append(task_dict)
    
    return PaginatedResponse(
        data=tasks_data,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{task_id}", response_model=CollectionTask)
def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """
    获取单个采集任务详情
    
    - **task_id**: 任务 ID
    """
    task = db.query(DBCollectionTask).filter(DBCollectionTask.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return task


@router.post("", response_model=CollectionTask)
def create_task(
    task: CollectionTaskCreate,
    db: Session = Depends(get_db)
):
    """
    创建新的采集任务
    
    需要提供：
    - **url**: 文章 URL（必填，必须以 http:// 或 https:// 开头）
    - **title**: 文章标题（可选）
    - **source**: 来源公众号（可选）
    - **priority**: 优先级 1-10，默认 5（可选）
    - **created_by**: 创建人（可选）
    """
    # 检查 URL 是否已存在
    existing = db.query(DBCollectionTask).filter(DBCollectionTask.url == task.url).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="该 URL 的任务已存在，无需重复创建"
        )
    
    # 创建任务
    db_task = DBCollectionTask(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return db_task


@router.post("/batch")
def create_batch_tasks(
    tasks: List[CollectionTaskCreate],
    db: Session = Depends(get_db)
):
    """
    批量创建采集任务
    
    提供任务列表，一次性创建多个任务
    """
    created_tasks = []
    failed_urls = []
    
    for task_data in tasks:
        # 检查 URL 是否已存在
        existing = db.query(DBCollectionTask).filter(DBCollectionTask.url == task_data.url).first()
        
        if existing:
            failed_urls.append(task_data.url)
            continue
        
        # 创建任务
        db_task = DBCollectionTask(**task_data.model_dump())
        db.add(db_task)
        created_tasks.append(db_task)
    
    db.commit()
    
    # 刷新获取 ID
    for task in created_tasks:
        db.refresh(task)
    
    # 转换为字典列表，移除 SQLAlchemy 内部状态
    created_data = []
    for task in created_tasks:
        task_dict = task.__dict__.copy()
        task_dict.pop('_sa_instance_state', None)
        created_data.append(task_dict)
    
    return {
        "success": True,
        "message": f"成功创建 {len(created_tasks)} 个任务，{len(failed_urls)} 个任务已存在",
        "data": {
            "created": created_data,
            "failed_urls": failed_urls
        }
    }


@router.put("/{task_id}", response_model=CollectionTask)
def update_task(
    task_id: int,
    task: CollectionTaskUpdate,
    db: Session = Depends(get_db)
):
    """
    更新采集任务
    
    - **task_id**: 任务 ID
    - 提供需要更新的字段
    
    常用于：
    - 更新任务状态（processing/completed/failed）
    - 更新错误信息
    - 更新提取的记录数
    """
    db_task = db.query(DBCollectionTask).filter(DBCollectionTask.id == task_id).first()
    
    if not db_task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 更新字段
    update_data = task.model_dump(exclude_unset=True)
    
    # 如果更新状态为 processing，记录开始时间
    if update_data.get('status') == 'processing' and not db_task.started_at:
        db_task.started_at = datetime.utcnow()
    
    # 如果更新状态为 completed 或 failed，记录完成时间
    if update_data.get('status') in ['completed', 'failed'] and not db_task.completed_at:
        db_task.completed_at = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    
    return db_task


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """
    删除采集任务
    
    - **task_id**: 任务 ID
    """
    db_task = db.query(DBCollectionTask).filter(DBCollectionTask.id == task_id).first()
    
    if not db_task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    db.delete(db_task)
    db.commit()
    
    return {"success": True, "message": "删除成功"}


@router.post("/{task_id}/retry")
def retry_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """
    重试失败的任务
    
    - **task_id**: 任务 ID
    - 将任务状态重置为 pending
    - 重置错误信息
    """
    db_task = db.query(DBCollectionTask).filter(DBCollectionTask.id == task_id).first()
    
    if not db_task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    db_task.status = 'pending'
    db_task.error_message = None
    db_task.retry_count += 1
    db_task.completed_at = None
    
    db.commit()
    db.refresh(db_task)
    
    task_dict = db_task.__dict__.copy()
    task_dict.pop('_sa_instance_state', None)
    
    return {
        "success": True,
        "message": "任务已重新加入队列",
        "data": task_dict
    }
