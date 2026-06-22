import re
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'app'))

# 复制专业提取相关的代码进行测试
PAT_COUNTRY = re.compile(r'(?:美国|英国|加拿大|澳大利亚|澳洲|新加坡|新西兰|香港|日本|韩国|德国|法国|瑞士|荷兰|意大利|西班牙)')
PAT_UNI_KEY = re.compile(r'(?:大学|学院|University|College|School|Institute)')
PAT_MAJOR = re.compile(r'专业')
PAT_OFFER = re.compile(r'(?:offer|OFFER|录取|喜报|捷报|Offer)', re.IGNORECASE)

# 专业关键词列表 - 用于专业提取
MAJOR_KEYWORDS = [
    '计算机科学', '电子工程', '机械工程', '土木工程', '电气工程', '化学工程',
    '软件工程', '人工智能', '数据科学', '信息安全', '网络安全', '机器人',
    '数学', '应用数学', '统计学', '物理', '应用物理', '化学', '生物',
    '生物医学', '医学', '药学', '护理学', '公共卫生', '健康科学',
    '金融', '会计', '经济', '工商管理', '市场营销', '国际商务', '供应链',
    '管理', '企业管理', '金融工程', '商业分析', '金融数学',
    '法律', '法学', '国际法', '知识产权',
    '心理', '社会学', '哲学', '历史', '政治', '国际关系',
    '英语', '比较文学', '东亚研究', '文化研究',
    '艺术', '设计', '建筑', '景观建筑', '城市规划', '音乐', '戏剧',
    '新闻', '传播', '媒体', '广告', '公共关系',
    '环境科学', '地球科学', '海洋科学', '生态学', '气候变化',
    '计算机', '电子信息', '自动化', '通信工程', '信息工程',
    '物理', '化学', '生物', '材料科学', '纳米技术',
    '教育', '教育心理学', '课程与教学', '教育管理',
    '农业', '食品科学', '营养学',
    'CS', 'EECS', 'EE', 'ME', 'BME', 'MS&E', 'OR', 'Finance', 'Economics',
    'Computer Science', 'Electrical Engineering', 'Mechanical Engineering',
    'Biomedical Engineering', 'Data Science', 'Artificial Intelligence',
]

# 专业提取正则模式
PAT_MAJOR_PREFIX = re.compile(r'(?:就读于|录取到|入读|获得|收到|拿下|斩获|喜获)([\u4e00-\u9fa-zA-Z\s]{2,20}?)(?:专业|系|学院)')
PAT_MAJOR_SUFFIX = re.compile(r'([\u4e00-\u9fa-zA-Z\s]{2,20}?)(?:专业|系|学院)(?:录取|入读|就读)')

def _extract_major(text: str) -> str:
    """从文本中提取专业信息"""
    if not text:
        return ""
    
    print(f"DEBUG: 输入文本: {text}")
    
    # 方法1: 尝试前缀匹配模式：录取到XX专业
    m = PAT_MAJOR_PREFIX.search(text)
    if m:
        maj = m.group(1).strip()
        print(f"DEBUG: 方法1匹配到: {maj}")
        if maj and len(maj) >= 2:
            return maj
    
    # 方法2: 尝试后缀匹配模式：XX专业录取
    m = PAT_MAJOR_SUFFIX.search(text)
    if m:
        maj = m.group(1).strip()
        print(f"DEBUG: 方法2匹配到: {maj}")
        if maj and len(maj) >= 2:
            return maj
    
    # 方法3: 尝试关键词匹配
    for kw in MAJOR_KEYWORDS:
        if kw in text:
            print(f"DEBUG: 方法3匹配到关键词: {kw}")
            return kw
    
    # 方法4: 尝试简单的"XX专业"模式
    m = re.search(r'([\u4e00-\u9fa-zA-Z\s]{2,15}?)专业', text)
    if m:
        maj = m.group(1).strip()
        print(f"DEBUG: 方法4匹配到: {maj}")
        if maj and len(maj) >= 2:
            return maj
    
    print(f"DEBUG: 未匹配到任何专业")
    return ""

print("=" * 80)
print("专业提取功能测试")
print("=" * 80)

test_cases = [
    "Jack Yang同学录取到密歇根州立大学计算机科学专业",
    "热烈祝贺Jack Yang收到密歇根州立大学录取通知",
    "金融专业录取",
    "入读电子工程系",
    "获得计算机科学学位",
    "被斯坦福大学CS专业录取",
    "恭喜XX同学获得美国哈佛大学人工智能专业录取",
]

for test in test_cases:
    print(f"\n{'=' * 80}")
    result = _extract_major(test)
    print(f"输入: {test}")
    print(f"提取结果: {'✅ ' + result if result else '❌ 无'}")
