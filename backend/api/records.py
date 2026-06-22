# 完成时间：2026-03-18 23:27 UTC
import os
"""
录取记录 API 路由
提供录取记录的增删改查功能
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))
from app.models import get_db, AdmissionRecord as DBAdmissionRecord
from app.schemas import (
    AdmissionRecordCreate, AdmissionRecordUpdate, AdmissionRecord,
    AdmissionRecordResponse, PaginatedResponse
)

router = APIRouter(prefix="/records", tags=["录取记录"])


@router.get("", response_model=PaginatedResponse)
def get_records(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    student_name: Optional[str] = Query(None, description="学生姓名"),
    university_name: Optional[str] = Query(None, description="大学名称"),
    country: Optional[str] = Query(None, description="国家"),
    admission_year: Optional[int] = Query(None, description="录取年份"),
    data_source: Optional[str] = Query(None, description="数据来源"),
    major: Optional[str] = Query(None, description="专业"),
    year_start: Optional[int] = Query(None, ge=2000, le=2100, description="年份范围开始"),
    year_end: Optional[int] = Query(None, ge=2000, le=2100, description="年份范围结束"),
    db: Session = Depends(get_db)
):
    """
    查询录取记录列表（支持多条件组合筛选）
    """
    query = db.query(DBAdmissionRecord)
    
    # 应用筛选条件 - 使用数据库实际字段名
    if student_name:
        query = query.filter(DBAdmissionRecord.student_name_cn.contains(student_name))
    if university_name:
        query = query.filter(DBAdmissionRecord.university_cn.contains(university_name))
    if country:
        query = query.filter(DBAdmissionRecord.country.contains(country))
    if admission_year:
        query = query.filter(DBAdmissionRecord.admission_year == admission_year)
    if data_source:
        query = query.filter(DBAdmissionRecord.data_source.contains(data_source))
    if major:
        query = query.filter(DBAdmissionRecord.major_cn.contains(major))
    
    # 年份范围筛选
    if year_start:
        query = query.filter(DBAdmissionRecord.admission_year >= year_start)
    if year_end:
        query = query.filter(DBAdmissionRecord.admission_year <= year_end)
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    offset = (page - 1) * page_size
    records = query.order_by(DBAdmissionRecord.created_at.desc()).offset(offset).limit(page_size).all()
    
    # 计算总页数
    total_pages = (total + page_size - 1) // page_size
    
    # 转换为字典列表
    records_data = []
    for record in records:
        record_dict = {
            "id": record.id,
            "student_name_cn": record.student_name_cn,
            "student_name_en": record.student_name_en,
            "data_source": record.data_source,
            "country": record.country,
            "university_cn": record.university_cn,
            "university_en": record.university_en,
            "major_cn": record.major_cn,
            "major_en": record.major_en,
            "admission_type": record.admission_type,
            "admission_status": record.admission_status,
            "admission_year": record.admission_year,
            "article_url": record.article_url,
            "article_title": record.article_title,
            "scholarship_amount": record.scholarship_amount,
            "scholarship_currency": record.scholarship_currency,
            "created_at": record.created_at.isoformat() if record.created_at else None,
            "updated_at": record.updated_at.isoformat() if record.updated_at else None,
            "recognition_model": record.recognition_model,
        }
        records_data.append(record_dict)
    
    return {
        "success": True,
        "message": "操作成功",
        "records": records_data,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@router.get("/{record_id}", response_model=AdmissionRecordResponse)
def get_record(record_id: int, db: Session = Depends(get_db)):
    """获取单条录取记录详情"""
    record = db.query(DBAdmissionRecord).filter(DBAdmissionRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return record


@router.post("", response_model=AdmissionRecordResponse)
def create_record(record: AdmissionRecordCreate, db: Session = Depends(get_db)):
    """创建新的录取记录"""
    db_record = DBAdmissionRecord(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


@router.put("/{record_id}", response_model=AdmissionRecordResponse)
def update_record(record_id: int, record: AdmissionRecordUpdate, db: Session = Depends(get_db)):
    """更新录取记录"""
    db_record = db.query(DBAdmissionRecord).filter(DBAdmissionRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    for key, value in record.dict(exclude_unset=True).items():
        setattr(db_record, key, value)
    
    db.commit()
    db.refresh(db_record)
    return db_record


@router.delete("/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)):
    """删除录取记录"""
    db_record = db.query(DBAdmissionRecord).filter(DBAdmissionRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    db.delete(db_record)
    db.commit()
    return {"message": "删除成功"}
