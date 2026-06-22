import sqlite3
import os

DB_PATH = r'd:\大学录取信息整理系统\backend\data\admission_system.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT enabled, start_hour, end_hour, last_run_at, updated_at FROM scheduler_settings WHERE id = 1")
row = cursor.fetchone()

if row:
    enabled = bool(row[0])
    start_hour = row[1]
    end_hour = row[2]
    last_run = row[3]
    updated_at = row[4]
    
    print("=" * 50)
    print("定时采集当前状态")
    print("=" * 50)
    print(f"启用状态: {'✅ 已启用' if enabled else '❌ 未启用'}")
    print(f"采集时间段: {start_hour}:00 - {end_hour}:00")
    print(f"上次运行时间: {last_run if last_run else '从未运行'}")
    print(f"配置更新时间: {updated_at}")
    print("=" * 50)
    
    if enabled:
        print("\n💡 调度器已配置启用")
        print("   调度器会在采集时间段内自动执行待处理任务")
        print("   如果当前不在采集时间段，调度器会等待到指定时间")
    else:
        print("\n💡 请在管理界面启用定时采集")
    
else:
    print("❌ 未找到定时采集配置")

conn.close()