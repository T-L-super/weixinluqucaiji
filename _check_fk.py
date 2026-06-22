import sqlite3
db_path = r"d:\大学录取信息整理系统\backend\data\admission_system.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check ALL tables for FK references to admission_records
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'admission_records' ORDER BY name")
tables = [r[0] for r in c.fetchall()]

print("Checking ALL tables for FK references to admission_records(id):")
for table in tables:
    try:
        c.execute(f"PRAGMA foreign_key_list({table})")
        fks = c.fetchall()
        for fk in fks:
            if fk[2] == 'admission_records':
                print(f"  {table}.{fk[3]} -> admission_records.{fk[4]} (update={fk[5]}, delete={fk[6]})")
    except Exception as e:
        print(f"  {table}: error - {e}")

# Also check FK references by looking at table creation SQL
print("\n--- Checking table schemas ---")
c.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'admission_records' ORDER BY name")
tables = c.fetchall()
for name, sql in tables:
    if sql and 'admission_records' in sql.lower():
        print(f"\n  {name} references admission_records:")
        print(f"    {sql[:200]}")

conn.close()