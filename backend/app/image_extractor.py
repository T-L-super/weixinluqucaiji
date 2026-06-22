# -*- coding: utf-8 -*-
"""
图片识别提取模块 - 方案 A
功能：通过 URL 打开文章 → 截图 → AI 视觉模型识别 → 提取录取字段
"""

import os
import base64
import io
import time
import re
import json
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict

from playwright.async_api import async_playwright, Page
from openai import OpenAI
from PIL import Image

logger = logging.getLogger('ImageExtractor')

DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "sk-Df27ROwppc1QI9aYiXhWV7L3JGAwjYzzESTu09J9dRLgMeZG")
DASHSCOPE_BASE_URL = "https://newapi.beiyou.org.cn/v1"
DASHSCOPE_COMPAT_BASE_URL = "https://newapi.beiyou.org.cn/v1"

VISION_MODEL = "qwen3.6-plus"

MODEL_API_BASE_MAP = {
    "qwen3.5-plus": DASHSCOPE_COMPAT_BASE_URL,
    "qwen3.6-plus": DASHSCOPE_COMPAT_BASE_URL,
}


@dataclass
class ExtractedRecord:
    """从图片中提取的单条录取记录"""
    student_name_cn: str = ''
    student_name_en: str = ''
    university_cn: str = ''
    university_en: str = ''
    major_cn: str = ''
    major_en: str = ''
    country: str = ''
    admission_year: str = ''
    scholarship_amount: str = ''
    scholarship_currency: str = ''
    admission_type: str = ''
    admission_status: str = ''
    article_url: str = ''
    source_image_index: int = -1
    data_source: str = ''


def _img_to_base64(img: Image.Image) -> str:
    """将图片转换为 base64 编码的 data URL"""
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"


def _create_vision_client():
    """创建视觉模型客户端"""
    return OpenAI(api_key=DASHSCOPE_API_KEY, base_url=DASHSCOPE_BASE_URL)


async def _capture_page(url: str, timeout: int = 30) -> Dict:
    """
    使用 Playwright 打开 URL，截图并提取所有图片
    返回：{full_screenshot, page_images, page_title, page_url}
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        try:
            await page.goto(url, wait_until='networkidle', timeout=timeout * 1000)
            
            page_title = await page.title()
            
            # 渐进式滚动确保所有懒加载图片都被触发
            logger.info("开始渐进式滚动以触发懒加载...")
            await page.evaluate("""
                async () => {
                    const scrollHeight = document.body.scrollHeight;
                    const viewportHeight = window.innerHeight;
                    const step = viewportHeight;
                    let currentScroll = 0;
                    
                    while (currentScroll < scrollHeight) {
                        window.scrollTo(0, currentScroll);
                        currentScroll += step;
                        await new Promise(r => setTimeout(r, 300));
                    }
                    
                    window.scrollTo(0, scrollHeight);
                    await new Promise(r => setTimeout(r, 1000));
                    
                    const images = document.querySelectorAll('img');
                    const loadPromises = Array.from(images).map(img => {
                        if (img.complete) return Promise.resolve();
                        return new Promise(resolve => {
                            img.onload = resolve;
                            img.onerror = resolve;
                            setTimeout(resolve, 2000);
                        });
                    });
                    
                    await Promise.all(loadPromises);
                }
            """)
            logger.info("渐进式滚动完成，所有图片已加载")
            
            await page.wait_for_timeout(1000)
            
            full_screenshot = await page.screenshot(full_page=True, type='png')
            
            page_images = []
            
            image_elements = await page.query_selector_all('img')
            logger.info(f"找到 {len(image_elements)} 个 img 元素")
            
            for idx, img_elem in enumerate(image_elements[:30]):
                try:
                    img_src = await img_elem.get_attribute('src')
                    if not img_src:
                        continue
                    if not img_src.startswith('http'):
                        continue
                    
                    box = await img_elem.bounding_box()
                    if not box:
                        continue
                    
                    width = box.get('width', 0)
                    height = box.get('height', 0)
                    
                    min_size = 30
                    if width >= min_size and height >= min_size:
                        try:
                            screenshot_bytes = await asyncio.wait_for(
                                img_elem.screenshot(type='png'),
                                timeout=8
                            )
                            if screenshot_bytes and len(screenshot_bytes) > 300:
                                page_images.append({
                                    'url': img_src,
                                    'width': width,
                                    'height': height,
                                    'index': idx,
                                    'data': screenshot_bytes
                                })
                                logger.debug(f"添加图片 {idx}: {img_src[:50]}... ({width}x{height}, {len(screenshot_bytes)} bytes)")
                        except asyncio.TimeoutError:
                            logger.warning(f"图片 {idx} 截图超时，跳过")
                except Exception as e:
                    logger.warning(f"加载图片 {idx} 失败: {e}")
            
            logger.info(f"页面截图完成: {page_title}, 整页截图 {len(full_screenshot)} bytes, 图片数: {len(page_images)}")
            
            return {
                'full_screenshot': full_screenshot,
                'page_images': page_images,
                'page_title': page_title,
                'page_url': url,
            }
            
        except Exception as e:
            logger.error(f"页面加载失败: {e}")
            raise
        finally:
            await browser.close()


def _analyze_image_with_vision(image_data: bytes, prompt: str) -> str:
    """使用 qwen3.6-plus 视觉模型分析图片"""
    client = _create_vision_client()
    
    img = Image.open(io.BytesIO(image_data))
    if img.width <= 10 or img.height <= 10:
        img = img.resize((max(img.width * 10, 100), max(img.height * 10, 100)))
    b64 = _img_to_base64(img)
    
    try:
        resp = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": b64}}
                ]
            }],
            max_tokens=2000,
            temperature=0.1
        )
        return resp.choices[0].message.content
    except Exception as e:
        logger.error(f"视觉模型调用失败: {e}")
        raise


def _analyze_image_with_vision_model(image_data: bytes, prompt: str, model: str) -> str:
    api_base = MODEL_API_BASE_MAP.get(model, DASHSCOPE_COMPAT_BASE_URL)
    client = OpenAI(api_key=DASHSCOPE_API_KEY, base_url=api_base)
    img = Image.open(io.BytesIO(image_data))
    if img.width <= 10 or img.height <= 10:
        img = img.resize((max(img.width * 10, 100), max(img.height * 10, 100)))
    b64 = _img_to_base64(img)
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": b64}}
                ]
            }],
            max_tokens=2000,
            temperature=0.1
        )
        return resp.choices[0].message.content
    except Exception as e:
        error_str = str(e)
        if "401" in error_str or "authentication" in error_str.lower() or "api key" in error_str.lower():
            logger.error(f"API Key无效，请检查配置: {e}")
        else:
            logger.error(f"视觉模型调用失败(model={model}): {e}")
        raise


def _parse_vision_response(text: str) -> List[ExtractedRecord]:
    """解析视觉模型返回的文本，提取结构化录取记录"""
    records = []
    
    # 新字段名到旧字段名的映射
    field_mapping = {
        'student_name': 'student_name_cn',
        'university': 'university_cn',
        'major': 'major_cn',
    }
    
    json_match = re.search(r'\[?\s*\{.*\}\s*\]?', text, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group())
            if isinstance(data, dict):
                data = [data]
            if isinstance(data, list):
                for item in data:
                    record = ExtractedRecord()
                    for key, val in item.items():
                        # 映射新字段名到旧字段名
                        mapped_key = field_mapping.get(key, key)
                        if hasattr(record, mapped_key):
                            setattr(record, mapped_key, str(val) if val else '')
                    records.append(record)
                return records
        except json.JSONDecodeError:
            pass
    
    lines = text.strip().split('\n')
    current_record = ExtractedRecord()
    has_data = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        field_map = {
            r'(?:学生|姓名|中文名|名字)：?': 'student_name_cn',
            r'(?:英文名|English name|英文名)：?': 'student_name_en',
            r'(?:大学|院校|学校|录取学校|录取院校|offer)：?': 'university_cn',
            r'(?:大学英|University|学校英)：?': 'university_en',
            r'(?:专业|Major|program|课程)：?': 'major_cn',
            r'(?:专业英|Major English|专业英文)：?': 'major_en',
            r'(?:国家|Country|地区)：?': 'country',
            r'(?:年份|Year|录取年份|入学年份|入学年)：?': 'admission_year',
            r'(?:奖学金|Scholarship|奖学金金额)：?': 'scholarship_amount',
            r'(?:货币|Currency)：?': 'scholarship_currency',
            r'(?:类型|Type|录取类型|学位)：?': 'admission_type',
            r'(?:状态|Status|录取状态)：?': 'admission_status',
            r'(?:数据来源|来源|公众号|作者)：?': 'data_source',
        }
        
        matched = False
        for pattern, field_name in field_map.items():
            match = re.match(rf'{pattern}(.+)', line)
            if match:
                value = match.group(1).strip()
                if value and value != '未知':
                    setattr(current_record, field_name, value)
                    has_data = True
                matched = True
                break
        
        if not matched and has_data:
            parts = line.split('：') if '：' in line else line.split(':')
            if len(parts) == 2:
                key, value = parts[0].strip(), parts[1].strip()
                for field_name in field_map.values():
                    if key.lower() in field_name.lower() or field_name.lower() in key.lower():
                        if value and value != '未知':
                            setattr(current_record, field_name, value)
                            has_data = True
    
    if has_data:
        records.append(current_record)
    
    return records


def extract_from_url(url: str, timeout: int = 30) -> Dict:
    """主入口：从 URL 提取录取信息"""
    result = {
        "success": False,
        "page_title": "",
        "page_url": url,
        "records": [],
        "images_analyzed": 0,
        "error": ""
    }
    
    try:
        page_data = asyncio.run(_capture_page(url, timeout))
        result['page_title'] = page_data['page_title']
        result['page_url'] = page_data.get('page_url', url)
        
        full_screenshot = page_data['full_screenshot']
        prompt = """你是一名专业的全球大学录取信息采集员，熟背全球所有大学及其专业设置，精通中英双语信息提取，现在的工作是浏览图片信息，提取学生被大学录取的信息。

【绝对禁止幻觉！】
- **严禁编造任何信息！只能提取图片中明确显示的文字内容！**
- **如果图片中没有录取信息，返回空数组 []！**
- **绝对不能根据标题或上下文猜测、联想、编造学生姓名、大学名称等信息！**
- **不确定的字段填"未知"，绝对不能自己编造！**

【重要提醒】图片中可能包含多条录取记录！一个学生可能同时被多所大学录取，请务必识别出所有录取信息，不要遗漏任何一条！

【核心要求】
- 学生姓名必须是真实姓名，如"张三"、"李华"、"Zhang San"等；像"同学"、"内尔的同学"、"老师与同学"、"更多的同学"等不是真实姓名，不应提取，像张主任，李校长这类的人一听就不是学生，也不应提取
- 大学名称必须是真实大学，如"香港大学"、"帝国理工学院"、"The University of Hong Kong"等；像"就读于伦敦布鲁内尔大学"包含动词的不是纯大学名称，需提取纯大学部分
- 学生姓名和大学名称不分中英文，统一填写识别到的名称即可
- 只返回指定字段，不要添加任何额外字段

请仔细识别图片中的所有录取相关信息，务必做到：

【必填字段】
- student_name: 学生姓名（不分中英文，识别到什么就填什么，如：张三、李华、Zhang San。**如果图片中没有明确显示学生姓名，就直接放弃采集这条数据，不要返回该条记录！**）
- university: 录取大学名称（不分中英文，识别到什么就填什么，如：香港大学、帝国理工学院、The University of Hong Kong。**如果图片中没有明确显示大学名称，就直接放弃采集这条数据，不要返回该条记录！**）

【可选字段】
- major: 录取专业名称（不分中英文，如：城市设计、生物医学工程、Computer Science）
- country: 国家/地区（**重要**：请根据录取大学名称推断其所在国家/地区。例如：看到"帝国理工学院"填"英国"，看到"香港大学"填"中国香港"，看到"东国大学"填"韩国"。如无法推断则填"未知"）
- admission_year: 录取年份（如：2024、2025）
- scholarship_amount: 奖学金金额（纯数字，如：50000）
- scholarship_currency: 奖学金货币（如：港币、美元、英镑、人民币）
- admission_type: 录取类型（如：硕士、本科、博士、MBA）
- admission_status: 录取状态（如：录取、有条件录取、已入学）
- data_source: 数据来源/发布公众号（**重要**：必须准确提取发布这篇文章的公众号名称，通常位于标题下方小字处，如："XX国际教育"、"XX升学指导"。如图片中确实没有显示公众号名称，则填"未知"）

【提取规则】
1. 学生姓名验证：必须是真实姓名，排除"同学"、"老师"、"他们"、"我们"等泛称
2. 大学名称验证：必须是纯大学名称，排除包含动词或多余描述的文本，但是如果是某某大学某某分校，则可以提取
3. 大学名称要使用官方译名
4. **国家推断**：利用你的全球大学知识库，根据大学名称准确判断其所在国家/地区（中国香港、中国澳门、中国台湾需特别注明）
5. **数据来源识别**：仔细寻找标题下方的亮色小字，提取公众号名称（这是识别文章出处的关键信息）
6. 【重点】一个学生可能被多所大学录取，每位学生的每一份录取通知书都要作为独立记录提取
7. 仔细检查图片的每个部分，确保不遗漏任何录取记录
8. 注意区分学生姓名和学校名称，不要混淆

请以严格的 JSON 数组格式返回，每条记录一个对象，字段名严格按照上述指定名称。如果某些字段不确定，填"未知"。只返回 JSON 数组，不要其他任何文字。"""
        
        try:
            vision_text = _analyze_image_with_vision(full_screenshot, prompt)
            logger.info(f"整页识别结果: {vision_text[:200]}...")
            page_records = _parse_vision_response(vision_text)
            for r in page_records:
                r.article_url = url
            result['records'].extend(page_records)
            result['images_analyzed'] += 1
        except Exception as e:
            logger.warning(f"整页截图识别失败: {e}")
        
        for img_info in page_data['page_images'][:5]:
            try:
                img_data = img_info.get('data')
                if img_data and len(img_data) > 1000:
                    img_prompt = f"""这是留学录取海报或喜报图片，请提取所有录取信息。

【核心要求】
- 学生姓名必须是真实姓名，排除"同学"、"老师"等泛称
- 专业名称必须是纯专业名称，排除包含大学名称的文本
- 只返回指定字段，不要添加任何额外字段

以 JSON 格式返回，字段：student_name_cn, university_cn, major_cn, country, admission_year, scholarship_amount
只返回 JSON，不要其他文字。"""
                    img_text = _analyze_image_with_vision(img_data, img_prompt)
                    img_records = _parse_vision_response(img_text)
                    for r in img_records:
                        r.article_url = url
                        r.source_image_index = img_info['index']
                    result['records'].extend(img_records)
                    result['images_analyzed'] += 1
                    logger.info(f"图片 {img_info['url'][:60]}... 识别成功")
            except Exception as e:
                logger.warning(f"图片 {img_info.get('url', '')} 分析失败: {e}")
                continue
        
        seen = set()
        unique_records = []
        for r in result['records']:
            key = (r.student_name_cn, r.university_cn)
            if key not in seen and (r.student_name_cn or r.university_cn):
                seen.add(key)
                unique_records.append(r)
        
        result['records'] = unique_records
        result['success'] = len(unique_records) > 0
        
        if not result['success']:
            result['error'] = '未能从图片中提取到有效的录取信息，请检查页面是否包含录取相关内容'
        
    except Exception as e:
        result['error'] = f'页面访问失败: {str(e)}'
        logger.error(f"提取失败: {e}")
    
    return result


async def extract_from_url_with_model(url: str, model: str, timeout: int = 30) -> Dict:
    """使用指定模型从 URL 提取录取信息"""
    result = {
        "success": False,
        "page_title": "",
        "page_url": url,
        "records": [],
        "images_analyzed": 0,
        "error": ""
    }
    
    api_key_invalid = False
    
    try:
        page_data = await _capture_page(url, timeout)
        result['page_title'] = page_data['page_title']
        result['page_url'] = page_data.get('page_url', url)
        
        full_screenshot = page_data['full_screenshot']
        prompt = """你是一名专业的全球大学录取信息采集员，熟背全球所有大学及其专业设置，精通中英双语信息提取。

【绝对禁止幻觉！】
- **严禁编造任何信息！只能提取图片中明确显示的文字内容！**
- **如果图片中没有录取信息，返回空数组 []！**
- **绝对不能根据标题或上下文猜测、联想、编造学生姓名、大学名称等信息！**
- **不确定的字段填"未知"，绝对不能自己编造！**

【重要提醒】图片中可能包含多条录取记录！一个学生可能同时被多所大学录取，请务必识别出所有录取信息，不要遗漏任何一条！

【核心要求】
- 学生姓名必须是真实姓名，如"张三"、"李华"、"Zhang San"等；像"同学"、"内尔的同学"、"老师与同学"、"更多的同学"等不是真实姓名，不应提取
- 大学名称必须是真实大学，如"香港大学"、"帝国理工学院"、"The University of Hong Kong"等；像"就读于伦敦布鲁内尔大学"包含动词的不是纯大学名称，需提取纯大学部分
- 学生姓名和大学名称不分中英文，统一填写识别到的名称即可
- 只返回指定字段，不要添加任何额外字段

请仔细识别图片中的所有录取相关信息，务必做到：

【必填字段】
- student_name: 学生姓名（不分中英文，识别到什么就填什么，如：张三、李华、Zhang San。如果图片中没有明确显示，就不采集这条数据）
- university: 录取大学名称（不分中英文，识别到什么就填什么，如：香港大学、帝国理工学院、The University of Hong Kong。如果图片中没有明确显示，就不采集这条数据）

【可选字段】
- major: 录取专业名称（不分中英文，如：城市设计、生物医学工程、Computer Science）
- country: 国家/地区（**重要**：请根据录取大学名称推断其所在国家/地区。例如：看到"帝国理工学院"填"英国"，看到"香港大学"填"中国香港"，看到"东国大学"填"韩国"。如无法推断则填"未知"）
- admission_year: 录取年份（如：2024、2025）
- scholarship_amount: 奖学金金额（纯数字，如：50000）
- scholarship_currency: 奖学金货币（如：港币、美元、英镑、人民币）
- admission_type: 录取类型（如：硕士、本科、博士、MBA）
- admission_status: 录取状态（如：录取、有条件录取、已入学）
- data_source: 数据来源/发布公众号（**重要**：必须准确提取发布这篇文章的公众号名称，通常位于标题下方小字处，如："XX国际教育"、"XX升学指导"。如图片中确实没有显示公众号名称，则填"未知"）

【提取规则】
1. 学生姓名验证：必须是真实姓名，排除"同学"、"老师"、"他们"、"我们"等泛称
2. 大学名称验证：必须是纯大学名称，排除包含动词或多余描述的文本，但如果是某某大学某某分校之类的，则可以通过
3. 大学名称要使用官方译名
4. **国家推断**：利用你的全球大学知识库，根据大学名称准确判断其所在国家/地区（中国香港、中国澳门、中国台湾需特别注明）
5. **数据来源识别**：仔细寻找标题下方的亮色小字，提取公众号名称（这是识别文章出处的关键信息）
6. 【重点】一个学生可能被多所大学录取，每位学生的每一份录取通知书都要作为独立记录提取
7. 仔细检查图片的每个部分，确保不遗漏任何录取记录
8. 注意区分学生姓名和学校名称，不要混淆

请以严格的 JSON 数组格式返回，每条记录一个对象，字段名严格按照上述指定名称。如果某些字段不确定，填"未知"。只返回 JSON 数组，不要其他任何文字。"""
        
        if not api_key_invalid:
            try:
                vision_text = _analyze_image_with_vision_model(full_screenshot, prompt, model)
                logger.info(f"整页识别结果(model={model}): {vision_text[:200]}...")
                page_records = _parse_vision_response(vision_text)
                for r in page_records:
                    r.article_url = url
                result['records'].extend(page_records)
                result['images_analyzed'] += 1
            except Exception as e:
                error_str = str(e)
                if "401" in error_str or "authentication" in error_str.lower() or "api key" in error_str.lower():
                    api_key_invalid = True
                    logger.warning(f"API Key无效，跳过图片识别")
                else:
                    logger.warning(f"整页截图识别失败: {e}")
        
        if not api_key_invalid:
            for img_info in page_data['page_images'][:3]:  # 减少处理图片数量
                try:
                    img_data = img_info.get('data')
                    if img_data and len(img_data) > 1000:
                        img_prompt = f"""这是留学录取海报或喜报图片，请提取所有录取信息。

【核心要求】
- 学生姓名必须是真实姓名，排除"同学"、"老师"等泛称
- 专业名称必须是纯专业名称，排除包含大学名称的文本
- 只返回指定字段，不要添加任何额外字段

以 JSON 格式返回，字段：student_name_cn, university_cn, major_cn, country, admission_year, scholarship_amount
只返回 JSON，不要其他文字。"""
                        img_text = _analyze_image_with_vision_model(img_data, img_prompt, model)
                        img_records = _parse_vision_response(img_text)
                        for r in img_records:
                            r.article_url = url
                            r.source_image_index = img_info['index']
                        result['records'].extend(img_records)
                        result['images_analyzed'] += 1
                        logger.info(f"图片 {img_info['url'][:60]}... 识别成功，模型: {model}")
                except Exception as e:
                    error_str = str(e)
                    if "401" in error_str or "authentication" in error_str.lower() or "api key" in error_str.lower():
                        api_key_invalid = True
                        logger.warning(f"API Key无效，跳过后续图片识别")
                        break
                    else:
                        logger.warning(f"图片 {img_info.get('url', '')} 分析失败: {e}")
                        continue
        
        seen = set()
        unique_records = []
        for r in result['records']:
            key = (r.student_name_cn, r.university_cn)
            if key not in seen and (r.student_name_cn or r.university_cn):
                seen.add(key)
                unique_records.append(r)
        
        result['records'] = unique_records
        result['success'] = len(unique_records) > 0
        
        if not result['success']:
            result['error'] = '未能从图片中提取到有效的录取信息，请检查页面是否包含录取相关内容'
        
    except Exception as e:
        result['error'] = f'页面访问失败: {str(e)}'
        logger.error(f"提取失败: {e}")
    
    return result

import asyncio


async def extract_from_url_fullpage(url: str, timeout: int = 60) -> Dict:
    """仅使用整页截图从 URL 提取录取信息"""
    result = {
        "success": False,
        "page_title": "",
        "page_url": url,
        "records": [],
        "images_analyzed": 0,
        "error": ""
    }

    try:
        page_data = await _capture_page(url, timeout)
        result['page_title'] = page_data['page_title']
        result['page_url'] = page_data.get('page_url', url)

        full_screenshot = page_data['full_screenshot']
        prompt = """你是一名专业的全球大学录取信息采集员，熟背全球所有大学及其专业设置，精通中英双语信息提取。

【重要提醒】图片中可能包含多条录取记录！一个学生可能同时被多所大学录取，请务必识别出所有录取信息，不要遗漏任何一条！

【核心要求】
- 学生姓名必须是真实姓名，如"张三"、"李华"、"Zhang San"等；像"同学"、"内尔的同学"、"老师与同学"、"更多的同学"等不是真实姓名，不应提取
- 大学名称必须是真实大学，如"香港大学"、"帝国理工学院"、"The University of Hong Kong"等；像"就读于伦敦布鲁内尔大学"包含动词的不是纯大学名称，需提取纯大学部分
- 学生姓名和大学名称不分中英文，统一填写识别到的名称即可
- 只返回指定字段，不要添加任何额外字段

请仔细识别图片中的所有录取相关信息，务必做到：

【必填字段】
- student_name: 学生姓名（不分中英文，识别到什么就填什么，如：张三、李华、Zhang San）
- university: 录取大学名称（不分中英文，识别到什么就填什么，如：香港大学、帝国理工学院、The University of Hong Kong）

【可选字段】
- major: 录取专业名称（不分中英文，如：城市设计、生物医学工程、Computer Science）
- country: 国家/地区（如：中国香港、英国、美国、中国澳门、加拿大、澳大利亚）
- admission_year: 录取年份（如：2024、2025）
- scholarship_amount: 奖学金金额（纯数字，如：50000）
- scholarship_currency: 奖学金货币（如：港币、美元、英镑、人民币）
- admission_type: 录取类型（如：硕士、本科、博士、MBA）
- admission_status: 录取状态（如：录取、有条件录取、已入学）
- data_source: 数据来源/发布公众号（**重要**：必须准确提取发布这篇文章的公众号名称，通常位于标题下方小字处，如："XX国际教育"、"XX升学指导"。如图片中确实没有显示公众号名称，则填"未知"）

【提取规则】
1. 学生姓名验证：必须是真实姓名，排除"同学"、"老师"、"他们"、"我们"等泛称
2. 大学名称验证：必须是纯大学名称，排除包含动词或多余描述的文本
3. 大学名称要使用官方译名
4. 国家/地区要填写标准名称（中国香港、中国澳门、中国台湾需特别注明）
5. 【重点】一个学生可能被多所大学录取，每位学生的每一份录取通知书都要作为独立记录提取
6. 仔细检查图片的每个部分，确保不遗漏任何录取记录
7. 注意区分学生姓名和学校名称，不要混淆

请以严格的 JSON 数组格式返回，每条记录一个对象，字段名严格按照上述指定名称。如果某些字段不确定，填"未知"。只返回 JSON 数组，不要其他任何文字。"""

        vision_text = _analyze_image_with_vision(full_screenshot, prompt)
        logger.info(f"整页识别结果: {vision_text[:500]}...")
        page_records = _parse_vision_response(vision_text)
        logger.info(f"解析到 {len(page_records)} 条记录")
        for i, r in enumerate(page_records):
            logger.info(f"记录{i}: student_name_cn='{r.student_name_cn}', university_cn='{r.university_cn}'")
            r.article_url = url
        result['records'].extend(page_records)
        result['images_analyzed'] += 1

        seen = set()
        unique_records = []
        for r in result['records']:
            key = (r.student_name_cn, r.university_cn)
            if key not in seen and (r.student_name_cn or r.university_cn):
                seen.add(key)
                unique_records.append(r)

        logger.info(f"去重后剩余 {len(unique_records)} 条记录")
        result['records'] = unique_records
        result['success'] = len(unique_records) > 0

        if not result['success']:
            result['error'] = '未能从图片中提取到有效的录取信息，请检查页面是否包含录取相关内容'

    except Exception as e:
        result['error'] = f'页面访问失败: {str(e)}'
        logger.error(f"提取失败: {e}")

    return result