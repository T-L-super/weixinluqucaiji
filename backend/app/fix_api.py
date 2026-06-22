#!/usr/bin/env python3
"""
修复 /api/records 接口 - 使用 JOIN 查询关联表
返回完整的录取信息（包含来源学校、大学、国家的实际名称）
"""

# import sqlite3 - replaced by db_config
import os
from typing import List, Dict

from app.db_config import get_db_connection
def get_db_connection():