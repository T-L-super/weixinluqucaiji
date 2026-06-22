# 完成时间：2026-03-19 00:00 UTC
"""
大学录取信息采集器模块
负责从各种来源采集录取信息数据（纯图片识别模式）
"""
import os
import json
# import sqlite3 - replaced by db_config
from datetime import datetime
from typing import List, Dict, Any, Optional
import sys

class AdmissionCollector:
    """录取信息采集器（纯图片识别模式）"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            data_dir = os.path.join(os.path.dirname(__file__), "../../data")
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, "admission_system.db")
        self.db_path = db_path
    
    def get_connection(self):
        conn = get_db_connection()
        # conn.row_factory - handled by get_db_connection()
        return conn
    
    def parse_admission_text(self, text: str) -> List[Dict[str, Any]]:
        """
        解析录取文本（已改为使用图片识别，保留兼容接口）
        原正则表达式方法已移除，如需解析请使用图片识别方式
        """
        return []
    
    def batch_import(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        conn = self.get_connection()
        cursor = conn.cursor()
        success_count = 0
        failed_count = 0
        duplicate_count = 0
        for record in records:
            try:
                exec_sql(cursor, "SELECT id FROM admission_records WHERE student_id = ?", [record.get("student_id")])
                if cursor.fetchone():
                    duplicate_count += 1
                    continue
                cursor.execute('''
                    INSERT INTO admission_records 
                    (student_name, student_id, university, major, admission_type, score, province, year, status, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', [
                    record.get("student_name"), record.get("student_id"), record.get("university"),
                    record.get("major"), record.get("admission_type"), record.get("score"),
                    record.get("province"), record.get("year"), record.get("status", "pending"),
                    record.get("notes")
                ])
                success_count += 1
            except Exception as e:
                failed_count += 1
        conn.commit()
        conn.close()
        return {"success": success_count, "failed": failed_count, "duplicate": duplicate_count, "total": len(records)}
    
    def export_records(self, output_path: str, format: str = "json") -> str:
        conn = self.get_connection()
        cursor = conn.cursor()
        exec_sql(cursor, "SELECT * FROM admission_records ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        records = [dict(row) for row in rows]
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        if format == "json":
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
        elif format == "csv":
            import csv
            if records:
                with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=records[0].keys())
                    writer.writeheader()
                    writer.writerows(records)
        return output_path
    
    def get_statistics(self) -> Dict[str, Any]:
        conn = self.get_connection()
        cursor = conn.cursor()
        exec_sql(cursor, "SELECT COUNT(*) FROM admission_records")
        total = cursor.fetchone()[0]
        exec_sql(cursor, "SELECT status, COUNT(*) FROM admission_records GROUP BY status")
        status_stats = {row[0]: row[1] for row in cursor.fetchall()}
        exec_sql(cursor, "SELECT university, COUNT(*) FROM admission_records GROUP BY university ORDER BY COUNT(*) DESC LIMIT 10")
        university_stats = {row[0]: row[1] for row in cursor.fetchall()}
        exec_sql(cursor, "SELECT year, COUNT(*) FROM admission_records WHERE year IS NOT NULL GROUP BY year ORDER BY year DESC")
        year_stats = {str(row[0]): row[1] for row in cursor.fetchall()}
        conn.close()
        return {"total": total, "by_status": status_stats, "by_university": university_stats, "by_year": year_stats, "generated_at": datetime.now().isoformat()}
    
    def cleanup_duplicates(self) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        exec_sql(cursor, 'SELECT student_id, COUNT(*) as cnt FROM admission_records GROUP BY student_id HAVING cnt > 1')
        duplicates = cursor.fetchall()
        deleted_count = 0
        for student_id, count in duplicates:
            exec_sql(cursor, '''DELETE FROM admission_records WHERE student_id = ? AND id NOT IN (SELECT MIN(id) FROM admission_records WHERE student_id = ?)''', [student_id, student_id])
            deleted_count += count - 1
        conn.commit()
        conn.close()
        return deleted_count

from app.db_config import get_db_connection, exec_sql
def create_collector(db_path: str = None) -> AdmissionCollector: