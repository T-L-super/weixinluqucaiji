import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_path = os.path.join(os.path.dirname(__file__), 'data', 'admission_system.db')

conn = sqlite3.connect(db_path)
c = conn.cursor()

print("清理姓名为'未知'或空的数据...\n")

# 1. 清理暂存表中姓名为'未知'或空的数据
tables_to_clean = ['admission_records_staging', 'admission_records']

for table in tables_to_clean:
    try:
        # 先统计数量
        c.execute(f"SELECT COUNT(*) FROM {table} WHERE student_name_cn IS NULL OR student_name_cn = '' OR student_name_cn = '未知' OR TRIM(student_name_cn) = ''")
        invalid_count = c.fetchone()[0]
        
        # 统计总数
        c.execute(f"SELECT COUNT(*) FROM {table}")
        total_count = c.fetchone()[0]
        
        if invalid_count > 0:
            # 删除无效数据
            c.execute(f"DELETE FROM {table} WHERE student_name_cn IS NULL OR student_name_cn = '' OR student_name_cn = '未知' OR TRIM(student_name_cn) = ''")
            conn.commit()
            
            # 验证
            c.execute(f"SELECT COUNT(*) FROM {table}")
            remaining = c.fetchone()[0]
            print(f"[OK] {table}: 删除 {invalid_count} 条无效数据，剩余 {remaining} 条（原 {total_count} 条）")
        else:
            print(f"[OK] {table}: 没有无效数据（共 {total_count} 条）")
    except Exception as e:
        print(f"[ERROR] {table}: {e}")

# 2. 最终验证
print("\n最终验证 - 检查是否还有姓名为'未知'的数据：")
for table in tables_to_clean:
    try:
        c.execute(f"SELECT COUNT(*) FROM {table} WHERE student_name_cn = '未知' OR student_name_cn IS NULL OR student_name_cn = ''")
        count = c.fetchone()[0]
        status = "CLEAN" if count == 0 else f"HAS {count} INVALID"
        print(f"  [{status}] {table}")
    except:
        pass

conn.close()
print("\n清理完成！")
