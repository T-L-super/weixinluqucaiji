import pymysql

conn = pymysql.connect(host='10.9.8.120', port=3306, user='python', password='YLcXkLEcYAihBitr', database='python', charset='utf8mb4')
c = conn.cursor()
c.execute("SELECT id, student_name_cn, university_cn, review_status FROM admission_records ORDER BY id DESC LIMIT 3")
for r in c.fetchall():
    print(r)
c.execute("SELECT COUNT(*) as cnt FROM admission_records_staging WHERE review_status = 'pending'")
print("Pending staging:", c.fetchone()[0])
conn.close()
