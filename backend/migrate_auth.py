#!/usr/bin/env python3
# 完成时间：2026-03-20 16:00 UTC - Agent-10 用户权限管理
"""
数据库迁移脚本 - 用户权限管理系统
初始化用户、角色和用户角色关联表
"""

import sqlite3
import os
from datetime import datetime
from passlib.context import CryptContext

# 数据库路径
DB_PATH = "/root/.openclaw/workspace/大学录取信息整理系统/data/admission_system.db"

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def init_auth_tables():
    """初始化用户认证相关表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("📦 开始初始化用户权限管理系统...")
    
    # 创建角色表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            permissions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ 创建 roles 表")
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            role_id INTEGER,
            is_active INTEGER DEFAULT 1,
            last_login TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (role_id) REFERENCES roles(id)
        )
    ''')
    print("✓ 创建 users 表")
    
    # 创建用户角色关联表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role_id INTEGER NOT NULL,
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            assigned_by INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (role_id) REFERENCES roles(id),
            UNIQUE(user_id, role_id)
        )
    ''')
    print("✓ 创建 user_roles 表")
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_roles_user ON user_roles(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_roles_role ON user_roles(role_id)')
    print("✓ 创建索引")
    
    # 初始化默认角色
    default_roles = [
        ('super_admin', '超级管理员', '["*"]'),
        ('data_admin', '数据管理员', '["read", "write", "delete", "manage_users"]'),
        ('normal_user', '普通用户', '["read"]')
    ]
    
    for role_name, description, permissions in default_roles:
        cursor.execute('SELECT id FROM roles WHERE name = ?', (role_name,))
        if not cursor.fetchone():
            cursor.execute(
                'INSERT INTO roles (name, description, permissions) VALUES (?, ?, ?)',
                (role_name, description, permissions)
            )
            print(f"✓ 创建角色：{role_name}")
    
    # 创建默认超级管理员账户
    cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        password_hash = pwd_context.hash("admin123")
        cursor.execute(
            'INSERT INTO users (username, email, password_hash, full_name, role_id) VALUES (?, ?, ?, ?, ?)',
            ('admin', 'admin@beiyouschool.com', password_hash, '系统管理员', 1)
        )
        print("✓ 创建默认管理员账户：admin / admin123")
    else:
        print("ℹ️  管理员账户已存在")
    
    conn.commit()
    conn.close()
    
    print("\n✅ 用户权限管理系统初始化完成！")
    print("\n📋 角色说明:")
    print("   - 超级管理员 (super_admin): 全部权限")
    print("   - 数据管理员 (data_admin): 数据管理权限")
    print("   - 普通用户 (normal_user): 只读权限")
    print("\n🔐 默认账户:")
    print("   用户名：admin")
    print("   密码：admin123")
    print("   ⚠️  请在生产环境中立即修改密码！")


if __name__ == "__main__":
    init_auth_tables()
