# 完成时间：2026-03-18 23:29 UTC
import os
"""
统计数据 API 路由
提供各类统计数据的查询功能
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from typing import List, Optional
from datetime import datetime, timedelta

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))
from models import get_db, AdmissionRecord, CollectionTask, University, Country
from schemas import StatisticsOverview, StatisticsByCountry, StatisticsByUniversity

router = APIRouter(prefix="/stats", tags=["统计数据"])


@router.get("/overview", response_model=StatisticsOverview)
def get_overview_stats(db: Session = Depends(get_db)):
    """
    获取总体统计数据
    
    返回：
    - 总记录数
    - 大学总数
    - 国家总数
    - 任务总数
    - 待处理任务数
    - 已完成任务数
    - 已验证记录数
    """
    total_records = db.query(AdmissionRecord).count()
    total_universities = db.query(University).count()
    total_countries = db.query(Country).count()
    total_tasks = db.query(CollectionTask).count()
    pending_tasks = db.query(CollectionTask).filter(CollectionTask.status == 'pending').count()
    completed_tasks = db.query(CollectionTask).filter(CollectionTask.status == 'completed').count()
    verified_records = db.query(AdmissionRecord).filter(AdmissionRecord.is_verified == True).count()
    
    return StatisticsOverview(
        total_records=total_records,
        total_universities=total_universities,
        total_countries=total_countries,
        total_tasks=total_tasks,
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks,
        verified_records=verified_records
    )


@router.get("/by-country", response_model=List[StatisticsByCountry])
def get_stats_by_country(
    limit: int = Query(50, ge=1, le=200, description="返回数量限制"),
    db: Session = Depends(get_db)
):
    """
    按国家统计录取数据
    
    返回每个国家的：
    - 记录数量
    - 平均 GPA
    - 平均 TOEFL
    - 奖学金总额
    """
    results = db.query(
        Country.id,
        Country.name,
        func.count(AdmissionRecord.id).label('record_count'),
        func.avg(AdmissionRecord.gpa).label('avg_gpa'),
        func.avg(AdmissionRecord.toefl).label('avg_toefl'),
        func.coalesce(func.sum(AdmissionRecord.scholarship_amount), 0).label('scholarship_total')
    ).join(
        AdmissionRecord, Country.id == AdmissionRecord.country_id
    ).group_by(
        Country.id, Country.name
    ).order_by(
        func.count(AdmissionRecord.id).desc()
    ).limit(limit).all()
    
    return [
        StatisticsByCountry(
            country_id=row.id,
            country_name=row.name,
            record_count=row.record_count,
            avg_gpa=float(row.avg_gpa) if row.avg_gpa else None,
            avg_toefl=float(row.avg_toefl) if row.avg_toefl else None,
            scholarship_total=float(row.scholarship_total)
        )
        for row in results
    ]


@router.get("/by-university", response_model=List[StatisticsByUniversity])
def get_stats_by_university(
    limit: int = Query(50, ge=1, le=200, description="返回数量限制"),
    db: Session = Depends(get_db)
):
    """
    按大学统计录取数据
    
    返回每个大学的：
    - 记录数量
    - 所属国家
    """
    results = db.query(
        University.id,
        University.name,
        func.count(AdmissionRecord.id).label('record_count'),
        Country.name.label('country_name')
    ).join(
        AdmissionRecord, University.id == AdmissionRecord.university_id
    ).join(
        Country, University.country_id == Country.id
    ).group_by(
        University.id, University.name, Country.name
    ).order_by(
        func.count(AdmissionRecord.id).desc()
    ).limit(limit).all()
    
    return [
        StatisticsByUniversity(
            university_id=row.id,
            university_name=row.name,
            record_count=row.record_count,
            country_name=row.country_name
        )
        for row in results
    ]


@router.get("/by-year")
def get_stats_by_year(
    start_year: int = Query(2020, ge=2000, le=2100, description="起始年份"),
    end_year: int = Query(2026, ge=2000, le=2100, description="结束年份"),
    db: Session = Depends(get_db)
):
    """
    按年份统计录取趋势
    
    返回指定年份范围内的每年录取记录数
    """
    results = db.query(
        AdmissionRecord.application_year.label('year'),
        func.count(AdmissionRecord.id).label('record_count')
    ).filter(
        AdmissionRecord.application_year >= start_year,
        AdmissionRecord.application_year <= end_year
    ).group_by(
        AdmissionRecord.application_year
    ).order_by(
        AdmissionRecord.application_year
    ).all()
    
    return {
        "success": True,
        "data": [
            {"year": row.year, "record_count": row.record_count}
            for row in results
        ]
    }


@router.get("/recent")
def get_recent_stats(
    days: int = Query(30, ge=1, le=365, description="统计最近 N 天"),
    db: Session = Depends(get_db)
):
    """
    获取最近 N 天的统计数据
    
    返回：
    - 新增记录数
    - 新增任务数
    - 完成任务数
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    new_records = db.query(AdmissionRecord).filter(
        AdmissionRecord.created_at >= start_date
    ).count()
    
    new_tasks = db.query(CollectionTask).filter(
        CollectionTask.created_at >= start_date
    ).count()
    
    completed_tasks = db.query(CollectionTask).filter(
        CollectionTask.completed_at >= start_date,
        CollectionTask.status == 'completed'
    ).count()
    
    return {
        "success": True,
        "data": {
            "days": days,
            "new_records": new_records,
            "new_tasks": new_tasks,
            "completed_tasks": completed_tasks
        }
    }


@router.get("/score-distribution")
def get_score_distribution(
    score_type: str = Query("gpa", description="成绩类型：gpa/toefl/ielts/sat"),
    db: Session = Depends(get_db)
):
    """
    获取成绩分布统计
    
    支持的成绩类型：
    - gpa: GPA 分布（按 0.5 分段）
    - toefl: TOEFL 分布（按 10 分分段）
    - ielts: IELTS 分布（按 0.5 分段）
    - sat: SAT 分布（按 100 分分段）
    """
    if score_type == "gpa":
        # GPA 分布（0-4.0，按 0.5 分段）
        results = db.query(
            func.floor(AdmissionRecord.gpa * 2).label('bucket'),
            func.count(AdmissionRecord.id).label('count')
        ).filter(
            AdmissionRecord.gpa.isnot(None)
        ).group_by(
            func.floor(AdmissionRecord.gpa * 2)
        ).order_by(
            func.floor(AdmissionRecord.gpa * 2)
        ).all()
        
        distribution = [
            {"range": f"{i*0.5:.1f}-{(i+1)*0.5:.1f}", "count": 0}
            for i in range(9)  # 0-4.0
        ]
        
        for row in results:
            if 0 <= row.bucket < 9:
                distribution[int(row.bucket)]["count"] = row.count
        
        return {"success": True, "data": {"score_type": "gpa", "distribution": distribution}}
    
    elif score_type == "toefl":
        # TOEFL 分布（0-120，按 10 分分段）
        results = db.query(
            func.floor(AdmissionRecord.toefl / 10).label('bucket'),
            func.count(AdmissionRecord.id).label('count')
        ).filter(
            AdmissionRecord.toefl.isnot(None)
        ).group_by(
            func.floor(AdmissionRecord.toefl / 10)
        ).order_by(
            func.floor(AdmissionRecord.toefl / 10)
        ).all()
        
        distribution = [
            {"range": f"{i*10}-{(i+1)*10}", "count": 0}
            for i in range(12)  # 0-120
        ]
        
        for row in results:
            if 0 <= row.bucket < 12:
                distribution[int(row.bucket)]["count"] = row.count
        
        return {"success": True, "data": {"score_type": "toefl", "distribution": distribution}}
    
    elif score_type == "ielts":
        # IELTS 分布（0-9，按 0.5 分段）
        results = db.query(
            func.floor(AdmissionRecord.ielts * 2).label('bucket'),
            func.count(AdmissionRecord.id).label('count')
        ).filter(
            AdmissionRecord.ielts.isnot(None)
        ).group_by(
            func.floor(AdmissionRecord.ielts * 2)
        ).order_by(
            func.floor(AdmissionRecord.ielts * 2)
        ).all()
        
        distribution = [
            {"range": f"{i*0.5:.1f}-{(i+1)*0.5:.1f}", "count": 0}
            for i in range(18)  # 0-9
        ]
        
        for row in results:
            if 0 <= row.bucket < 18:
                distribution[int(row.bucket)]["count"] = row.count
        
        return {"success": True, "data": {"score_type": "ielts", "distribution": distribution}}
    
    elif score_type == "sat":
        # SAT 分布（400-1600，按 100 分分段）
        results = db.query(
            func.floor((AdmissionRecord.sat - 400) / 100).label('bucket'),
            func.count(AdmissionRecord.id).label('count')
        ).filter(
            AdmissionRecord.sat.isnot(None)
        ).group_by(
            func.floor((AdmissionRecord.sat - 400) / 100)
        ).order_by(
            func.floor((AdmissionRecord.sat - 400) / 100)
        ).all()
        
        distribution = [
            {"range": f"{400+i*100}-{400+(i+1)*100}", "count": 0}
            for i in range(12)  # 400-1600
        ]
        
        for row in results:
            if 0 <= row.bucket < 12:
                distribution[int(row.bucket)]["count"] = row.count
        
        return {"success": True, "data": {"score_type": "sat", "distribution": distribution}}
    
    else:
        raise HTTPException(
            status_code=400,
            detail="不支持的成绩类型，支持：gpa, toefl, ielts, sat"
        )
