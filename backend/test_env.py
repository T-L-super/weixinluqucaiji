#!/usr/bin/env python3
# 测试环境
print("Testing Python environment...")
try:
    import sqlite3
    print("✅ sqlite3 imported")
except ImportError as e:
    print(f"❌ sqlite3 import failed: {e}")

try:
    import pymysql
    print("✅ pymysql imported")
except ImportError as e:
    print(f"❌ pymysql import failed: {e}")

print("\nChecking SQLite database...")
import os
db_path = os.path.join(os.path.dirname(__file__), "data/admission_system.db")
print(f"Database path: {db_path}")
print(f"Exists: {os.path.exists(db_path)}")
