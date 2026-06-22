#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查定时采集配置状态"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'backend', 'data', 'admission_system.db')

def check_scheduler_status():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取定时采集设置
        cursor.execute("SELECT enabled, start_hour, end_hour, last_run_at FROM scheduler_settings WHERE id = 1")
        row = cursor.fetchone()
        
        if row:
            enabled = bool(row[0])
            start_hour = row[1]
            end_hour = row[2]
            last_run = row[3]
            
            print("定时采集配置状态:")
            print(f"  ✅ 已启用: {'是' if enabled else '否'}")
            print(f"  ⏰ 采集时间段: {start_hour}:00 - {end_hour}:00")
            print(f"  📅 上次运行时间: {last_run if last_run else '从未运行'}")
            
            if not enabled:
                print("\n  💡 提示: 定时采集当前未启用，请通过管理界面或API开启")
        else:
            print("❌ 未找到定时采集配置")
        
        conn.close()
    except Exception as e:
        print(f"❌ 检查失败: {e}")

if __name__ == '__main__':
    check_scheduler_status()