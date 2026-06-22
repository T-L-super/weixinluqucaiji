import sqlite3
import os

DB_PATH = r'd:\大学录取信息整理系统\backend\data\admission_system.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT enabled, start_hour, end_hour, last_run_at FROM scheduler_settings WHERE id = 1")
row = cursor.fetchone()

if row:
    enabled = bool(row[0])
    start_hour = row[1]
    end_hour = row[2]
    last_run = row[3]
    
    print(f"定时采集配置:")
    print(f"  已启用: {'✅ 是' if enabled else '❌ 否'}")
    print(f"  采集时间段: {start_hour}:00 - {end_hour}:00")
    print(f"  上次运行: {last_run if last_run else '从未运行'}")
    
    if enabled:
        print("\n💡 提示: 配置已启用，但调度器进程可能需要几分钟才能启动")
    else:
        print("\n💡 提示: 请在前端勾选'启用定时采集'并保存")
else:
    print("❌ 未找到定时采集配置")

conn.close()