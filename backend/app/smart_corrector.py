"""
语义大模型智能修正模块
在数据存入暂存表之前，使用大模型对采集的数据进行语义理解和智能修正
如：'年月批次留学韩国东国大学' → '东国大学'
"""
import os
import json
# import sqlite3 - replaced by db_config
import logging
from typing import List, Dict, Optional
from openai import OpenAI

logger = logging.getLogger('SmartCorrector')

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/admission_system.db")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "../data/llm_config.json")

DASHSCOPE_API_KEY = "sk-Df27ROwppc1QI9aYiXhWV7L3JGAwjYzzESTu09J9dRLgMeZG"
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

CORRECTION_PROMPT = """你是一个大学录取数据修正助手。我会给你一些从网页中提取的录取记录，这些记录可能包含错误或不精确的字段。

请逐条检查并修正每条记录，重点关注以下问题：

1. **大学名称修正**：
   - 大学名中可能混入了无关文字（如"年月批次留学韩国东国大学"应改为"东国大学"），请提取出真正的大学名称。
   - **特别注意**：如果大学字段包含明显的叙述性文字或动词短语（如"绩通过后方可进入国外本科大学"、"我们祝贺第一批已收获大学"），这些根本不是大学名，应该将整个大学字段标记为空字符串""。
   - 真正的大学名应该：①包含"大学"、"学院"等标识词；②不包含动词（如"通过"、"进入"、"祝贺"、"获得"等）；③长度合理（2-15个中文字符）。
   - 如果大学名本身就是正确的则保留。

2. **国家补充**：如果国家字段为空或不正确，根据大学名称推断正确的国家。

3. **专业名称清理**：专业名中如果混入了多余的文字（如编号、标点、多余描述），请清理为纯专业名。

4. **学生姓名修正**：如果姓名明显不是真实人名（如被填成了URL片段、学校名片段、或者"我们"、"他们"等代词），标记为空字符串""。

修正规则：
- 只修正明显错误，不确定的保留原值
- 大学名必须是一个具体大学，不能是泛称，更不能包含叙述性文字
- 修正后的字段放入 fixed_xxx 中，未修正的字段返回原文
- 为每条记录添加 correction_summary 简要说明做了哪些修正

以 JSON 数组格式逐条返回，每条包含：
- index: 原始序号
- fixed_student_name_cn: 修正后的学生姓名
- fixed_university_cn: 修正后的大学名称
- fixed_major_cn: 修正后的专业名称
- fixed_country: 修正后的国家
- correction_summary: 修正摘要（如"大学名从'年月批次留学韩国东国大学'修正为'东国大学'"；如"大学名'绩通过后方可进入国外本科大学'不是有效大学名，已清空"；如无修正填"无需修正"）

只返回 JSON，不要任何其他文字。

待修正记录：
{records_json}"""


def _load_config() -> dict:
    defaults = {"enabled": True, "provider": "dashscope", "api_base": DASHSCOPE_BASE_URL,
                "api_key": DASHSCOPE_API_KEY, "model": "qwen3.5-plus",
                "max_tokens": 2000, "temperature": 0.1, "batch_size": 20, "timeout": 60}
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            for k in ("api_base", "api_key", "model", "max_tokens", "temperature", "batch_size", "timeout"):
                if k in cfg and cfg[k]:
                    defaults[k] = cfg[k]
            if "corrector_enabled" in cfg:
                defaults["enabled"] = cfg["corrector_enabled"]
    except Exception:
        pass
    return defaults


async def correct_records(records: List[Dict]) -> List[Dict]:
    """
    使用大模型对采集记录进行智能修正

    Args:
        records: 原始采集记录列表

    Returns:
        修正后的记录列表（保留所有字段，仅修正有问题的字段）
    """
    if not records:
        return records

    config = _load_config()
    if not config.get("corrector_enabled", True):
        logger.info("SmartCorrector: disabled via config")
        return records

    logger.info("SmartCorrector: temporarily disabled for testing")
    return records
    api_base = config.get("api_base") or DASHSCOPE_BASE_URL
    model = config.get("model") or "qwen3.5-plus"
    timeout = config.get("timeout", 60)

    if not api_key:
        logger.warning("SmartCorrector: no API key configured, skipping correction")
        return records

    client = OpenAI(api_key=api_key, base_url=api_base, timeout=timeout)

    batch_size = min(config.get("batch_size", 20), 20)
    corrected_all = []

    for batch_start in range(0, len(records), batch_size):
        batch = records[batch_start:batch_start + batch_size]
        batch_for_llm = []
        for idx, r in enumerate(batch):
            batch_for_llm.append({
                "index": idx,
                "student_name_cn": r.get("student_name_cn", ""),
                "university_cn": r.get("university_cn", ""),
                "major_cn": r.get("major_cn", ""),
                "country": r.get("country", ""),
            })

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": CORRECTION_PROMPT.format(records_json=json.dumps(batch_for_llm, ensure_ascii=False))}],
                temperature=0.1,
                max_tokens=2000,
            )

            content = response.choices[0].message.content or ""
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            corrections = json.loads(content)
            if not isinstance(corrections, list):
                corrections = [corrections]

            correction_map = {}
            for corr in corrections:
                idx = corr.get("index", -1)
                if 0 <= idx < len(batch):
                    correction_map[idx] = corr

            for idx, r in enumerate(batch):
                corr = correction_map.get(idx, {})
                fixed_university = corr.get("fixed_university_cn", "").strip()
                if fixed_university and fixed_university != r.get("university_cn", ""):
                    r["university_cn"] = fixed_university

                fixed_country = corr.get("fixed_country", "").strip()
                if fixed_country and (not r.get("country") or r.get("country") == "未知"):
                    r["country"] = fixed_country

                fixed_major = corr.get("fixed_major_cn", "").strip()
                if fixed_major and fixed_major != r.get("major_cn", ""):
                    r["major_cn"] = fixed_major

                fixed_name = corr.get("fixed_student_name_cn", "").strip()
                if fixed_name and fixed_name != r.get("student_name_cn", ""):
                    r["student_name_cn"] = fixed_name

                summary = corr.get("correction_summary", "")
                if summary and summary != "无需修正":
                    r["notes"] = (r.get("notes") or "") + "[AI修正: " + summary + "] "

            corrected_all.extend(batch)
            logger.info(f"SmartCorrector: corrected batch {batch_start // batch_size + 1}, {len(batch)} records")

        except json.JSONDecodeError as e:
            logger.warning(f"SmartCorrector: JSON parse error, keeping original records: {e}")
            corrected_all.extend(batch)
        except Exception as e:
            logger.warning(f"SmartCorrector: LLM call failed, keeping original records: {e}")
            corrected_all.extend(batch)

    return corrected_all
