import sqlite3

conn = sqlite3.connect('data/admission_system.db')
cursor = conn.cursor()

# 检查 source_data 字段是否存在
cursor.execute("PRAGMA table_info(admission_records)")
columns = [col[1] for col in cursor.fetchall()]

if 'source_data' in columns:
    # SQLite 不支持直接删除列，需要创建新表并迁移数据
    cursor.execute("""
        CREATE TABLE admission_records_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name_cn TEXT,
            student_name_en TEXT,
            student_grade TEXT,
            country TEXT,
            country_en TEXT,
            university_cn TEXT,
            university_en TEXT,
            university_type TEXT,
            university_ranking INTEGER,
            major_cn TEXT,
            major_en TEXT,
            major_category TEXT,
            admission_type TEXT,
            admission_status TEXT,
            conditional_offer INTEGER DEFAULT 0,
            admission_date TEXT,
            admission_year INTEGER,
            language_requirement_type TEXT,
            language_score_required REAL,
            sat_required INTEGER DEFAULT 0,
            scholarship_amount REAL DEFAULT 0,
            scholarship_currency TEXT,
            scholarship_type TEXT,
            source_school TEXT,
            article_url TEXT,
            article_title TEXT,
            status INTEGER DEFAULT 1,
            review_status TEXT DEFAULT 'pending',
            promoted_from_staging_id INTEGER,
            promoted_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            recognition_model TEXT DEFAULT ''
        )
    """)
    
    # 迁移数据（排除 source_data）
    cursor.execute("""
        INSERT INTO admission_records_new SELECT 
            id, student_name_cn, student_name_en, student_grade, country, country_en,
            university_cn, university_en, university_type, university_ranking,
            major_cn, major_en, major_category, admission_type, admission_status,
            conditional_offer, admission_date, admission_year, language_requirement_type,
            language_score_required, sat_required, scholarship_amount, scholarship_currency,
            scholarship_type, source_school, article_url, article_title, status,
            review_status, promoted_from_staging_id, promoted_at, created_at, updated_at,
            notes, recognition_model
        FROM admission_records
    """)
    
    # 删除旧表并重命名新表
    cursor.execute("DROP TABLE admission_records")
    cursor.execute("ALTER TABLE admission_records_new RENAME TO admission_records")
    
    conn.commit()
    print("已删除 source_data 字段")
else:
    print("source_data 字段不存在")

# 验证结果
cursor.execute("PRAGMA table_info(admission_records)")
print("\n当前表结构:")
for col in cursor.fetchall():
    print(col)

conn.close()