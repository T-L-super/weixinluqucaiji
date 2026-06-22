"""
LLM 审核筛选模块 - 已停用
此模块已被移除，仅保留空实现以保持兼容性
"""
import os
import json
# import sqlite3 - replaced by db_config
from typing import List, Tuple

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/admission_system.db")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "../data/llm_config.json")

DEFAULT_CONFIG = {
    "enabled": False,
    "provider": "openai",
    "api_base": "https://api.openai.com/v1",
    "api_key": "",
    "model": "gpt-3.5-turbo",
    "max_tokens": 500,
    "temperature": 0.1,
    "batch_size": 10,
    "timeout": 30,
}


from app.db_config import get_db_connection
def _load_config() -> dict: