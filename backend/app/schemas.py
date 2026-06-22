# 完成时间：2026-03-18 23:26 UTC
"""
Pydantic 数据验证模式
用于 API 请求/响应的数据验证和序列化
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


# ==================== 国家相关 ====================

class CountryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="国家名称")
    name_en: Optional[str] = Field(None, max_length=100, description="英文名称")
    continent: Optional[str] = Field(None, max_length=50, description="所属洲")
    region: Optional[str] = Field(None, max_length=100, description="地区")


class CountryCreate(CountryBase):
    pass


class CountryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    name_en: Optional[str] = Field(None, max_length=100)
    continent: Optional[str] = Field(None, max_length=50)
    region: Optional[str] = Field(None, max_length=100)


class Country(CountryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# ==================== 大学相关 ====================

class UniversityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="大学名称")
    name_en: Optional[str] = Field(None, max_length=200, description="英文名称")
    country_id: Optional[int] = Field(None, description="所属国家 ID")
    ranking_world: Optional[int] = Field(None, ge=1, description="世界排名")
    ranking_national: Optional[int] = Field(None, ge=1, description="国家排名")
    university_type: Optional[str] = Field(None, max_length=50, description="类型")
    is_target: bool = Field(False, description="是否目标院校")
    
    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError('大学名称不能为空')
        return v.strip()


class UniversityCreate(UniversityBase):
    pass


class UniversityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    name_en: Optional[str] = Field(None, max_length=200)
    country_id: Optional[int] = Field(None)
    ranking_world: Optional[int] = Field(None, ge=1)
    ranking_national: Optional[int] = Field(None, ge=1)
    university_type: Optional[str] = Field(None, max_length=50)
    is_target: Optional[bool] = Field(None)


class University(UniversityBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# ==================== 来源学校相关 ====================

class SourceSchoolBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="学校名称")
    city: Optional[str] = Field(None, max_length=100, description="城市")
    province: Optional[str] = Field(None, max_length=100, description="省份")
    contact_person: Optional[str] = Field(None, max_length=100, description="联系人")
    contact_phone: Optional[str] = Field(None, max_length=50, description="联系电话")
    official_account: Optional[str] = Field(None, max_length=100, description="公众号名称")


class SourceSchoolCreate(SourceSchoolBase):
    pass


class SourceSchoolUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    province: Optional[str] = Field(None, max_length=100)
    contact_person: Optional[str] = Field(None, max_length=100)
    contact_phone: Optional[str] = Field(None, max_length=50)
    official_account: Optional[str] = Field(None, max_length=100)


class SourceSchool(SourceSchoolBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# ==================== 录取条件相关 ====================

class AdmissionRequirementBase(BaseModel):
    university_id: int = Field(..., description="大学 ID")
    major: Optional[str] = Field(None, max_length=200, description="专业名称")
    gpa_min: Optional[float] = Field(None, ge=0, le=4.0, description="最低 GPA 要求")
    toefl_min: Optional[int] = Field(None, ge=0, le=120, description="最低 TOEFL 要求")
    ielts_min: Optional[float] = Field(None, ge=0, le=9.0, description="最低 IELTS 要求")
    sat_min: Optional[int] = Field(None, ge=400, le=1600, description="最低 SAT 要求")
    act_min: Optional[int] = Field(None, ge=1, le=36, description="最低 ACT 要求")
    gre_min: Optional[int] = Field(None, ge=130, le=340, description="最低 GRE 要求")
    gmat_min: Optional[int] = Field(None, ge=200, le=800, description="最低 GMAT 要求")
    other_requirements: Optional[str] = Field(None, description="其他要求")


class AdmissionRequirementCreate(AdmissionRequirementBase):
    pass


class AdmissionRequirementUpdate(BaseModel):
    university_id: Optional[int] = Field(None)
    major: Optional[str] = Field(None, max_length=200)
    gpa_min: Optional[float] = Field(None, ge=0, le=4.0)
    toefl_min: Optional[int] = Field(None, ge=0, le=120)
    ielts_min: Optional[float] = Field(None, ge=0, le=9.0)
    sat_min: Optional[int] = Field(None, ge=400, le=1600)
    act_min: Optional[int] = Field(None, ge=1, le=36)
    gre_min: Optional[int] = Field(None, ge=130, le=340)
    gmat_min: Optional[int] = Field(None, ge=200, le=800)
    other_requirements: Optional[str] = Field(None)


class AdmissionRequirement(AdmissionRequirementBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# ==================== 录取记录相关 ====================

class AdmissionRecordBase(BaseModel):
    # 学生信息
    student_name_cn: str = Field(..., min_length=1, max_length=100, description="学生中文名")
    student_name_en: Optional[str] = Field(None, max_length=100, description="学生英文名")
    student_grade: Optional[str] = Field(None, max_length=20, description="学生年级")
    
    # 国家信息
    country: str = Field(..., max_length=50, description="国家")
    country_en: Optional[str] = Field(None, max_length=50, description="国家英文名")
    
    # 大学信息
    university_cn: str = Field(..., max_length=200, description="大学中文名")
    university_en: Optional[str] = Field(None, max_length=200, description="大学英文名")
    university_type: Optional[str] = Field(None, max_length=50, description="大学类型")
    university_ranking: Optional[int] = Field(None, description="大学排名")
    
    # 来源学校
    data_source: Optional[str] = Field(None, max_length=200, description="数据来源（公众号）")
    
    # 专业信息
    major_cn: Optional[str] = Field(None, max_length=200, description="专业中文名")
    major_en: Optional[str] = Field(None, max_length=200, description="专业英文名")
    major_category: Optional[str] = Field(None, max_length=50, description="专业类别")
    
    # 录取信息
    admission_type: Optional[str] = Field(None, max_length=50, description="录取类型")
    admission_status: Optional[str] = Field(None, max_length=50, description="录取状态")
    conditional_offer: Optional[int] = Field(0, description="是否条件录取")
    admission_date: Optional[datetime] = Field(None, description="录取日期")
    admission_year: int = Field(..., ge=2000, le=2100, description="录取年份")
    
    # 语言成绩
    language_requirement_type: Optional[str] = Field(None, max_length=50, description="语言考试类型")
    language_score_required: Optional[str] = Field(None, max_length=50, description="语言分数要求")
    language_score_actual: Optional[str] = Field(None, max_length=50, description="实际语言分数")
    language_waived: Optional[int] = Field(0, description="是否豁免语言")
    
    # 标化考试
    sat_required: Optional[str] = Field(None, max_length=50, description="SAT要求")
    sat_actual: Optional[str] = Field(None, max_length=50, description="SAT实际分数")
    test_optional: Optional[int] = Field(0, description="是否标化可选")
    
    # 奖学金
    scholarship_amount: Optional[float] = Field(None, ge=0, description="奖学金金额")
    scholarship_currency: Optional[str] = Field(None, max_length=10, description="货币单位")
    scholarship_type: Optional[str] = Field(None, max_length=50, description="奖学金类型")
    
    # 来源信息
    article_url: str = Field(..., max_length=500, description="文章来源 URL")
    article_title: Optional[str] = Field(None, max_length=300, description="文章标题")
    publish_date: Optional[datetime] = Field(None, description="发布日期")
    
    # 系统字段
    status: Optional[int] = Field(1, description="状态")
    data_quality: Optional[int] = Field(3, ge=1, le=5, description="数据质量评分")
    notes: Optional[str] = Field(None, description="备注")
    
    @field_validator('student_name_cn')
    @classmethod
    def student_name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('学生姓名不能为空')
        return v.strip()


class AdmissionRecordCreate(AdmissionRecordBase):
    pass


class AdmissionRecordUpdate(BaseModel):
    student_name_cn: Optional[str] = Field(None, min_length=1, max_length=100)
    student_name_en: Optional[str] = Field(None, max_length=100)
    student_grade: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=50)
    country_en: Optional[str] = Field(None, max_length=50)
    university_cn: Optional[str] = Field(None, max_length=200)
    university_en: Optional[str] = Field(None, max_length=200)
    university_type: Optional[str] = Field(None, max_length=50)
    university_ranking: Optional[int] = Field(None)
    data_source: Optional[str] = Field(None, max_length=200)
    major_cn: Optional[str] = Field(None, max_length=200)
    major_en: Optional[str] = Field(None, max_length=200)
    major_category: Optional[str] = Field(None, max_length=50)
    admission_type: Optional[str] = Field(None, max_length=50)
    admission_status: Optional[str] = Field(None, max_length=50)
    conditional_offer: Optional[int] = Field(None)
    admission_date: Optional[datetime] = Field(None)
    admission_year: Optional[int] = Field(None, ge=2000, le=2100)
    language_requirement_type: Optional[str] = Field(None, max_length=50)
    language_score_required: Optional[str] = Field(None, max_length=50)
    language_score_actual: Optional[str] = Field(None, max_length=50)
    language_waived: Optional[int] = Field(None)
    sat_required: Optional[str] = Field(None, max_length=50)
    sat_actual: Optional[str] = Field(None, max_length=50)
    test_optional: Optional[int] = Field(None)
    scholarship_amount: Optional[float] = Field(None, ge=0)
    scholarship_currency: Optional[str] = Field(None, max_length=10)
    scholarship_type: Optional[str] = Field(None, max_length=50)
    article_url: Optional[str] = Field(None, max_length=500)
    article_title: Optional[str] = Field(None, max_length=300)
    publish_date: Optional[datetime] = Field(None)
    status: Optional[int] = Field(None)
    data_quality: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = Field(None)


class AdmissionRecord(AdmissionRecordBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class AdmissionRecordResponse(AdmissionRecord):
    """包含关联信息的完整响应"""
    university: Optional[University] = None
    country: Optional[Country] = None
    data_source_rel: Optional[SourceSchool] = None


# ==================== 采集任务相关 ====================

class CollectionTaskBase(BaseModel):
    url: str = Field(..., min_length=1, max_length=500, description="文章 URL")
    title: Optional[str] = Field(None, max_length=300, description="文章标题")
    source: Optional[str] = Field(None, max_length=100, description="来源公众号")
    priority: int = Field(5, ge=1, le=10, description="优先级 1-10")
    created_by: Optional[str] = Field(None, max_length=100, description="创建人")
    
    @field_validator('url')
    @classmethod
    def url_valid(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL 必须以 http:// 或 https:// 开头')
        return v


class CollectionTaskCreate(CollectionTaskBase):
    pass


class CollectionTaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=300)
    source: Optional[str] = Field(None, max_length=100)
    priority: Optional[int] = Field(None, ge=1, le=10)
    status: Optional[str] = Field(None)
    error_message: Optional[str] = Field(None)
    records_extracted: Optional[int] = Field(None, ge=0)


class CollectionTask(CollectionTaskBase):
    id: int
    status: str
    retry_count: int
    error_message: Optional[str]
    records_extracted: int
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


# ==================== 统计数据相关 ====================

class StatisticsOverview(BaseModel):
    """总体统计"""
    total_records: int = Field(0, description="总记录数")
    total_universities: int = Field(0, description="大学总数")
    total_countries: int = Field(0, description="国家总数")
    total_tasks: int = Field(0, description="任务总数")
    pending_tasks: int = Field(0, description="待处理任务")
    completed_tasks: int = Field(0, description="已完成任务")
    verified_records: int = Field(0, description="已验证记录")


class StatisticsByCountry(BaseModel):
    """按国家统计"""
    country_id: int
    country_name: str
    record_count: int
    avg_gpa: Optional[float]
    avg_toefl: Optional[float]
    scholarship_total: float


class StatisticsByUniversity(BaseModel):
    """按大学统计"""
    university_id: int
    university_name: str
    record_count: int
    country_name: str


# ==================== 通用响应 ====================

class ResponseBase(BaseModel):
    success: bool = True
    message: str = "操作成功"
    data: Optional[dict] = None


class PaginatedResponse(BaseModel):
    """分页响应"""
    success: bool = True
    message: str = "操作成功"
    records: List[dict]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    class Config:
        from_attributes = True
