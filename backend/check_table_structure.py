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

# 查看 admission_records_staging 表结构
cursor.execute("DESCRIBE admission_records_staging")
columns = cursor.fetchall()

print("admission_records_staging 表结构:")
for col in columns:
    print(f"  {col[0]} - {col[1]}")

print("\n")

# 查看 admission_records 表结构
cursor.execute("DESCRIBE admission_records")
columns = cursor.fetchall()

print("admission_records 表结构:")
for col in columns:
    print(f"  {col[0]} - {col[1]}")

conn.close()
