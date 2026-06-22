#!/usr/bin/env python3
"""
数据库迁移脚本 - 添加数据审核功能（Agent-15）
执行此脚本将添加审核状态字段和审核日志表
"""

import sqlite3
import os

# 数据库路径
DB_PATH = "/root/.openclaw/workspace/大学录取信息整理系统/data/admission_system.db"

def migrate():
    """执行数据库迁移"""
    if not os.path.exists(DB_PATH):
        print(f"❌ 数据库文件不存在：{DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("🔍 检查现有表结构...")
        
        # 1. 检查 admission_records 表的列
        cursor.execute("PRAGMA table_info(admission_records)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # 2. 添加审核状态字段（如果不存在）
        new_columns = []
        if 'review_status' not in columns:
            cursor.execute("ALTER TABLE admission_records ADD COLUMN review_status TEXT DEFAULT 'pending'")
            new_columns.append('review_status')
            print("✅ 添加字段：review_status")
        
        if 'reviewed_at' not in columns:
            cursor.execute("ALTER TABLE admission_records ADD COLUMN reviewed_at TIMESTAMP")
            new_columns.append('reviewed_at')
            print("✅ 添加字段：reviewed_at")
        
        if 'reviewed_by' not in columns:
            cursor.execute("ALTER TABLE admission_records ADD COLUMN reviewed_by INTEGER")
            new_columns.append('reviewed_by')
            print("✅ 添加字段：reviewed_by")
        
        if 'review_comment' not in columns:
            cursor.execute("ALTER TABLE admission_records ADD COLUMN review_comment TEXT")
            new_columns.append('review_comment')
            print("✅ 添加字段：review_comment")
        
        if not new_columns:
            print("✓ 审核状态字段已存在")
        
        # 3. 创建审核日志表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                previous_status TEXT,
                new_status TEXT NOT NULL,
                comment TEXT,
                reviewer_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (record_id) REFERENCES admission_records(id),
                FOREIGN KEY (reviewer_id) REFERENCES users(id)
            )
        """)
        print("✅ 创建表：review_logs")
        
        # 4. 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_record ON review_logs(record_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_reviewer ON review_logs(reviewer_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_created ON review_logs(created_at)")
        print("✅ 创建审核日志索引")
        
        # 5. 为现有记录设置默认审核状态
        cursor.execute("""
            UPDATE admission_records 
            SET review_status = 'approved' 
            WHERE is_verified = 1 AND review_status IS NULL
        """)
        updated_count = cursor.rowcount
        print(f"✅ 更新现有已验证记录为已通过状态：{updated_count} 条")
        
        # 6. 未验证的记录设为待审核
        cursor.execute("""
            UPDATE admission_records 
            SET review_status = 'pending' 
            WHERE is_verified = 0 AND review_status IS NULL
        """)
        pending_count = cursor.rowcount
        print(f"✅ 设置待审核记录：{pending_count} 条")
        
        conn.commit()
        print("\n🎉 数据库迁移完成！")
        print("\n新增功能:")
        print("  - 审核状态字段 (review_status, reviewed_at, reviewed_by, review_comment)")
        print("  - 审核日志表 (review_logs)")
        print("  - 支持单条/批量审核")
        print("  - 审核历史追溯")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ 迁移失败：{str(e)}")
        return False
        
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("大学录取信息整理系统 - 数据审核功能数据库迁移")
    print("=" * 60)
    print()
    
    success = migrate()
    
    if success:
        print("\n✅ 迁移成功！可以重启应用使用新功能。")
        exit(0)
    else:
        print("\n❌ 迁移失败，请检查错误信息。")
        exit(1)
