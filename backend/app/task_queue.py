"""
任务队列管理器 — 优化大并发任务执行
核心优化：
1. 线程安全连接池，避免频繁创建/关闭连接
2. 受控并发，支持背压防止数据库过载
3. 批量数据库操作，减少 I/O 次数
4. 进度心跳，减少状态查询频率
"""
import os
import threading
import time
from datetime import datetime
from queue import Queue, Empty
from collections import deque
from threading import Semaphore, Event

# 导入统一数据库配置
from app.db_config import DB_TYPE, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE


class ConnectionPool:
    """数据库连接池 — 支持 SQLite 和 MySQL"""

    def __init__(self, pool_size=5):
        self._pool_size = pool_size
        self._local = threading.local()
        self._lock = threading.Lock()
        self._pool = deque()
        self._total_created = 0

    def _create_connection(self):
        if DB_TYPE == "mysql":
            import pymysql
            conn = pymysql.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            return conn
        else:
            # import sqlite3 - replaced by db_config
            DB_PATH = os.path.join(os.path.dirname(__file__), "../data/admission_system.db")
            conn = get_db_connection()
            # conn.row_factory - handled by get_db_connection()
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA cache_size = 20000")
            conn.execute("PRAGMA temp_store = MEMORY")
            conn.execute("PRAGMA mmap_size = 67108864")
            conn.execute("PRAGMA busy_timeout = 30000")
            conn.execute("PRAGMA wal_autocheckpoint = 1000")
            conn.execute("PRAGMA journal_size_limit = 67108864")
            conn.execute("PRAGMA foreign_keys = ON")
            return conn

    def get(self):
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            with self._lock:
                if self._pool:
                    self._local.conn = self._pool.popleft()
                else:
                    self._local.conn = self._create_connection()
                    self._total_created += 1
        return self._local.conn

    def return_all(self):
        if hasattr(self._local, 'conn') and self._local.conn is not None:
            with self._lock:
                if len(self._pool) < self._pool_size:
                    self._pool.append(self._local.conn)
                else:
                    self._local.conn.close()
            self._local.conn = None

    def close_all(self):
        with self._lock:
            while self._pool:
                conn = self._pool.popleft()
                try:
                    conn.close()
                except Exception:
                    pass


_connection_pool = ConnectionPool(pool_size=5)


def get_pooled_connection():
    return _connection_pool.get()


class TaskQueueManager:
    """受控并发任务队列 — 限制并发数 + 背压 + 批量提交"""

    def __init__(self, max_workers=3):
        self.max_workers = max_workers
        self._semaphore = Semaphore(max_workers)
        self._active_tasks = {}
        self._cancel_events = {}
        self._status_lock = threading.Lock()
        self._running = False
        self._total_completed = 0
        self._total_failed = 0
        self._start_time = None
        self._batch_changes = []
        self._batch_lock = threading.Lock()
        self._batch_flush_interval = 50

    def start(self, task_ids, process_func):
        if self._running:
            raise RuntimeError("队列已在运行中")
        self._running = True
        self._total_completed = 0
        self._total_failed = 0
        self._start_time = time.time()
        self._batch_changes = []

        task_queue = Queue()
        for tid in task_ids:
            task_queue.put(tid)

        total = len(task_ids)

        def worker():
            while self._running:
                try:
                    tid = task_queue.get(timeout=2)
                except Empty:
                    break

                self._semaphore.acquire()
                cancel_event = Event()
                self._cancel_events[tid] = cancel_event

                try:
                    result = process_func(tid, cancel_event)
                    with self._status_lock:
                        if result.get("status") == "success":
                            self._total_completed += 1
                        else:
                            self._total_failed += 1
                    self._batch_checkpoint()
                except Exception as e:
                    with self._status_lock:
                        self._total_failed += 1
                    print(f"[QUEUE] 任务 {tid} 异常: {e}")
                finally:
                    self._cancel_events.pop(tid, None)
                    self._semaphore.release()
                    task_queue.task_done()

        workers = []
        num_workers = min(self.max_workers * 3, total, 10)
        for _ in range(num_workers):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            workers.append(t)

        for t in workers:
            t.join(timeout=600)

        self._running = False
        self._flush_batch(force=True)
        return {"completed": self._total_completed, "failed": self._total_failed}

    def cancel_task(self, tid):
        if tid in self._cancel_events:
            self._cancel_events[tid].set()
            return True
        return False

    def get_progress(self):
        total = self._total_completed + self._total_failed
        elapsed = time.time() - self._start_time if self._start_time else 0
        rate = total / (elapsed / 60) if elapsed > 0 else 0
        return {
            "running": self._running,
            "completed": self._total_completed,
            "failed": self._total_failed,
            "total_processed": total,
            "rate_per_min": round(rate, 1),
            "elapsed_seconds": round(elapsed, 1),
        }

    def add_batch_update(self, sql, params):
        with self._batch_lock:
            self._batch_changes.append((sql, params))

    def _batch_checkpoint(self):
        with self._status_lock:
            self._status_lock.__dict__.setdefault('_counter', 0)
            self._status_lock.__dict__['_counter'] += 1
        if self._status_lock.__dict__['_counter'] % self._batch_flush_interval == 0:
            self._flush_batch()

    def _flush_batch(self, force=False):
        with self._batch_lock:
            if not self._batch_changes:
                return
            changes = self._batch_changes[:]
            self._batch_changes = []

        if not changes:
            return

        try:
            conn = get_pooled_connection()
            c = conn.cursor()
            for sql, params in changes:
                c.execute(sql, params)
            conn.commit()
        except Exception as e:
            print(f"[QUEUE] 批量写入失败: {e}")


_task_queue_manager = None


def get_task_queue(max_workers=3):
    global _task_queue_manager
    if _task_queue_manager is None:
        _task_queue_manager = TaskQueueManager(max_workers=max_workers)
    else:
        _task_queue_manager.max_workers = max_workers
    return _task_queue_manager
