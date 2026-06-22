# -*- coding: utf-8 -*-
"""
系统监控告警模块
功能：
1. 健康检查 API
2. 性能监控（CPU、内存、磁盘）
3. 日志收集和查看
4. 告警配置（邮件/钉钉）
5. 监控指标：API 响应时间、数据库连接数、磁盘使用率、采集任务状态
"""

import os
import psutil
from app.db_config import get_db_connection, exec_sql
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class AlertConfig:
    """告警配置"""
    enabled: bool = True
    email_enabled: bool = False
    email_recipients: List[str] = None
    dingtalk_enabled: bool = False
    dingtalk_webhook: str = ""
    cpu_threshold: float = 80.0  # CPU 使用率告警阈值 %
    memory_threshold: float = 85.0  # 内存使用率告警阈值 %
    disk_threshold: float = 90.0  # 磁盘使用率告警阈值 %
    api_latency_threshold: float = 2.0  # API 响应时间告警阈值 (秒)
    check_interval: int = 60  # 检查间隔 (秒)
    
    def __post_init__(self):
        if self.email_recipients is None:
            self.email_recipients = []


@dataclass
class SystemMetrics:
    """系统性能指标"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    network_sent_mb: float
    network_recv_mb: float


@dataclass
class HealthStatus:
    """健康状态"""
    status: str  # healthy, warning, critical
    timestamp: str
    api_status: str
    database_status: str
    disk_status: str
    task_queue_status: str
    active_alerts: List[Dict[str, Any]]
    metrics: Dict[str, Any]


class MonitorService:
    """监控服务类"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.path.join(os.path.dirname(__file__), "../data/admission_system.db")
        self.start_time = datetime.now()
        self.alert_config = AlertConfig()
        self.metrics_history: List[SystemMetrics] = []
        self.active_alerts: List[Dict[str, Any]] = []
        self.api_response_times: List[float] = []
        
        # 确保监控数据目录存在
        self.data_dir = os.path.join(os.path.dirname(__file__), "../data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 初始化监控数据库表
        self._init_monitor_db()
        
    def _init_monitor_db(self):
        """初始化监控数据库表"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 创建监控指标表（兼容 MySQL 和 SQLite）
            from app.db_config import DB_TYPE
            if DB_TYPE == "mysql":
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS system_metrics (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        cpu_percent FLOAT,
                        memory_percent FLOAT,
                        disk_percent FLOAT,
                        api_latency_avg FLOAT,
                        active_tasks INT,
                        completed_tasks INT,
                        failed_tasks INT
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                ''')
            else:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS system_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        cpu_percent REAL,
                        memory_percent REAL,
                        disk_percent REAL,
                        api_latency_avg REAL,
                        active_tasks INTEGER,
                        completed_tasks INTEGER,
                        failed_tasks INTEGER
                    )
                ''')
            
            # 创建告警记录表（兼容 MySQL 和 SQLite）
            if DB_TYPE == "mysql":
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS alert_records (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        alert_type VARCHAR(100),
                        severity VARCHAR(20),
                        message TEXT,
                        metric_value FLOAT,
                        threshold FLOAT,
                        is_resolved TINYINT DEFAULT 0,
                        resolved_at TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                ''')
            else:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS alert_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        alert_type TEXT,
                        severity TEXT,
                        message TEXT,
                        metric_value REAL,
                        threshold REAL,
                        is_resolved INTEGER DEFAULT 0,
                        resolved_at TIMESTAMP
                    )
                ''')
            
            # 创建 API 响应时间表（兼容 MySQL 和 SQLite）
            if DB_TYPE == "mysql":
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS api_latency_log (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        endpoint VARCHAR(255),
                        method VARCHAR(10),
                        latency_ms FLOAT,
                        status_code INT
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                ''')
            else:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS api_latency_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        endpoint TEXT,
                        method TEXT,
                        latency_ms REAL,
                        status_code INTEGER
                    )
                ''')
            
            # 创建索引（兼容 MySQL 和 SQLite）
            if DB_TYPE == "mysql":
                # MySQL 5.x 不支持 IF NOT EXISTS，直接尝试创建，忽略错误
                try:
                    cursor.execute('CREATE INDEX idx_metrics_timestamp ON system_metrics(timestamp)')
                except:
                    pass
                try:
                    cursor.execute('CREATE INDEX idx_alerts_timestamp ON alert_records(timestamp)')
                except:
                    pass
                try:
                    cursor.execute('CREATE INDEX idx_latency_timestamp ON api_latency_log(timestamp)')
                except:
                    pass
            else:
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON system_metrics(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alert_records(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_latency_timestamp ON api_latency_log(timestamp)')
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"初始化监控数据库失败：{e}")
    
    def get_system_metrics(self) -> SystemMetrics:
        """获取当前系统性能指标"""
        try:
            # CPU 使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # 内存使用
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = memory.used / (1024 ** 3)
            memory_total_gb = memory.total / (1024 ** 3)
            
            # 磁盘使用
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used_gb = disk.used / (1024 ** 3)
            disk_total_gb = disk.total / (1024 ** 3)
            
            # 网络流量
            network = psutil.net_io_counters()
            network_sent_mb = network.bytes_sent / (1024 ** 2)
            network_recv_mb = network.bytes_recv / (1024 ** 2)
            
            return SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_gb=round(memory_used_gb, 2),
                memory_total_gb=round(memory_total_gb, 2),
                disk_percent=disk_percent,
                disk_used_gb=round(disk_used_gb, 2),
                disk_total_gb=round(disk_total_gb, 2),
                network_sent_mb=round(network_sent_mb, 2),
                network_recv_mb=round(network_recv_mb, 2)
            )
        except Exception as e:
            logger.error(f"获取系统指标失败：{e}")
            return None
    
    def check_database_health(self) -> Dict[str, Any]:
        """检查数据库健康状态"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 检查连接
            cursor.execute("SELECT 1")
            
            # 检查表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            # 检查记录数
            cursor.execute("SELECT COUNT(*) FROM admission_records")
            record_count = cursor.fetchone()[0]
            
            # 检查采集任务状态
            cursor.execute("SELECT status, COUNT(*) FROM collection_tasks GROUP BY status")
            task_stats = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                "status": "healthy",
                "tables_count": len(tables),
                "record_count": record_count,
                "task_stats": task_stats
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def get_task_queue_status(self) -> Dict[str, Any]:
        """获取任务队列状态"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 各状态任务数
            cursor.execute("SELECT status, COUNT(*) FROM collection_tasks GROUP BY status")
            status_counts = dict(cursor.fetchall())
            
            # 待处理任务数
            pending_count = status_counts.get('pending', 0)
            
            # 处理中任务数
            processing_count = status_counts.get('processing', 0)
            
            # 今日完成任务数
            cursor.execute("""
                SELECT COUNT(*) FROM collection_tasks 
                WHERE status = 'completed' 
                AND DATE(completed_at) = DATE('now')
            """)
            today_completed = cursor.fetchone()[0]
            
            # 今日失败任务数
            cursor.execute("""
                SELECT COUNT(*) FROM collection_tasks 
                WHERE status = 'failed' 
                AND DATE(completed_at) = DATE('now')
            """)
            today_failed = cursor.fetchone()[0]
            
            # 最近失败的任务
            cursor.execute("""
                SELECT id, url, error_message, completed_at 
                FROM collection_tasks 
                WHERE status = 'failed' 
                ORDER BY completed_at DESC 
                LIMIT 5
            """)
            recent_failures = [
                {"id": row[0], "url": row[1], "error": row[2], "time": row[3]}
                for row in cursor.fetchall()
            ]
            
            conn.close()
            
            return {
                "status": "healthy" if pending_count < 100 else "warning",
                "pending": pending_count,
                "processing": processing_count,
                "completed_today": today_completed,
                "failed_today": today_failed,
                "recent_failures": recent_failures,
                "total_stats": status_counts
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def get_api_latency_stats(self) -> Dict[str, Any]:
        """获取 API 响应时间统计"""
        try:
            if not self.api_response_times:
                return {
                    "avg_ms": 0,
                    "p95_ms": 0,
                    "p99_ms": 0,
                    "count": 0
                }
            
            sorted_times = sorted(self.api_response_times)
            count = len(sorted_times)
            
            avg_ms = sum(sorted_times) / count * 1000
            p95_idx = int(count * 0.95)
            p99_idx = int(count * 0.99)
            
            return {
                "avg_ms": round(avg_ms, 2),
                "p95_ms": round(sorted_times[min(p95_idx, count-1)] * 1000, 2),
                "p99_ms": round(sorted_times[min(p99_idx, count-1)] * 1000, 2),
                "count": count
            }
        except Exception as e:
            logger.error(f"计算 API 延迟统计失败：{e}")
            return {"avg_ms": 0, "p95_ms": 0, "p99_ms": 0, "count": 0}
    
    def record_api_latency(self, endpoint: str, method: str, latency_sec: float, status_code: int):
        """记录 API 响应时间"""
        try:
            self.api_response_times.append(latency_sec)
            
            # 只保留最近 1000 次记录
            if len(self.api_response_times) > 1000:
                self.api_response_times = self.api_response_times[-1000:]
            
            # 记录到数据库
            conn = get_db_connection()
            cursor = conn.cursor()
            exec_sql(cursor,
                "INSERT INTO api_latency_log (endpoint, method, latency_ms, status_code) VALUES (?, ?, ?, ?)",
                [endpoint, method, latency_sec * 1000, status_code]
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"记录 API 延迟失败：{e}")
    
    def check_alerts(self, metrics: SystemMetrics) -> List[Dict[str, Any]]:
        """检查是否需要触发告警"""
        alerts = []
        
        if not self.alert_config.enabled:
            return alerts
        
        # CPU 告警
        if metrics.cpu_percent > self.alert_config.cpu_threshold:
            alert = {
                "type": "cpu_high",
                "severity": "warning" if metrics.cpu_percent < 95 else "critical",
                "message": f"CPU 使用率过高：{metrics.cpu_percent:.1f}%",
                "metric_value": metrics.cpu_percent,
                "threshold": self.alert_config.cpu_threshold,
                "timestamp": datetime.now().isoformat()
            }
            alerts.append(alert)
            self._save_alert(alert)
        
        # 内存告警
        if metrics.memory_percent > self.alert_config.memory_threshold:
            alert = {
                "type": "memory_high",
                "severity": "warning" if metrics.memory_percent < 95 else "critical",
                "message": f"内存使用率过高：{metrics.memory_percent:.1f}%",
                "metric_value": metrics.memory_percent,
                "threshold": self.alert_config.memory_threshold,
                "timestamp": datetime.now().isoformat()
            }
            alerts.append(alert)
            self._save_alert(alert)
        
        # 磁盘告警
        if metrics.disk_percent > self.alert_config.disk_threshold:
            alert = {
                "type": "disk_high",
                "severity": "warning" if metrics.disk_percent < 95 else "critical",
                "message": f"磁盘使用率过高：{metrics.disk_percent:.1f}%",
                "metric_value": metrics.disk_percent,
                "threshold": self.alert_config.disk_threshold,
                "timestamp": datetime.now().isoformat()
            }
            alerts.append(alert)
            self._save_alert(alert)
        
        # API 延迟告警
        latency_stats = self.get_api_latency_stats()
        if latency_stats["avg_ms"] > self.alert_config.api_latency_threshold * 1000:
            alert = {
                "type": "api_latency_high",
                "severity": "warning",
                "message": f"API 平均响应时间过长：{latency_stats['avg_ms']:.0f}ms",
                "metric_value": latency_stats["avg_ms"] / 1000,
                "threshold": self.alert_config.api_latency_threshold,
                "timestamp": datetime.now().isoformat()
            }
            alerts.append(alert)
            self._save_alert(alert)
        
        return alerts
    
    def _save_alert(self, alert: Dict[str, Any]):
        """保存告警记录到数据库"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO alert_records (alert_type, severity, message, metric_value, threshold) VALUES (?, ?, ?, ?, ?)",
                [alert["type"], alert["severity"], alert["message"], alert["metric_value"], alert["threshold"]]
            )
            conn.commit()
            conn.close()
            
            # 添加到活动告警列表
            self.active_alerts.append(alert)
            
            # 发送告警通知
            self._send_alert_notification(alert)
        except Exception as e:
            logger.error(f"保存告警记录失败：{e}")
    
    def _send_alert_notification(self, alert: Dict[str, Any]):
        """发送告警通知（邮件/钉钉）"""
        # 邮件通知
        if self.alert_config.email_enabled and self.alert_config.email_recipients:
            self._send_email_alert(alert)
        
        # 钉钉通知
        if self.alert_config.dingtalk_enabled and self.alert_config.dingtalk_webhook:
            self._send_dingtalk_alert(alert)
    
    def _send_email_alert(self, alert: Dict[str, Any]):
        """发送邮件告警"""
        # TODO: 实现邮件发送逻辑
        logger.info(f"邮件告警：{alert['message']}")
    
    def _send_dingtalk_alert(self, alert: Dict[str, Any]):
        """发送钉钉告警"""
        try:
            import requests
            
            message = {
                "msgtype": "text",
                "text": {
                    "content": f"⚠️ 系统告警\n类型：{alert['type']}\n级别：{alert['severity']}\n详情：{alert['message']}\n时间：{alert['timestamp']}"
                }
            }
            
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                self.alert_config.dingtalk_webhook,
                json=message,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("钉钉告警发送成功")
            else:
                logger.error(f"钉钉告警发送失败：{response.text}")
        except Exception as e:
            logger.error(f"发送钉钉告警失败：{e}")
    
    def get_health_status(self) -> HealthStatus:
        """获取系统健康状态"""
        metrics = self.get_system_metrics()
        db_health = self.check_database_health()
        task_status = self.get_task_queue_status()
        latency_stats = self.get_api_latency_stats()
        
        # 检查告警
        alerts = self.check_alerts(metrics) if metrics else []
        
        # 综合健康状态
        status = "healthy"
        if alerts:
            if any(a["severity"] == "critical" for a in alerts):
                status = "critical"
            else:
                status = "warning"
        
        return HealthStatus(
            status=status,
            timestamp=datetime.now().isoformat(),
            api_status="healthy" if latency_stats["avg_ms"] < self.alert_config.api_latency_threshold * 1000 else "warning",
            database_status=db_health["status"],
            disk_status="warning" if metrics and metrics.disk_percent > 80 else "healthy",
            task_queue_status=task_status["status"],
            active_alerts=alerts,
            metrics={
                "cpu_percent": metrics.cpu_percent if metrics else 0,
                "memory_percent": metrics.memory_percent if metrics else 0,
                "disk_percent": metrics.disk_percent if metrics else 0,
                "api_latency_avg_ms": latency_stats["avg_ms"],
                "active_tasks": task_status.get("pending", 0),
                "completed_today": task_status.get("completed_today", 0)
            }
        )
    
    def update_alert_config(self, config: Dict[str, Any]):
        """更新告警配置"""
        if "enabled" in config:
            self.alert_config.enabled = config["enabled"]
        if "email_enabled" in config:
            self.alert_config.email_enabled = config["email_enabled"]
        if "email_recipients" in config:
            self.alert_config.email_recipients = config["email_recipients"]
        if "dingtalk_enabled" in config:
            self.alert_config.dingtalk_enabled = config["dingtalk_enabled"]
        if "dingtalk_webhook" in config:
            self.alert_config.dingtalk_webhook = config["dingtalk_webhook"]
        if "cpu_threshold" in config:
            self.alert_config.cpu_threshold = config["cpu_threshold"]
        if "memory_threshold" in config:
            self.alert_config.memory_threshold = config["memory_threshold"]
        if "disk_threshold" in config:
            self.alert_config.disk_threshold = config["disk_threshold"]
        if "api_latency_threshold" in config:
            self.alert_config.api_latency_threshold = config["api_latency_threshold"]
        if "check_interval" in config:
            self.alert_config.check_interval = config["check_interval"]
    
    def get_alert_config(self) -> Dict[str, Any]:
        """获取告警配置"""
        return asdict(self.alert_config)
    
    def get_recent_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取最近的告警记录"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, timestamp, alert_type, severity, message, metric_value, threshold, is_resolved, resolved_at
                FROM alert_records
                ORDER BY timestamp DESC
                LIMIT ?
            """, [limit])
            
            alerts = []
            for row in cursor.fetchall():
                alerts.append({
                    "id": row[0],
                    "timestamp": row[1],
                    "type": row[2],
                    "severity": row[3],
                    "message": row[4],
                    "metric_value": row[5],
                    "threshold": row[6],
                    "is_resolved": bool(row[7]),
                    "resolved_at": row[8]
                })
            
            conn.close()
            return alerts
        except Exception as e:
            logger.error(f"获取告警记录失败：{e}")
            return []
    
    def get_metrics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """获取历史性能指标"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            since_time = datetime.now() - timedelta(hours=hours)
            cursor.execute("""
                SELECT timestamp, cpu_percent, memory_percent, disk_percent, api_latency_avg, active_tasks
                FROM system_metrics
                WHERE timestamp >= ?
                ORDER BY timestamp ASC
            """, [since_time.isoformat()])
            
            metrics = []
            for row in cursor.fetchall():
                metrics.append({
                    "timestamp": row[0],
                    "cpu_percent": row[1],
                    "memory_percent": row[2],
                    "disk_percent": row[3],
                    "api_latency_avg": row[4],
                    "active_tasks": row[5]
                })
            
            conn.close()
            return metrics
        except Exception as e:
            logger.error(f"获取历史指标失败：{e}")
            return []
    
    def save_current_metrics(self):
        """保存当前指标到数据库"""
        try:
            metrics = self.get_system_metrics()
            if not metrics:
                return
            
            latency_stats = self.get_api_latency_stats()
            task_status = self.get_task_queue_status()
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO system_metrics 
                   (cpu_percent, memory_percent, disk_percent, api_latency_avg, active_tasks, completed_tasks, failed_tasks)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                [
                    metrics.cpu_percent,
                    metrics.memory_percent,
                    metrics.disk_percent,
                    latency_stats["avg_ms"] / 1000,
                    task_status.get("pending", 0),
                    task_status.get("completed_today", 0),
                    task_status.get("failed_today", 0)
                ]
            )
            conn.commit()
            conn.close()
            
            # 添加到内存历史
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]
        except Exception as e:
            logger.error(f"保存当前指标失败：{e}")


# 全局监控服务实例
monitor_service = MonitorService()
