"""
SQLAlchemy 数据库模型定义
支持 SQLite 和 MySQL 两种数据库
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from app.db_config import get_sqlalchemy_engine

Base = declarative_base()

# 获取数据库引擎
engine = get_sqlalchemy_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Country(Base):
    """国家/地区表"""
    __tablename__ = "countries"
    
    id = Column(Integer, primary_key=True, index=True)
    name_cn = Column(String(100), unique=True, nullable=False, comment="中文名称")
    name_en = Column(String(100), comment="英文名称")
    continent = Column(String(50), comment="所属洲")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    records = relationship("AdmissionRecord", back_populates="country_rel")


class University(Base):
    """大学表"""
    __tablename__ = "universities"
    
    id = Column(Integer, primary_key=True, index=True)
    name_cn = Column(String(200), nullable=False, comment="中文名称")
    name_en = Column(String(200), comment="英文名称")
    country_id = Column(Integer, ForeignKey("countries.id"), comment="所属国家")
    ranking_world = Column(Integer, comment="世界排名")
    ranking_national = Column(Integer, comment="国家排名")
    university_type = Column(String(50), comment="类型")
    is_target = Column(Boolean, default=False, comment="是否目标院校")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    records = relationship("AdmissionRecord", back_populates="university_rel")


class SourceSchool(Base):
    """来源学校表"""
    __tablename__ = "source_schools"
    
    id = Column(Integer, primary_key=True, index=True)
    school_name = Column(String(200), unique=True, nullable=False, comment="学校名称")
    school_type = Column(String(50), comment="学校类型")
    location = Column(String(200), comment="所在地区")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    records = relationship("AdmissionRecord", back_populates="source_school_rel")


class AdmissionRecord(Base):
    """录取记录表（核心表）"""
    __tablename__ = "admission_records"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 学生信息
    student_name_cn = Column(String(100), nullable=False, comment="学生中文名")
    student_name_en = Column(String(100), comment="学生英文名")
    student_grade = Column(String(20), comment="学生年级")
    
    # 国家信息
    country = Column(String(50), nullable=False, comment="国家")
    country_en = Column(String(50), comment="国家英文名")
    
    # 大学信息
    university_cn = Column(String(200), nullable=False, comment="大学中文名")
    university_en = Column(String(200), comment="大学英文名")
    university_type = Column(String(50), comment="大学类型")
    university_ranking = Column(Integer, comment="大学排名")
    
    # 数据来源
    data_source = Column(String(200), nullable=True, comment="数据来源（公众号）")
    
    # 专业信息
    major_cn = Column(String(200), comment="专业中文名")
    major_en = Column(String(200), comment="专业英文名")
    major_category = Column(String(50), comment="专业类别")
    
    # 录取信息
    admission_type = Column(String(50), comment="录取类型")
    admission_status = Column(String(50), comment="录取状态")
    conditional_offer = Column(Integer, default=0, comment="是否条件录取")
    admission_date = Column(DateTime, comment="录取日期")
    admission_year = Column(Integer, nullable=False, comment="录取年份")
    
    # 语言成绩
    language_requirement_type = Column(String(50), comment="语言考试类型")
    language_score_required = Column(String(50), comment="语言分数要求")
    language_score_actual = Column(String(50), comment="实际语言分数")
    language_waived = Column(Integer, default=0, comment="是否豁免语言")
    
    # 标化考试
    sat_required = Column(String(50), comment="SAT要求")
    sat_actual = Column(String(50), comment="SAT实际分数")
    test_optional = Column(Integer, default=0, comment="是否标化可选")
    
    # 奖学金
    scholarship_amount = Column(Float, comment="奖学金金额")
    scholarship_currency = Column(String(10), comment="货币单位")
    scholarship_type = Column(String(50), comment="奖学金类型")
    
    # 来源信息
    article_url = Column(String(500), nullable=False, comment="文章来源 URL")
    article_title = Column(String(300), comment="文章标题")
    publish_date = Column(DateTime, comment="发布日期")
    
    # 系统字段
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Integer, default=1, comment="状态")
    data_quality = Column(Integer, default=3, comment="数据质量评分 1-5")
    notes = Column(Text, comment="备注")
    
    # 审核字段
    review_status = Column(String(20), default="pending", comment="审核状态")
    review_note = Column(Text, comment="审核备注")
    reviewed_by = Column(String(100), comment="审核人")
    reviewed_at = Column(DateTime, comment="审核时间")
    promoted_at = Column(DateTime, comment="迁入时间")
    recognition_model = Column(String(50), comment="识别模型")
    
    # 关系
    source_school_rel = relationship("SourceSchool", back_populates="records", cascade="all, delete-orphan")
    university_rel = relationship("University", back_populates="records")
    country_rel = relationship("Country", back_populates="records")
    
    __table_args__ = (
        Index('idx_admission_student', 'student_name_cn'),
        Index('idx_admission_country', 'country'),
        Index('idx_admission_university', 'university_cn'),
        Index('idx_admission_year', 'admission_year'),
        Index('idx_admission_source', 'data_source'),
    )


class CollectionTask(Base):
    """采集任务表"""
    __tablename__ = "collection_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), nullable=False, comment="文章 URL")
    title = Column(String(300), comment="文章标题")
    source = Column(String(100), comment="来源公众号")
    priority = Column(Integer, default=5, comment="优先级 1-10")
    status = Column(String(20), default='pending', comment="状态: pending/running/completed/failed")
    created_by = Column(String(100), comment="创建人")
    error_message = Column(Text, comment="错误信息")
    records_extracted = Column(Integer, default=0, comment="提取记录数")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, comment="完成时间")
    
    __table_args__ = (
        Index('idx_task_status', 'status'),
        Index('idx_task_priority', 'priority'),
    )


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(100))
    full_name = Column(String(100))
    role_id = Column(Integer, default=3)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)


class Role(Base):
    """角色表"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))
    permissions = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class AdmissionRecordStaging(Base):
    """录取记录临时表"""
    __tablename__ = "admission_records_staging"
    
    id = Column(Integer, primary_key=True, index=True)
    
    student_name_cn = Column(String(100))
    student_name_en = Column(String(100))
    student_grade = Column(String(20))
    
    country = Column(String(50))
    country_en = Column(String(50))
    
    university_cn = Column(String(200))
    university_en = Column(String(200))
    university_type = Column(String(50))
    university_ranking = Column(Integer)
    
    major_cn = Column(String(200))
    major_en = Column(String(200))
    major_category = Column(String(50))
    
    admission_type = Column(String(50))
    admission_status = Column(String(50))
    conditional_offer = Column(Integer, default=0)
    admission_date = Column(DateTime)
    admission_year = Column(Integer)
    
    language_requirement_type = Column(String(50))
    language_score_required = Column(String(50))
    language_score_actual = Column(String(50))
    language_waived = Column(Integer, default=0)
    
    sat_required = Column(String(50))
    sat_actual = Column(String(50))
    test_optional = Column(Integer, default=0)
    
    scholarship_amount = Column(Float)
    scholarship_currency = Column(String(10))
    scholarship_type = Column(String(50))
    
    source_school = Column(String(200))
    article_url = Column(String(500))
    article_title = Column(String(300))
    publish_date = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Integer, default=1)
    data_quality = Column(Integer, default=3)
    notes = Column(Text)
    review_status = Column(String(20), default="pending")
    recognition_model = Column(String(50))
    data_source = Column(String(200))


# 创建所有表（如果不存在）
Base.metadata.create_all(bind=engine)
