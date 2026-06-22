import pymysql

config = {
    'host': '10.9.8.120',
    'port': 3306,
    'user': 'python',
    'password': 'YLcXkLEcYAihBitr',
    'database': 'python',
    'charset': 'utf8mb4'
}

conn = pymysql.connect(**config)
cursor = conn.cursor()

# 为 admission_records_staging 添加缺失的字段
alter_statements = [
    "ALTER TABLE admission_records_staging ADD COLUMN IF NOT EXISTS review_comment TEXT",
    "ALTER TABLE admission_records_staging ADD COLUMN IF NOT EXISTS reviewed_by VARCHAR(100)",
    "ALTER TABLE admission_records_staging ADD COLUMN IF NOT EXISTS reviewed_at DATETIME",
    "ALTER TABLE admission_records_staging ADD COLUMN IF NOT EXISTS promoted_at DATETIME",
    "ALTER TABLE admission_records_staging ADD COLUMN IF NOT EXISTS sat_actual VARCHAR(50)",
    "ALTER TABLE admission_records_staging ADD COLUMN IF NOT EXISTS language_score_actual VARCHAR(50)",
    "ALTER TABLE admission_records_staging ADD COLUMN IF NOT EXISTS updated_at DATETIME",
]

for stmt in alter_statements:
    try:
        # MySQL 不支持 IF NOT EXISTS，需要用 try-except
        stmt_clean = stmt.replace("IF NOT EXISTS", "")
        cursor.execute(stmt_clean)
        print(f"OK: {stmt_clean}")
    except Exception as e:
        if "Duplicate column name" in str(e):
            print(f"SKIP (字段已存在): {stmt}")
        else:
            print(f"ERROR: {stmt} - {e}")

conn.commit()
print("\n字段添加完成!")

# 验证表结构
cursor.execute("DESCRIBE admission_records_staging")
columns = cursor.fetchall()

print("\nadmission_records_staging 表结构:")
for col in columns:
    print(f"  {col[0]} - {col[1]}")

conn.close()
