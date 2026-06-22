-- ============================================================
-- 完成时间：2026-05-26
-- 数据库：MySQL 8.0+
-- 项目：大学录取信息整理系统
-- 表数量：7 张核心表
-- ============================================================

-- ============================================================
-- 1. 国家/地区表 (countries)
-- ============================================================
CREATE TABLE IF NOT EXISTS countries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name_cn VARCHAR(50) NOT NULL UNIQUE,
    name_en VARCHAR(50),
    continent VARCHAR(50),
    region VARCHAR(50),
    currency VARCHAR(10),
    is_popular TINYINT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 2. 大学信息表 (universities)
-- ============================================================
CREATE TABLE IF NOT EXISTS universities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name_cn VARCHAR(200) NOT NULL UNIQUE,
    name_en VARCHAR(200),
    country VARCHAR(50),
    type VARCHAR(50),
    ranking_us_news INT,
    ranking_qs INT,
    is_target TINYINT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_universities_country (country),
    INDEX idx_universities_ranking (ranking_us_news)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 3. 来源学校表 (source_schools)
-- ============================================================
CREATE TABLE IF NOT EXISTS source_schools (
    id INT AUTO_INCREMENT PRIMARY KEY,
    school_name VARCHAR(200) NOT NULL UNIQUE,
    school_type VARCHAR(50),
    city VARCHAR(100),
    province VARCHAR(100),
    country VARCHAR(50),
    is_international TINYINT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 4. 录取记录表 (admission_records) - 核心表
-- ============================================================
CREATE TABLE IF NOT EXISTS admission_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
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
    university_ranking INT,
    
    -- 专业信息
    major_cn VARCHAR(200),
    major_en VARCHAR(200),
    major_category VARCHAR(50),
    
    -- 录取信息
    admission_type VARCHAR(50),
    admission_status VARCHAR(50),
    conditional_offer TINYINT DEFAULT 0,
    admission_date DATE,
    admission_year INT NOT NULL,
    
    -- 语言要求
    language_requirement_type VARCHAR(50),
    language_score_required VARCHAR(50),
    language_score_actual VARCHAR(50),
    language_waived TINYINT DEFAULT 0,
    
    -- 标化考试
    sat_required VARCHAR(50),
    sat_actual VARCHAR(50),
    test_optional TINYINT DEFAULT 0,
    
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
    status TINYINT DEFAULT 1,
    data_quality TINYINT DEFAULT 3,
    notes TEXT,
    review_status VARCHAR(20) DEFAULT 'pending',
    review_note TEXT,
    reviewed_by VARCHAR(100),
    reviewed_at DATETIME,
    promoted_at DATETIME,
    recognition_model VARCHAR(50),
    data_source VARCHAR(200),
    
    INDEX idx_admission_student (student_name_cn),
    INDEX idx_admission_country (country),
    INDEX idx_admission_university (university_cn),
    INDEX idx_admission_year (admission_year),
    INDEX idx_admission_country_year (country, admission_year),
    INDEX idx_admission_source (source_school),
    INDEX idx_admission_created (created_at),
    INDEX idx_admission_review_status (review_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 5. 采集任务队列表 (collection_tasks)
-- ============================================================
CREATE TABLE IF NOT EXISTS collection_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    article_url VARCHAR(500) NOT NULL UNIQUE,
    source_school_id INT,
    source_school_name VARCHAR(200),
    priority INT DEFAULT 5,
    task_status TINYINT DEFAULT 0,
    retry_count INT DEFAULT 0,
    max_retry INT DEFAULT 3,
    extracted_count INT DEFAULT 0,
    error_message TEXT,
    scheduled_at DATETIME,
    started_at DATETIME,
    completed_at DATETIME,
    processor VARCHAR(50),
    title VARCHAR(300),
    recognition_model VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_tasks_status_priority (task_status, priority),
    INDEX idx_tasks_created (created_at),
    INDEX idx_tasks_scheduled (scheduled_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 6. 录取条件详情表 (admission_requirements)
-- ============================================================
CREATE TABLE IF NOT EXISTS admission_requirements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    record_id INT NOT NULL,
    gpa_required VARCHAR(50),
    toefl_total INT,
    ielts_total DECIMAL(3,1),
    sat_total INT,
    act_total INT,
    essay_required TINYINT DEFAULT 0,
    portfolio_required TINYINT DEFAULT 0,
    interview_required TINYINT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_requirements_record (record_id),
    FOREIGN KEY (record_id) REFERENCES admission_records(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 7. 每日统计表 (statistics_daily)
-- ============================================================
CREATE TABLE IF NOT EXISTS statistics_daily (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stat_date DATE NOT NULL UNIQUE,
    total_records INT DEFAULT 0,
    records_by_country JSON,
    records_by_university JSON,
    records_by_major JSON,
    avg_scholarship DECIMAL(10,2),
    top_countries JSON,
    top_universities JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 8. 用户表 (users)
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    full_name VARCHAR(100),
    role_id INT DEFAULT 3,
    is_active TINYINT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    
    INDEX idx_users_username (username),
    INDEX idx_users_role (role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 9. 角色表 (roles)
-- ============================================================
CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(200),
    permissions TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 10. 录取记录临时表 (admission_records_staging)
-- ============================================================
CREATE TABLE IF NOT EXISTS admission_records_staging (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    student_name_cn VARCHAR(100),
    student_name_en VARCHAR(100),
    student_grade VARCHAR(20),
    
    country VARCHAR(50),
    country_en VARCHAR(50),
    
    university_cn VARCHAR(200),
    university_en VARCHAR(200),
    university_type VARCHAR(50),
    university_ranking INT,
    
    major_cn VARCHAR(200),
    major_en VARCHAR(200),
    major_category VARCHAR(50),
    
    admission_type VARCHAR(50),
    admission_status VARCHAR(50),
    conditional_offer TINYINT DEFAULT 0,
    admission_date DATE,
    admission_year INT,
    
    language_requirement_type VARCHAR(50),
    language_score_required VARCHAR(50),
    language_score_actual VARCHAR(50),
    language_waived TINYINT DEFAULT 0,
    
    sat_required VARCHAR(50),
    sat_actual VARCHAR(50),
    test_optional TINYINT DEFAULT 0,
    
    scholarship_amount DECIMAL(10,2),
    scholarship_currency VARCHAR(10),
    scholarship_type VARCHAR(50),
    
    source_school VARCHAR(200),
    article_url VARCHAR(500),
    article_title VARCHAR(300),
    publish_date DATE,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TINYINT DEFAULT 1,
    data_quality TINYINT DEFAULT 3,
    notes TEXT,
    review_status VARCHAR(20) DEFAULT 'pending',
    recognition_model VARCHAR(50),
    data_source VARCHAR(200),
    
    INDEX idx_staging_student (student_name_cn),
    INDEX idx_staging_university (university_cn)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 插入初始角色数据
-- ============================================================
INSERT IGNORE INTO roles (id, name, description, permissions) VALUES
(1, 'admin', '系统管理员', '["users:manage", "records:manage", "tasks:manage", "stats:view", "system:manage"]'),
(2, 'editor', '编辑', '["records:manage", "tasks:manage", "stats:view"]'),
(3, 'viewer', '查看者', '["records:view", "stats:view"]');

-- ============================================================
-- 插入初始用户 (密码: admin123)
-- ============================================================
INSERT IGNORE INTO users (id, username, hashed_password, email, full_name, role_id) VALUES
(1, 'admin', '$2b$12$EixZaYbB.rK4fl8x2q7Meu6Q6D2V5fF5Q5Q5Q5Q5Q5Q5Q5Q5Q5Q', 'admin@example.com', '系统管理员', 1);
