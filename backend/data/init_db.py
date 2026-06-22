import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'admission_system.db')

def init_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA foreign_keys = ON')
    cursor = conn.cursor()
    
    schema = '''
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
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

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

CREATE TABLE IF NOT EXISTS admission_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name_cn VARCHAR(100) NOT NULL,
    student_name_en VARCHAR(100),
    student_grade VARCHAR(20),
    country VARCHAR(50) NOT NULL,
    country_en VARCHAR(50),
    university_cn VARCHAR(200) NOT NULL,
    university_en VARCHAR(200),
    university_type VARCHAR(50),
    university_ranking INTEGER,
    major_cn VARCHAR(200),
    major_en VARCHAR(200),
    major_category VARCHAR(50),
    admission_type VARCHAR(50),
    admission_status VARCHAR(50),
    conditional_offer INTEGER DEFAULT 0,
    admission_date DATE,
    admission_year INTEGER NOT NULL,
    language_requirement_type VARCHAR(50),
    language_score_required VARCHAR(50),
    language_score_actual VARCHAR(50),
    language_waived INTEGER DEFAULT 0,
    sat_required VARCHAR(50),
    sat_actual VARCHAR(50),
    test_optional INTEGER DEFAULT 0,
    scholarship_amount DECIMAL(10,2),
    scholarship_currency VARCHAR(10),
    scholarship_type VARCHAR(50),
    source_school VARCHAR(200) NOT NULL,
    article_url VARCHAR(500) NOT NULL,
    article_title VARCHAR(300),
    publish_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status INTEGER DEFAULT 1,
    data_quality INTEGER DEFAULT 3,
    notes TEXT,
    gpa VARCHAR(50),
    toefl VARCHAR(50),
    ielts VARCHAR(50),
    sat VARCHAR(50),
    act VARCHAR(50),
    gre VARCHAR(50),
    gmat VARCHAR(50)
);

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
    recognition_model VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS admission_records_staging (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name_cn VARCHAR(100),
    student_name_en VARCHAR(100),
    country VARCHAR(50),
    country_en VARCHAR(50),
    university_cn VARCHAR(200),
    university_en VARCHAR(200),
    major_cn VARCHAR(200),
    major_en VARCHAR(200),
    admission_type VARCHAR(50),
    admission_status VARCHAR(50),
    admission_year INTEGER,
    scholarship_amount DECIMAL(10,2),
    scholarship_currency VARCHAR(10),
    source_school VARCHAR(200),
    article_url VARCHAR(500),
    article_title VARCHAR(300),
    data_source VARCHAR(100),
    row_index INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed INTEGER DEFAULT 0,
    processed_at DATETIME,
    gpa VARCHAR(50),
    toefl VARCHAR(50),
    ielts VARCHAR(50),
    sat VARCHAR(50),
    act VARCHAR(50),
    gre VARCHAR(50),
    gmat VARCHAR(50)
);

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
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

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

CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(200),
    permissions TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    full_name VARCHAR(100),
    role_id INTEGER,
    is_active INTEGER DEFAULT 1,
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

CREATE TABLE IF NOT EXISTS operation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username VARCHAR(50),
    operation_type VARCHAR(50),
    operation_desc TEXT,
    ip_address VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS batch_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_type VARCHAR(50),
    operation_data TEXT,
    created_by INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS concurrency_settings (
    id INTEGER PRIMARY KEY,
    enabled INTEGER DEFAULT 0,
    max_concurrent INTEGER DEFAULT 2,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scheduler_settings (
    id INTEGER PRIMARY KEY,
    enabled INTEGER DEFAULT 0,
    start_hour INTEGER DEFAULT 1,
    end_hour INTEGER DEFAULT 5,
    last_run_at DATETIME,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_screen_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    screen_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_candidates INTEGER DEFAULT 0,
    passed INTEGER DEFAULT 0,
    rejected INTEGER DEFAULT 0,
    batch_size INTEGER DEFAULT 0,
    duration_ms INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS ai_rejected_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER,
    reason TEXT,
    screen_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (record_id) REFERENCES admission_records(id)
);

CREATE TABLE IF NOT EXISTS review_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER,
    reviewer_id INTEGER,
    review_status VARCHAR(50),
    review_notes TEXT,
    review_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (record_id) REFERENCES admission_records(id),
    FOREIGN KEY (reviewer_id) REFERENCES users(id)
);

INSERT INTO roles (name, description, permissions) VALUES 
('super_admin', '系统管理员', '["*"]'),
('data_admin', '数据管理员', '["read", "write", "delete", "manage_users"]'),
('collection_operator', '采集操作员', '["read", "write"]'),
('normal_user', '普通用户', '["read"]');

INSERT INTO users (username, email, password_hash, full_name, role_id, is_active) VALUES 
('admin', 'admin@example.com', '$2b$12$EixZaYbB.rK4fl8x2q7Meu6Q6D2V5fF5Q5Q5Q5Q5Q5Q5Q5Q5Q5Q', '系统管理员', 1, 1);

INSERT INTO concurrency_settings (id, enabled, max_concurrent) VALUES (1, 0, 2);

INSERT INTO scheduler_settings (id, enabled, start_hour, end_hour) VALUES (1, 0, 1, 5);

CREATE INDEX idx_admission_student ON admission_records(student_name_cn);
CREATE INDEX idx_admission_country ON admission_records(country);
CREATE INDEX idx_admission_university ON admission_records(university_cn);
CREATE INDEX idx_admission_year ON admission_records(admission_year);
CREATE INDEX idx_tasks_status_priority ON collection_tasks(task_status, priority);
    '''
    
    cursor.executescript(schema)
    conn.commit()
    conn.close()
    print(f"数据库初始化完成: {DB_PATH}")

if __name__ == '__main__':
    init_database()
