-- ============================================================
-- 完成时间：2026-03-18 23:22 UTC
-- 数据库：SQLite 3.x
-- 项目：大学录取信息整理系统
-- 表数量：7 张核心表
-- ============================================================

-- 启用外键约束
PRAGMA foreign_keys = ON;

-- ============================================================
-- 1. 国家/地区表 (countries)
-- ============================================================
CREATE TABLE IF NOT EXISTS countries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_cn VARCHAR(50) NOT NULL UNIQUE,
    name_en VARCHAR(50),
    continent VARCHAR(50),
    region VARCHAR(50),
    currency VARCHAR(10),
    is_popular INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 2. 大学信息表 (universities)
-- ============================================================
CREATE TABLE IF NOT EXISTS universities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_cn VARCHAR(200) NOT NULL UNIQUE,
    name_en VARCHAR(200),
    country VARCHAR(50),
    type VARCHAR(50),
    ranking_us_news INTEGER,
    ranking_qs INTEGER,
    is_target INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country) REFERENCES countries(name_cn)
);

-- ============================================================
-- 3. 来源学校表 (source_schools)
-- ============================================================
CREATE TABLE IF NOT EXISTS source_schools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_name VARCHAR(200) NOT NULL UNIQUE,
    school_type VARCHAR(50),
    city VARCHAR(100),
    province VARCHAR(100),
    country VARCHAR(50),
    is_international INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 4. 录取记录表 (admission_records) - 核心表
-- ============================================================
CREATE TABLE IF NOT EXISTS admission_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 学生信息
    student_name_cn VARCHAR(100) NOT NULL,
    student_name_en VARCHAR(100),
    student_grade VARCHAR(20),
    
    -- 国家/地区信息
    country VARCHAR(50) NOT NULL,
    country_en VARCHAR(50),
    
    -- 大学信息
    university_cn VARCHAR(200) NOT NULL,
    university_en VARCHAR(200),
    university_type VARCHAR(50),
    university_ranking INTEGER,
    
    -- 专业信息
    major_cn VARCHAR(200),
    major_en VARCHAR(200),
    major_category VARCHAR(50),
    
    -- 录取信息
    admission_type VARCHAR(50),
    admission_status VARCHAR(50),
    conditional_offer INTEGER DEFAULT 0,
    admission_date DATE,
    admission_year INTEGER NOT NULL,
    
    -- 语言要求
    language_requirement_type VARCHAR(50),
    language_score_required VARCHAR(50),
    language_score_actual VARCHAR(50),
    language_waived INTEGER DEFAULT 0,
    
    -- 标化考试
    sat_required VARCHAR(50),
    sat_actual VARCHAR(50),
    test_optional INTEGER DEFAULT 0,
    
    -- 奖学金信息
    scholarship_amount DECIMAL(10,2),
    scholarship_currency VARCHAR(10),
    scholarship_type VARCHAR(50),
    
    -- 来源信息
    source_school VARCHAR(200) NOT NULL,
    article_url VARCHAR(500) NOT NULL,
    article_title VARCHAR(300),
    publish_date DATE,
    
    -- 系统字段
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status INTEGER DEFAULT 1,
    data_quality INTEGER DEFAULT 3,
    notes TEXT,
    
    -- 外键约束
    FOREIGN KEY (country) REFERENCES countries(name_cn),
    FOREIGN KEY (university_cn) REFERENCES universities(name_cn),
    FOREIGN KEY (source_school) REFERENCES source_schools(school_name)
);

-- ============================================================
-- 5. 采集任务队列表 (collection_tasks)
-- ============================================================
CREATE TABLE IF NOT EXISTS collection_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_url VARCHAR(500) NOT NULL UNIQUE,
    source_school_id INTEGER,
    source_school_name VARCHAR(200),
    priority INTEGER DEFAULT 5,
    task_status INTEGER DEFAULT 0,
    retry_count INTEGER DEFAULT 0,
    max_retry INTEGER DEFAULT 3,
    extracted_count INTEGER DEFAULT 0,
    error_message TEXT,
    scheduled_at DATETIME,
    started_at DATETIME,
    completed_at DATETIME,
    processor VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (source_school_id) REFERENCES source_schools(id)
);

-- ============================================================
-- 6. 录取条件详情表 (admission_requirements)
-- ============================================================
CREATE TABLE IF NOT EXISTS admission_requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER NOT NULL,
    gpa_required VARCHAR(50),
    toefl_total INTEGER,
    ielts_total DECIMAL(3,1),
    sat_total INTEGER,
    act_total INTEGER,
    essay_required INTEGER DEFAULT 0,
    portfolio_required INTEGER DEFAULT 0,
    interview_required INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (record_id) REFERENCES admission_records(id) ON DELETE CASCADE
);

-- ============================================================
-- 7. 每日统计表 (statistics_daily)
-- ============================================================
CREATE TABLE IF NOT EXISTS statistics_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stat_date DATE NOT NULL UNIQUE,
    total_records INTEGER DEFAULT 0,
    records_by_country TEXT,
    records_by_university TEXT,
    records_by_major TEXT,
    avg_scholarship DECIMAL(10,2),
    top_countries TEXT,
    top_universities TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 索引设计
-- ============================================================

-- admission_records 表索引
CREATE INDEX IF NOT EXISTS idx_admission_student ON admission_records(student_name_cn);
CREATE INDEX IF NOT EXISTS idx_admission_country ON admission_records(country);
CREATE INDEX IF NOT EXISTS idx_admission_university ON admission_records(university_cn);
CREATE INDEX IF NOT EXISTS idx_admission_year ON admission_records(admission_year);
CREATE INDEX IF NOT EXISTS idx_admission_country_year ON admission_records(country, admission_year);
CREATE INDEX IF NOT EXISTS idx_admission_source ON admission_records(source_school);
CREATE INDEX IF NOT EXISTS idx_admission_created ON admission_records(created_at);

-- collection_tasks 表索引
CREATE INDEX IF NOT EXISTS idx_tasks_status_priority ON collection_tasks(task_status, priority);
CREATE INDEX IF NOT EXISTS idx_tasks_created ON collection_tasks(created_at);
CREATE INDEX IF NOT EXISTS idx_tasks_scheduled ON collection_tasks(scheduled_at);

-- admission_requirements 表索引
CREATE INDEX IF NOT EXISTS idx_requirements_record ON admission_requirements(record_id);

-- universities 表索引
CREATE INDEX IF NOT EXISTS idx_universities_country ON universities(country);
CREATE INDEX IF NOT EXISTS idx_universities_ranking ON universities(ranking_us_news);

-- countries 表索引
CREATE INDEX IF NOT EXISTS idx_countries_continent ON countries(continent);
CREATE INDEX IF NOT EXISTS idx_countries_popular ON countries(is_popular);

-- ============================================================
-- 视图设计
-- ============================================================

-- 录取记录完整视图
CREATE VIEW IF NOT EXISTS v_admission_records_full AS
SELECT 
    ar.id,
    ar.student_name_cn,
    ar.student_name_en,
    ar.student_grade,
    ar.country,
    ar.country_en,
    ar.university_cn,
    ar.university_en,
    ar.university_type,
    ar.university_ranking,
    ar.major_cn,
    ar.major_en,
    ar.major_category,
    ar.admission_type,
    ar.admission_status,
    ar.conditional_offer,
    ar.admission_date,
    ar.admission_year,
    ar.language_requirement_type,
    ar.language_score_required,
    ar.language_score_actual,
    ar.language_waived,
    ar.sat_required,
    ar.sat_actual,
    ar.test_optional,
    ar.scholarship_amount,
    ar.scholarship_currency,
    ar.scholarship_type,
    ar.source_school,
    ar.article_url,
    ar.article_title,
    ar.publish_date,
    ar.created_at,
    ar.updated_at,
    ar.status,
    ar.data_quality,
    ar.notes,
    u.type AS university_type_detail,
    u.ranking_us_news,
    u.ranking_qs,
    ss.city AS school_city,
    ss.province AS school_province,
    c.continent,
    c.currency
FROM admission_records ar
LEFT JOIN universities u ON ar.university_cn = u.name_cn
LEFT JOIN source_schools ss ON ar.source_school = ss.school_name
LEFT JOIN countries c ON ar.country = c.name_cn;

-- 按国家统计视图
CREATE VIEW IF NOT EXISTS v_stats_by_country AS
SELECT 
    country,
    COUNT(*) as total_records,
    COUNT(DISTINCT university_cn) as unique_universities,
    COUNT(DISTINCT student_name_cn) as unique_students,
    AVG(scholarship_amount) as avg_scholarship,
    MIN(admission_year) as earliest_year,
    MAX(admission_year) as latest_year
FROM admission_records
WHERE status = 1
GROUP BY country
ORDER BY total_records DESC;

-- 按大学统计视图
CREATE VIEW IF NOT EXISTS v_stats_by_university AS
SELECT 
    university_cn,
    university_en,
    country,
    COUNT(*) as total_records,
    COUNT(DISTINCT student_name_cn) as unique_students,
    AVG(scholarship_amount) as avg_scholarship,
    SUM(CASE WHEN scholarship_amount > 0 THEN 1 ELSE 0 END) as scholarship_count
FROM admission_records
WHERE status = 1
GROUP BY university_cn, university_en, country
ORDER BY total_records DESC;

-- 按年份统计视图
CREATE VIEW IF NOT EXISTS v_stats_by_year AS
SELECT 
    admission_year,
    COUNT(*) as total_records,
    COUNT(DISTINCT country) as countries_count,
    COUNT(DISTINCT university_cn) as universities_count,
    AVG(scholarship_amount) as avg_scholarship
FROM admission_records
WHERE status = 1
GROUP BY admission_year
ORDER BY admission_year DESC;

-- 待处理任务视图
CREATE VIEW IF NOT EXISTS v_pending_tasks AS
SELECT 
    id,
    article_url,
    source_school_name,
    priority,
    task_status,
    retry_count,
    max_retry,
    scheduled_at,
    created_at
FROM collection_tasks
WHERE task_status IN (0, 1)
ORDER BY priority DESC, created_at ASC;

-- ============================================================
-- 触发器 - 自动更新时间
-- ============================================================

CREATE TRIGGER IF NOT EXISTS update_admission_records_timestamp 
AFTER UPDATE ON admission_records
BEGIN
    UPDATE admission_records SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_universities_timestamp 
AFTER UPDATE ON universities
BEGIN
    UPDATE universities SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_countries_timestamp 
AFTER UPDATE ON countries
BEGIN
    UPDATE countries SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_source_schools_timestamp 
AFTER UPDATE ON source_schools
BEGIN
    UPDATE source_schools SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_admission_requirements_timestamp 
AFTER UPDATE ON admission_requirements
BEGIN
    UPDATE admission_requirements SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_statistics_daily_timestamp 
AFTER UPDATE ON statistics_daily
BEGIN
    UPDATE statistics_daily SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
