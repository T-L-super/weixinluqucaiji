#!/usr/bin/env python3
"""定时采集调度器 - 每分钟检查是否在采集时间段内，如果是则执行待处理任务"""

import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from app.db_config import get_db_connection, exec_sql, DB_TYPE

LAST_RUN_FILE = os.path.join(os.path.dirname(__file__), 'data', '.last_scheduler_run')


def init_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    if DB_TYPE == "mysql":
        cursor.execute("""CREATE TABLE IF NOT EXISTS scheduler_settings (
            id INT PRIMARY KEY,
            enabled TINYINT DEFAULT 0,
            start_hour INT DEFAULT 1,
            end_hour INT DEFAULT 5,
            last_run_at DATETIME,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )""")
        cursor.execute("INSERT IGNORE INTO scheduler_settings (id, enabled, start_hour, end_hour) VALUES (1, 0, 1, 5)")
        cursor.execute("""CREATE TABLE IF NOT EXISTS concurrency_settings (
            id INT PRIMARY KEY,
            enabled TINYINT DEFAULT 0,
            max_concurrent INT DEFAULT 1,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )""")
        cursor.execute("INSERT IGNORE INTO concurrency_settings (id, enabled, max_concurrent) VALUES (1, 0, 1)")
    else:
        cursor.execute("""CREATE TABLE IF NOT EXISTS scheduler_settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            enabled INTEGER DEFAULT 0,
            start_hour INTEGER DEFAULT 1,
            end_hour INTEGER DEFAULT 5,
            last_run_at TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        cursor.execute("INSERT OR IGNORE INTO scheduler_settings (id, enabled, start_hour, end_hour) VALUES (1, 0, 1, 5)")
        cursor.execute("""CREATE TABLE IF NOT EXISTS concurrency_settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            enabled INTEGER DEFAULT 0,
            max_concurrent INTEGER DEFAULT 1,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        cursor.execute("INSERT OR IGNORE INTO concurrency_settings (id, enabled, max_concurrent) VALUES (1, 0, 1)")
    conn.commit()
    conn.close()


def execute_task(task_id):
    import urllib.request
    import json

    try:
        url = f"http://localhost:8001/api/collection-tasks/{task_id}/start"
        req = urllib.request.Request(url, method="POST")
        req.add_header('Content-Type', 'application/json')
        response = urllib.request.urlopen(req, timeout=300)
        result = json.loads(response.read().decode())
        return result.get('success', False), result.get('message', '')
    except Exception as e:
        return False, str(e)


def run_scheduler():
    init_tables()
    print(f"[{datetime.now()}] 定时采集调度器启动 (DB: {DB_TYPE})", flush=True)

    while True:
        try:
            now = datetime.now()
            current_hour = now.hour

            conn = get_db_connection()
            cursor = conn.cursor()
            conn_closed = False

            exec_sql(cursor, "SELECT enabled, start_hour, end_hour FROM scheduler_settings WHERE id = 1")
            row = cursor.fetchone()

            if not row:
                conn.close()
                time.sleep(60)
                continue

            enabled = bool(row[0] if not isinstance(row, dict) else row.get('enabled', 0))
            start_hour = row[1] if not isinstance(row, dict) else row.get('start_hour', 1)
            end_hour = row[2] if not isinstance(row, dict) else row.get('end_hour', 5)

            in_window = start_hour <= current_hour < end_hour

            last_run = None
            if os.path.exists(LAST_RUN_FILE):
                with open(LAST_RUN_FILE, 'r') as f:
                    last_run = f.read().strip()

            current_date_hour = now.strftime('%Y-%m-%d-%H')

            if enabled and in_window and last_run != current_date_hour:
                print(f"[{now}] 进入采集时间段 ({start_hour}:00-{end_hour}:00)，开始执行任务", flush=True)

                exec_sql(cursor, "SELECT enabled, max_concurrent FROM concurrency_settings WHERE id = 1")
                conc_row = cursor.fetchone()
                conc_enabled = bool(conc_row[0]) if conc_row else False
                max_conc = conc_row[1] if conc_row else 1

                CUTOFF_MINUTES = 30
                if DB_TYPE == "mysql":
                    cursor.execute(
                        "UPDATE collection_tasks SET task_status = 0, started_at = NULL, error_message = %s WHERE task_status = 2 AND started_at < DATE_SUB(NOW(), INTERVAL %s MINUTE)",
                        (f'调度器恢复：任务卡住超过{CUTOFF_MINUTES}分钟', CUTOFF_MINUTES)
                    )
                else:
                    exec_sql(cursor,
                        "UPDATE collection_tasks SET task_status = 0, started_at = NULL, error_message = '调度器恢复：任务卡住超过{}分钟' WHERE task_status = 2 AND started_at < datetime('now', '-{} minutes')".format(CUTOFF_MINUTES, CUTOFF_MINUTES)
                    )
                recovered = cursor.rowcount
                if recovered > 0:
                    conn.commit()
                    print(f"[{now}] 恢复了 {recovered} 个卡住超过{CUTOFF_MINUTES}分钟的任务", flush=True)

                exec_sql(cursor, "SELECT id FROM collection_tasks WHERE task_status = 0 ORDER BY priority ASC, created_at ASC")
                task_ids = [r[0] if not isinstance(r, dict) else r['id'] for r in cursor.fetchall()]

                conn.close()
                conn_closed = True

                if not task_ids:
                    print(f"[{now}] 没有待执行的任务", flush=True)
                else:
                    if conc_enabled and max_conc > 1:
                        to_run = task_ids[:max_conc]
                    else:
                        to_run = task_ids[:1]

                    for tid in to_run:
                        success, msg = execute_task(tid)
                        status = "成功" if success else f"失败: {msg}"
                        print(f"[{now}] 任务 {tid} 执行{status}", flush=True)

                    conn2 = get_db_connection()
                    cursor2 = conn2.cursor()
                    exec_sql(cursor2, "UPDATE scheduler_settings SET last_run_at = CURRENT_TIMESTAMP WHERE id = 1")
                    conn2.commit()
                    conn2.close()

                    with open(LAST_RUN_FILE, 'w') as f:
                        f.write(current_date_hour)

                    print(f"[{now}] 本轮采集完成，执行了 {len(to_run)} 个任务", flush=True)
            else:
                if not enabled:
                    pass
                elif not in_window:
                    pass
                else:
                    pass

            if not conn_closed:
                conn.close()

        except Exception as e:
            print(f"[{datetime.now()}] 调度器错误: {e}", flush=True)

        time.sleep(60)


if __name__ == '__main__':
    run_scheduler()
