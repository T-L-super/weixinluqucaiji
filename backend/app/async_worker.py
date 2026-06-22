"""
异步任务工作者 — aiohttp + lxml + 任务队列
================================================================
- Redis 任务队列（SQLite 兼容 fallback）
- aiohttp 异步 HTTP 抓取
- lxml 高性能 HTML 解析
- URL 去重
- 连接池复用
"""
import os
import asyncio
import aiohttp
import time
import re
import random
import hashlib
import logging
from datetime import datetime
from lxml import etree
from typing import Any, List, Dict

logger = logging.getLogger('AsyncWorker')

# 导入统一数据库配置
from app.db_config import get_db_connection, exec_sql, DB_TYPE

# ── Redis 兼容接口层 (SQLite fallback) ──────────────────────────
try:
    import redis.asyncio as aioredis
    REDIS_URL = os.environ.get("REDIS_URL", "")
    _redis_pool = None

    async def _get_redis():
        global _redis_pool
        if REDIS_URL and _redis_pool is None:
            _redis_pool = aioredis.from_url(REDIS_URL, decode_responses=True)
        return _redis_pool

    async def queue_push(task_id: int):
        r = await _get_redis()
        if r:
            await r.lpush("task_queue", str(task_id))
            await r.incr("task_queue_pending")

    async def queue_pop():
        r = await _get_redis()
        if r:
            return await r.rpop("task_queue")
        return None

    async def queue_pending_count():
        r = await _get_redis()
        if r:
            v = await r.get("task_queue_pending")
            return int(v) if v else 0
        return 0

    async def queue_decr_pending():
        r = await _get_redis()
        if r:
            await r.decr("task_queue_pending")

    async def url_seen(url: str) -> bool:
        r = await _get_redis()
        if r:
            key = hashlib.md5(url.encode()).hexdigest()
            ok = await r.sadd("seen_urls", key)
            return ok == 0
        return False

    async def queue_health() -> bool:
        r = await _get_redis()
        return r is not None

except Exception:
    aioredis = None

# SQLite 队列 fallback
class _SqliteQueue:
    _init = False

    @classmethod
    def _ensure_table(cls):
        if cls._init:
            return
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS _task_queue (id INTEGER PRIMARY KEY, task_id INTEGER, created_at REAL)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_tq_created ON _task_queue(created_at)")
        c.execute("CREATE TABLE IF NOT EXISTS _seen_urls (url_hash TEXT PRIMARY KEY, created_at REAL)")
        conn.commit()
        conn.close()
        cls._init = True

    @classmethod
    def _conn(cls):
        cls._ensure_table()
        conn = get_db_connection()
        return conn

    @classmethod
    def push(cls, task_id: int):
        conn = cls._conn()
        c = conn.cursor()
        c.execute("INSERT INTO _task_queue (task_id, created_at) VALUES (?, ?)", (task_id, time.time()))
        conn.commit()
        conn.close()

    @classmethod
    def pop(cls):
        conn = cls._conn()
        c = conn.cursor()
        c.execute("SELECT task_id FROM _task_queue ORDER BY created_at ASC LIMIT 1")
        row = c.fetchone()
        if row:
            tid = row[0]
            c.execute("DELETE FROM _task_queue WHERE task_id = ?", (tid,))
            conn.commit()
            conn.close()
            return tid
        conn.close()
        return None

    @classmethod
    def pending_count(cls):
        conn = cls._conn()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM _task_queue")
        v = c.fetchone()[0]
        conn.close()
        return v

    @classmethod
    def url_seen(cls, url: str) -> bool:
        key = hashlib.md5(url.encode()).hexdigest()
        conn = cls._conn()
        c = conn.cursor()
        c.execute("SELECT 1 FROM _seen_urls WHERE url_hash = ?", (key,))
        exists = c.fetchone() is not None
        if not exists:
            c.execute("INSERT INTO _seen_urls (url_hash, created_at) VALUES (?, ?)", (key, time.time()))
            conn.commit()
        conn.close()
        return exists


async def queue_push(task_id: int):
    """推送任务到队列"""
    try:
        if aioredis:
            r = await _get_redis()
            if r:
                await r.lpush("task_queue", str(task_id))
                return
    except Exception:
        pass
    _SqliteQueue.push(task_id)


async def queue_pop():
    """从队列取出任务"""
    try:
        if aioredis:
            r = await _get_redis()
            if r:
                tid = await r.rpop("task_queue")
                return int(tid) if tid else None
    except Exception:
        pass
    return _SqliteQueue.pop()


async def queue_pending_count():
    """队列中待处理数量"""
    try:
        if aioredis:
            r = await _get_redis()
            if r:
                return await r.llen("task_queue")
    except Exception:
        pass
    return _SqliteQueue.pending_count()


async def url_seen(url: str) -> bool:
    """URL 去重 — 返回 True 表示已存在"""
    try:
        if aioredis:
            r = await _get_redis()
            if r:
                key = hashlib.md5(url.encode()).hexdigest()
                ok = await r.sadd("seen_urls", key)
                return ok == 0
    except Exception:
        pass
    return _SqliteQueue.url_seen(url)


async def seed_seen_urls(urls: list):
    """批量种子去重集合"""
    for url in urls:
        await url_seen(url)


# ── 中文姓氏字典（前100常见姓） ──────────────────────────────
_CHINESE_SURNAMES = set("""
赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜
戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳酆鲍史唐
费廉岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅皮下齐康伍余元卜顾孟平黄
和穆萧尹姚邵湛汪祁毛禹狄米贝明臧计伏成戴谈宋茅庞熊纪舒屈项祝董梁
杜阮蓝闵席季麻强贾路娄危江童颜郭梅盛林刁钟徐邱骆高夏蔡田樊胡凌霍
虞万支柯咎管卢莫经房裘缪干解应宗丁宣贲邓郁单杭洪包诸左石崔吉钮龚
程嵇邢滑裴陆荣翁荀羊於惠甄曲家封芮羿储靳汲邴糜松井段富巫乌焦巴弓
牧隗山谷车侯宓蓬全郗班仰秋仲伊宫宁仇栾暴甘钭厉戎祖武符刘景詹束龙
叶幸司韶郜黎蓟薄印宿白怀蒲邰从鄂索咸籍赖卓蔺屠蒙池乔阴郁胥能苍双
闻莘党翟谭贡劳逄姬申扶堵冉宰郦雍却璩桑桂濮牛寿通边扈燕冀郏浦尚农
温别庄晏柴瞿阎充慕连茹习宦艾鱼容向古易慎戈廖庾终暨居衡步都耿满弘
匡国文寇广禄阙东欧殳沃利蔚越夔隆师巩厍聂晁勾敖融冷訾辛阚那简饶空
曾毋沙乜养鞠须丰巢关蒯相查后荆红游竺权逮盍益桓公
""".replace('\n', ''))

def _is_likely_name(s: str) -> bool:
    """判断是否更像中国人名（必须 2-3 字，首字是常见姓）"""
    s = s.strip()
    if len(s) < 2 or len(s) > 3:
        return False
    if not all('\u4e00' <= c <= '\u9fff' for c in s):
        return False
    if s[0] not in _CHINESE_SURNAMES:
        return False
    bad_chars = set('大学生校院系专业级届班录取申报考试学习留出国海内外')
    if any(c in bad_chars for c in s):
        return False
    
    # 新增：排除明显不是人名的词
    invalid_names = [
        '我们', '他们', '你们', '大家', '各位', '同学', '学生', '老师',
        '家长', '朋友', '校友', '嘉宾', '来宾', '观众', '读者', '网友',
        '第一批', '第二批', '第三批', '首批', '本届', '该届', '这届',
        '通过', '进入', '祝贺', '恭喜', '喜报', '捷报', '荣获', '获得',
        '拿到', '收到', '斩获', '拿下', '喜获', '揽获', '顺利', '成功',
        '包括', '涵盖', '涉及', '共有', '新增', '汇总', '顶尖', '世界',
        '全球', '知名', '著名', '多所', '哪些', '什么', '这个', '那个',
    ]
    if s in invalid_names:
        return False
    
    # 检查是否包含明显的非人名字符组合
    invalid_patterns = [
        '通过后方', '后方可', '进入国', '祝贺第', '恭喜第',
        '第一批', '第二批', '第三批', '我们祝', '他们祝',
    ]
    for pattern in invalid_patterns:
        if pattern in s:
            return False
    
    return True


# ── 异步 HTTP 抓取 + lxml 解析 ───────────────────────────────────

UA_MOBILE = (
    "Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36 MicroMessenger/8.0.0"
)
UA_DESKTOP = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
UA_DESKTOP2 = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
)
UA_WECHAT = (
    "Mozilla/5.0 (Linux; Android 12; SM-G9980) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/99.0.4844.88 Mobile Safari/537.36 MicroMessenger/8.0.40.2420"
)
UA_RETRY = [UA_WECHAT, UA_MOBILE, UA_DESKTOP, UA_DESKTOP2]

PAT_COUNTRY = re.compile(r'(?:美国|英国|加拿大|澳大利亚|澳洲|新加坡|新西兰|香港|日本|韩国|德国|法国|瑞士|荷兰|意大利|西班牙)')
PAT_UNI_KEY = re.compile(r'(?:大学|学院|University|College|School|Institute)')
PAT_MAJOR = re.compile(r'专业')
PAT_OFFER = re.compile(r'(?:offer|OFFER|录取|喜报|捷报|Offer)', re.IGNORECASE)
PAT_ANTI_BOT = re.compile(r'(?:环境异常|验证|验证码|请输入验证码)')

# 姓名模式：常见姓 + 1~2字名，后跟"同学"
PAT_NAME_TONGXUE = re.compile(r'(?:^|[,，、\s]|和|与)([\u4e00-\u9fa5]{2,3})同学')
# 字母开头的同学格式：W同学、L同学
PAT_NAME_ALPHA_TONGXUE = re.compile(r'(?:^|[,，、\s])([A-Za-z]{1,2})同学')
# 恭喜XX / 祝贺XX
PAT_NAME_CONGRATS = re.compile(r'(?:恭喜|祝贺|喜报[：:]?)\s*([\u4e00-\u9fa5]{2,3})')
# XX获得/XX收到/XX斩获/XX拿下（前面需要是句首或标点）
PAT_NAME_ACHIEVE = re.compile(r'(?:^|[。！!；;\s,])([\u4e00-\u9fa5]{2,3})(?:获得|收到|斩获|拿下|收获|拿到|荣获|喜获|揽获)')
# X同学获得XX录取 格式 - 简化版本
PAT_STUDENT_ADMISSION = re.compile(r'([A-Za-z]{1}[\u4e00-\u9fa5]?(?:同学)|[\u4e00-\u9fa5]{2,3}(?:同学))[\s，,:：、\-—–]*[\s\S]{0,30}(?:获得|斩获|收到|拿到|荣获)\s*([\u4e00-\u9fa5]+?(?:大学|学院|科大|理工|旅游|镜湖|澳大))')
# 大学名模式 - 非贪婪匹配最近的前缀
PAT_UNI_CN = re.compile(r'([\u4e00-\u9fa5]{2,12}?(?:大学|学院|公学|中学|高中))')
PAT_UNI_EN1 = re.compile(r'((?:[A-Z][a-z]+\s*)+(?:University|College|School|Institute))')
PAT_UNI_EN2 = re.compile(r'([A-Z][a-zA-Z\s]+(?:School|College|University|Institute))')
PAT_UNI_LONG = re.compile(r'([\u4e00-\u9fa5]{4,15}(?:大学|学院|学校|公学))')
PAT_UNI_SHORT = re.compile(r'(牛津大学|牛津|剑桥大学|剑桥|哈佛大学|哈佛|耶鲁大学|耶鲁|斯坦福大学|斯坦福|麻省理工学院|麻省|普林斯顿大学|普林斯顿|哥伦比亚大学|哥伦比亚|宾夕法尼亚大学|宾夕法尼亚|康奈尔大学|康奈尔|杜克大学|杜克|布朗大学|布朗|达特茅斯学院|达特茅斯|芝加哥大学|芝加哥|加州大学伯克利分校|加州伯克利|加州大学洛杉矶分校|加州洛杉矶|加州理工学院|加州理工|加州大学圣地亚哥分校|加州圣地亚哥|加州大学戴维斯分校|加州戴维斯|加州大学圣巴巴拉分校|加州圣巴巴拉|加州大学欧文分校|加州欧文|密歇根大学|密歇根|西北大学|约翰霍普金斯大学|约翰霍普金斯|宾夕法尼亚州立大学|宾夕法尼亚州立|德克萨斯大学奥斯汀分校|德州奥斯汀|威斯康星大学|威斯康星|伊利诺伊大学|伊利诺伊|普渡大学|普渡|佐治亚理工学院|佐治亚理工|北卡罗来纳大学教堂山分校|北卡教堂山|弗吉尼亚大学|弗吉尼亚|卡内基梅隆大学|卡内基梅隆|莱斯大学|莱斯|埃默里大学|埃默里|范德堡大学|范德堡|华盛顿大学|波士顿大学|波士顿学院|东北大学|乔治城大学|乔治城|塔夫茨大学|塔夫茨|布兰迪斯大学|布兰迪斯|凯莱商学院|凯莱|凯洛格商学院|凯洛格|沃顿商学院|沃顿|布斯商学院|布斯|哈斯商学院|哈斯|斯特恩商学院|斯特恩|纽约大学|纽大|帝国理工学院|帝国理工|伦敦政治经济学院|伦敦政经|伦敦大学学院|多伦多大学|多伦多|麦吉尔大学|麦吉尔|滑铁卢大学|滑铁卢|UBC|UCL|MIT|NYU|CMU|UCLA|USC|LSE|KCL|Edinburgh|Manchester|Warwick|ANU|悉尼大学|墨尔本大学|昆士兰大学|莫纳什大学|新南威尔士大学|香港大学|港大|香港中文大学|港中文|香港科技大学|港科大|南洋理工大学|南洋理工|新加坡国立大学|新加坡国立|澳门大学|澳门科技大学|澳门理工大学|澳门城市大学|澳门旅游大学|澳门镜湖护理学院)')
PAT_YEAR = re.compile(r'(?:20\d{2})\s*(?:年|届|级|入学|录取|申请)')
PAT_SCHOLARSHIP = re.compile(r'(?:奖学金|奖金)\s*[:：]?\s*\$?([\d,]+(?:\.[\d]+)?)\s*(?:万)?\s*(?:美元|美金|英镑|欧元|澳元|加元|人民币|元|USD|GBP|EUR|AUD|CAD|CNY)?')

# ── 国外大学库 ───────────────────────────────────────────────
FOREIGN_UNIVERSITIES = [
    # 美国大学
    '哈佛大学', '耶鲁大学', '普林斯顿大学', '斯坦福大学', '麻省理工学院',
    '芝加哥大学', '宾夕法尼亚大学', '康奈尔大学', '杜克大学', '布朗大学',
    '达特茅斯学院', '哥伦比亚大学', '西北大学', '约翰霍普金斯大学', '加州大学伯克利分校',
    '加州大学洛杉矶分校', '加州理工学院', '加州大学圣地亚哥分校', '加州大学戴维斯分校',
    '加州大学圣巴巴拉分校', '加州大学欧文分校', '加州大学尔湾分校', '加州大学河滨分校',
    '加州大学圣克鲁兹分校', '密歇根大学', '密歇根州立大学', '伊利诺伊大学厄巴纳-香槟分校',
    '普渡大学', '佐治亚理工学院', '北卡罗来纳大学教堂山分校', '弗吉尼亚大学',
    '卡内基梅隆大学', '莱斯大学', '埃默里大学', '范德堡大学', '华盛顿大学',
    '华盛顿大学圣路易斯分校', '华盛顿大学西雅图分校', '波士顿大学', '波士顿学院',
    '东北大学', '乔治城大学', '塔夫茨大学', '布兰迪斯大学', '纽约大学',
    '宾夕法尼亚州立大学', '德克萨斯大学奥斯汀分校', '德克萨斯大学达拉斯分校',
    '德克萨斯A&M大学', '威斯康星大学麦迪逊分校', '威斯康星大学密尔沃基分校',
    '威斯康星大学拉克罗斯分校', '马里兰大学', '马里兰大学帕克分校', '罗格斯大学',
    '明尼苏达大学', '俄亥俄州立大学', '印第安纳大学', '印第安纳大学伯明顿分校',
    '密歇根大学安娜堡分校', '亚利桑那大学', '亚利桑那州立大学', '科罗拉多大学',
    '科罗拉多大学博尔德分校', '科罗拉多州立大学', '新罕布什尔大学',
    '新泽西州立大学', '弗吉尼亚联邦大学', '马萨诸塞大学', '马萨诸塞大学阿默斯特分校',
    '加州大学默塞德分校', '迈阿密大学', '迈阿密大学牛津分校',
    # 美国商学院
    '凯莱商学院', '凯洛格商学院', '沃顿商学院', '布斯商学院', '哈斯商学院',
    '史登商学院', '哥伦比亚商学院', 'MIT斯隆管理学院', '耶鲁管理学院',
    # 英国大学
    '牛津大学', '剑桥大学', '帝国理工学院', '伦敦政治经济学院', '伦敦大学学院',
    '伦敦国王学院', '曼彻斯特大学', '爱丁堡大学', '布里斯托大学',
    '华威大学', '格拉斯哥大学', '杜伦大学', '圣安德鲁斯大学', '诺丁汉大学',
    '谢菲尔德大学', '伯明翰大学', '利兹大学', '利物浦大学', '南安普顿大学',
    # 加拿大大学
    '多伦多大学', '麦吉尔大学', '不列颠哥伦比亚大学', '阿尔伯塔大学',
    '麦克马斯特大学', '滑铁卢大学', '西安大略大学', '西蒙菲莎大学',
    '女王大学', '渥太华大学', '卡尔顿大学', '约克大学',
    # 澳大利亚大学
    '悉尼大学', '墨尔本大学', '昆士兰大学', '莫纳什大学', '新南威尔士大学',
    '西澳大利亚大学', '阿德莱德大学', '麦考瑞大学', '墨尔本皇家墨尔本大学',
    '南澳大学', '迪肯大学', '科廷大学',
    # 新加坡大学
    '新加坡国立大学', '南洋理工大学', '新加坡管理大学',
    # 香港大学
    '香港大学', '香港中文大学', '香港科技大学', '香港城市大学',
    '香港理工大学', '香港浸会大学', '香港岭南大学', '香港教育大学',
    # 其他国家大学
    '东京大学', '京都大学', '大阪大学', '首尔大学', '韩国科学技术院',
    '苏黎世联邦理工学院', '洛桑联邦理工学院',
    # CWUR 补充 - 美国
    '加州大学旧金山分校', '德州大学奥斯汀分校', '佛罗里达州立大学', '乔治亚理工学院',
    '明尼苏达大学双城分校', '匹兹堡大学', '南加州大学', '德州A&M大学',
    '爱荷华大学', '雪城大学', '特拉华大学', '纽约州立大学石溪分校', '纽约州立大学布法罗分校',
    '俄勒冈大学', '内布拉斯加大学林肯分校', '堪萨斯大学', '犹他大学', '南卡罗来纳大学',
    '路易斯安那州立大学', '田纳西大学', '密苏里大学', '奥本大学', '康涅狄格大学',
    '马萨诸塞大学波士顿分校', '韦恩州立大学', '休斯顿大学', '辛辛那提大学', '北德克萨斯大学',
    '密西西比大学', '路易斯维尔大学', '南佛罗里达大学', '德雷塞尔大学', '克拉克大学',
    '贝勒大学', '杨百翰大学', '乔治华盛顿大学', '美利坚大学', '纽约理工学院',
    '罗切斯特理工学院', '伊利诺伊理工学院', '新泽西理工学院', '加州州立大学',
    '纽约州立大学', '宾夕法尼亚西部大学', '德克萨斯理工大学',
    # CWUR 补充 - 加拿大
    '蒙特利尔大学', '英属哥伦比亚大学', 'UBC', '女王大学', '约克大学',
    # CWUR 补充 - 澳大利亚
    '澳大利亚国立大学', '昆士兰科技大学', '悉尼科技大学', '皇家墨尔本理工大学',
    # CWUR 补充 - 德国
    '慕尼黑大学', '海德堡大学', '慕尼黑工业大学', '柏林洪堡大学', '波恩大学',
    '图宾根大学', '弗莱堡大学', '哥廷根大学', '科隆大学', '柏林自由大学',
    '多特蒙德工业大学', '德累斯顿工业大学', '斯图加特大学', '汉诺威大学', '达姆施塔特工业大学',
    # CWUR 补充 - 法国
    '巴黎第六大学', '巴黎第十一大学', '巴黎综合理工学院', '巴黎第四大学', '里昂第一大学',
    # CWUR 补充 - 瑞士
    '苏黎世大学', '日内瓦大学',
    # CWUR 补充 - 日本
    '名古屋大学', '九州大学', '北海道大学', '东京工业大学', '大阪市立大学',
    '神户大学', '筑波大学', '广岛大学', '九州工业大学', '东京医科齿科大学',
    # CWUR 补充 - 韩国
    '高丽大学', '延世大学', '成均馆大学', '梨花女子大学', '西江大学', '中央大学', '庆熙大学',
    # CWUR 补充 - 荷兰
    '乌得勒支大学', '阿姆斯特丹大学', '莱顿大学', '格罗宁根大学', '鹿特丹伊拉斯姆斯大学',
    # CWUR 补充 - 英国
    '莱斯特大学', '纽卡斯尔大学', '萨塞克斯大学', '埃克塞特大学', '贝尔法斯特女王大学',
    '巴斯大学', '东安格利亚大学', '阿伯丁大学', '斯特拉斯克莱德大学', '赫尔大学',
    '曼彻斯特城市大学', '伯明翰城市大学', '考文垂大学', '普利茅斯大学', '索尔福德大学',
    # CWUR 补充 - 比利时
    '鲁汶大学', '根特大学',
    # CWUR 补充 - 北欧
    '乌普萨拉大学', '隆德大学', '斯德哥尔摩大学', '南丹麦大学', '奥尔堡大学',
    '哥本哈根商学院', '奥斯陆大学', '卑尔根大学', '冰岛大学',
    # CWUR 补充 - 爱尔兰
    '都柏林大学', '科克大学', '高威大学',
    # CWUR 补充 - 意大利
    '帕多瓦大学', '博洛尼亚大学', '罗马大学', '米兰大学', '都灵大学',
    # CWUR 补充 - 西班牙
    '马德里自治大学', '巴塞罗那大学', '格拉纳达大学', '塞维利亚大学', '瓦伦西亚大学',
    # CWUR 补充 - 亚洲
    '台湾大学', '台湾清华大学', '台湾交通大学', '成功大学', '中山大学', '中正大学',
    '印度理工学院',
    # CWUR 补充 - 中国大陆
    '清华大学', '北京大学', '复旦大学', '上海交通大学', '浙江大学', '南京大学', '中国科学技术大学',
]

_aiohttp_session: aiohttp.ClientSession = None
_session_lock = None

def _get_text(elem) -> str:
    """安全获取元素文本，优先用 itertext (lxml 全版本兼容)"""
    if elem is None:
        return ""
    try:
        return "".join(elem.itertext()).strip()
    except (AttributeError, TypeError):
        try:
            return elem.text_content().strip()
        except (AttributeError, TypeError):
            return str(elem).strip()


def _get_session_lock():
    global _session_lock
    if _session_lock is None:
        _session_lock = asyncio.Lock()
    return _session_lock


async def _get_session():
    global _aiohttp_session
    async with _get_session_lock():
        try:
            loop = asyncio.get_running_loop()
            if _aiohttp_session is not None and not _aiohttp_session.closed:
                if getattr(_aiohttp_session, '_loop', None) is loop:
                    return _aiohttp_session
                await _aiohttp_session.close()
                _aiohttp_session = None
        except RuntimeError:
            pass
        if _aiohttp_session is None or _aiohttp_session.closed:
            timeout = aiohttp.ClientTimeout(total=25, connect=8, sock_read=20)
            _aiohttp_session = aiohttp.ClientSession(
                timeout=timeout,
                connector=aiohttp.TCPConnector(
                    limit=30,
                    limit_per_host=10,
                    ttl_dns_cache=300,
                    force_close=False,
                ),
            )
            _aiohttp_session._loop = asyncio.get_running_loop()
        return _aiohttp_session


async def cleanup_session():
    global _aiohttp_session
    if _aiohttp_session and not _aiohttp_session.closed:
        await _aiohttp_session.close()
        _aiohttp_session = None


async def _fetch_html(url: str) -> str:
    """抓取 HTML — 独立 session，避免跨 event loop 问题"""
    timeout = aiohttp.ClientTimeout(total=25, connect=8, sock_read=20)
    connector = aiohttp.TCPConnector(limit=1, force_close=True)
    html = None
    last_err = None
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        for i, ua in enumerate(UA_RETRY):
            try:
                if i > 0:
                    await asyncio.sleep(i * 1.5)
                headers = {"User-Agent": ua, "Accept": "text/html,application/xhtml+xml,*/*"}
                async with session.get(url, headers=headers, allow_redirects=True) as resp:
                    resp.raise_for_status()
                    html = await resp.text()
                    if PAT_ANTI_BOT.search(html or ""):
                        raise ValueError("anti_bot detected")
                    return html
            except Exception as e:
                last_err = e
                continue
    if html:
        return html
    raise last_err or RuntimeError("fetch failed")



def _parse_html(html: str) -> etree._Element:
    html = html.replace('\x00', '')
    return etree.HTML(html)


def _extract_title(tree) -> str:
    meta = tree.xpath('//meta[@property="og:title"]/@content')
    if meta:
        return meta[0].strip()
    title = tree.xpath('//*[@id="activity-name"]/text()')
    if title:
        return title[0].strip()
    t = tree.xpath('//title/text()')
    if t:
        return t[0].strip()
    return ""


def _extract_school(tree) -> str:
    meta = tree.xpath('//meta[@property="og:nickname"]/@content')
    if meta:
        return meta[0].strip()
    spans = tree.xpath('//span[contains(@class,"rich_media_meta_nickname")]/text()')
    return spans[0].strip() if spans else ""


def _extract_records(tree, school: str, url: str, title: str) -> list:
    """提取录取记录 — 表格优先 + section 解析 + 文本回退 + 姓名验证"""
    records = []
    seen_names = set()
    seen_students = set()  # 用于去重：只记录学生名字，不考虑大学

    # ── 策略1: 表格提取 ──
    for table in tree.xpath('//table'):
        rows = table.xpath('.//tr')
        if len(rows) <= 1:
            continue
        for tr in rows[1:]:
            cells = [_get_text(c) for c in tr.xpath('.//td')]
            if len(cells) < 2:
                continue
            sname, uni, maj, country = "", "", "", ""
            all_text = " ".join(cells)
            for val in cells:
                if not sname and _is_likely_name(val):
                    sname = val
                if PAT_UNI_KEY.search(val):
                    uni = val
            if not uni:
                uni = _find_university(all_text)
            if PAT_MAJOR.search(all_text):
                m = PAT_MAJOR.search(all_text)
                maj = m.group().replace("专业", "").strip()
            m = PAT_COUNTRY.search(all_text)
            if m:
                country = m.group()
            if sname and uni:
                # 统一名字格式，去除"同学"后缀
                sname_clean = sname.replace('同学', '')
                uni_clean = uni.replace('美国', '').replace('英国', '').replace('加拿大', '').replace('澳大利亚', '').replace('新加坡', '').replace('中国', '').strip()
                
                # 首先检查学生是否已经被记录过（去重）
                if sname_clean in seen_students:
                    continue
                seen_students.add(sname_clean)
                
                key = f"{sname_clean}|{uni_clean}"
                if key not in seen_names:
                    seen_names.add(key)
                    records.append((sname, uni, maj, country, school or "未知", url, title))

    # ── 策略2: Section 解析（微信文章的结构单元） ──
    if not records:
        for section in tree.xpath('//section'):
            text = _get_text(section)
            if len(text) < 10:
                continue
            
            sentences = re.split(r'[。！!；;\n]', text)
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) < 10:
                    continue
                
                has_offer = PAT_OFFER.search(sentence)
                if not has_offer:
                    continue
                
                # 在句子内找所有同学名字和位置
                students = []
                
                # 模式1: "XX、YY等N名同学" 格式
                group_pattern = re.compile(r'([\u4e00-\u9fa5]{2,3}(?:、[\u4e00-\u9fa5]{2,3})+)等\d+名同学')
                for match in group_pattern.finditer(sentence):
                    names_str = match.group(1)
                    names = names_str.split('、')
                    for name in names:
                        sname = name + '同学'
                        if sname in ['于各位同学', '各位同学']:
                            continue
                        students.append((match.start() + names_str.find(name), sname))
                
                # 模式2: "XX同学" 格式
                if not students:
                    single_pattern = re.compile(r'([\u4e00-\u9fa5]{2,3})同学')
                    for match in single_pattern.finditer(sentence):
                        sname = match.group(1) + '同学'
                        if sname in ['于各位同学', '各位同学']:
                            continue
                        students.append((match.start(), sname))
                
                if not students:
                    continue
                
                # 在句子中找到所有大学和位置
                unis_in_sentence = []
                for uni in FOREIGN_UNIVERSITIES:
                    if uni in sentence:
                        pos = 0
                        while True:
                            pos = sentence.find(uni, pos)
                            if pos == -1:
                                break
                            unis_in_sentence.append((pos, uni))
                            pos += len(uni)
                unis_in_sentence.sort(key=lambda x: x[0])
                
                if not unis_in_sentence:
                    # 如果国外大学库没找到，用原有方法
                    for pos, sname in students:
                        if not sname or len(sname) < 2:
                            continue
                        uni = _find_university(sentence)
                        if uni:
                            uni_clean = uni.replace('美国', '').replace('英国', '').replace('加拿大', '').replace('澳大利亚', '').replace('新加坡', '').replace('中国', '').strip()
                            sname_clean = sname.replace('同学', '')
                            key = f"{sname_clean}|{uni_clean}"
                            if key not in seen_names:
                                seen_names.add(key)
                                country = ""
                                m = PAT_COUNTRY.search(sentence)
                                if m:
                                    country = m.group()
                                records.append((sname, uni, "", country, school or "未知", url, title))
                    continue
                
                # 对于每个同学，找到离他最近的大学
                for student_pos, sname in students:
                    if not sname or len(sname) < 2:
                        continue
                    
                    best_uni = None
                    best_distance = float('inf')
                    best_uni_pos = -1
                    
                    for uni_pos, uni in unis_in_sentence:
                        if uni_pos > student_pos:
                            distance = uni_pos - student_pos
                        else:
                            distance = (student_pos - uni_pos) * 2
                        
                        # 优先选择距离更近的大学；距离相同时优先选择位置更靠后的大学
                        if distance < best_distance or (distance == best_distance and uni_pos > best_uni_pos):
                            best_distance = distance
                            best_uni = uni
                            best_uni_pos = uni_pos
                    
                    if best_uni:
                        uni_clean = best_uni.replace('美国', '').replace('英国', '').replace('加拿大', '').replace('澳大利亚', '').replace('新加坡', '').replace('中国', '').strip()
                        sname_clean = sname.replace('同学', '')
                        
                        # 首先检查学生是否已经被记录过（去重）
                        if sname_clean in seen_students:
                            continue
                        seen_students.add(sname_clean)
                        
                        key = f"{sname_clean}|{uni_clean}"
                        if key not in seen_names:
                            seen_names.add(key)
                            country = ""
                            m = PAT_COUNTRY.search(sentence)
                            if m:
                                country = m.group()
                            records.append((sname, best_uni, "", country, school or "未知", url, title))
                
                if len(records) >= 30:
                    break
            
            if len(records) >= 30:
                break

    # ── 策略3: "X同学获得XX录取" 格式提取 ──
    text = " ".join(tree.xpath('//text()'))
    
    # 先按句子分割文本，分别处理每个句子
    sentences = re.split(r'[。！!；;\n]', text)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 10:
            continue
        
        # 在句子内找所有同学名字和位置
        students = []
        
        # 模式1: "XX、YY等N名同学" 格式（支持中文和字母姓名）
        group_pattern = re.compile(r'((?:[\u4e00-\u9fa5]{2,3}|[A-Za-z]{1,2})(?:、(?:[\u4e00-\u9fa5]{2,3}|[A-Za-z]{1,2}))+)等\d+名同学')
        for match in group_pattern.finditer(sentence):
            names_str = match.group(1)
            names = names_str.split('、')
            for name in names:
                sname = name + '同学'
                if sname in ['于各位同学', '各位同学']:
                    continue
                students.append((match.start() + names_str.find(name), sname))
        
        # 模式2: "XX同学" 格式（支持中文和字母姓名）
        if not students:
            single_pattern = re.compile(r'((?:[\u4e00-\u9fa5]{2,3}|[A-Za-z]{1,2}))同学')
            for match in single_pattern.finditer(sentence):
                sname = match.group(1) + '同学'
                if sname in ['于各位同学', '各位同学']:
                    continue
                students.append((match.start(), sname))
        
        if not students:
            continue
        
        # 在句子中找到所有大学和位置
        unis_in_sentence = []
        for uni in FOREIGN_UNIVERSITIES:
            if uni in sentence:
                # 找到这个大学在句子中的所有出现位置
                pos = 0
                while True:
                    pos = sentence.find(uni, pos)
                    if pos == -1:
                        break
                    unis_in_sentence.append((pos, uni))
                    pos += len(uni)
        # 按位置排序
        unis_in_sentence.sort(key=lambda x: x[0])
        
        if not unis_in_sentence:
            # 如果国外大学库没找到，用原有方法
            for pos, sname in students:
                if not sname or len(sname) < 2:
                    continue
                uni = _find_university(sentence)
                if uni:
                    uni_clean = uni.replace('美国', '').replace('英国', '').replace('加拿大', '').replace('澳大利亚', '').replace('新加坡', '').replace('中国', '').strip()
                    sname_clean = sname.replace('同学', '')
                    key = f"{sname_clean}|{uni_clean}"
                    if key not in seen_names:
                        seen_names.add(key)
                        country = ''
                        if '澳门' in uni:
                            country = '中国澳门'
                        elif '多伦多' in uni or '加拿大' in uni or 'UBC' in uni or 'McGill' in uni:
                            country = '加拿大'
                        elif '伦敦' in uni or '帝国' in uni or '英国' in uni:
                            country = '英国'
                        elif any(kw in uni for kw in ['加州', '斯坦福', '麻省', '哈佛', '耶鲁', '普林斯顿', '哥伦比亚', '芝加哥', '宾夕法尼亚', '西北', '约翰霍普金斯', '密歇根', '威斯康星', '伊利诺伊', '普渡', '佐治亚', '北卡', '弗吉尼亚', '卡内基梅隆', '莱斯', '埃默里', '范德堡', '波士顿', '东北', '乔治城', '塔夫茨', '布兰迪斯', '凯莱', '沃顿', '布斯', '哈斯', '斯特恩', '纽约']):
                            country = '美国'
                        records.append((sname, uni, "", country, school or "未知", url, title))
                        logger.info(f"提取到: {sname} - {uni}")
            continue
        
        # 对于每个同学，找到离他最近的大学
        for student_pos, sname in students:
            if not sname or len(sname) < 2:
                continue
            
            # 找离同学位置最近的大学
            best_uni = None
            best_distance = float('inf')
            best_uni_pos = -1
            
            for uni_pos, uni in unis_in_sentence:
                # 计算距离（优先找同学后面的大学，因为通常句式是"XX同学被YY录取"
                if uni_pos > student_pos:
                    distance = uni_pos - student_pos
                else:
                    distance = (student_pos - uni_pos) * 2  # 前面的大学距离翻倍，降低优先级
                
                # 优先选择距离更近的大学；距离相同时优先选择位置更靠后的大学
                if distance < best_distance or (distance == best_distance and uni_pos > best_uni_pos):
                    best_distance = distance
                    best_uni = uni
                    best_uni_pos = uni_pos
            
            if best_uni:
                uni_clean = best_uni.replace('美国', '').replace('英国', '').replace('加拿大', '').replace('澳大利亚', '').replace('新加坡', '').replace('中国', '').strip()
                sname_clean = sname.replace('同学', '')
                
                # 首先检查学生是否已经被记录过（去重）
                if sname_clean in seen_students:
                    continue
                seen_students.add(sname_clean)
                
                key = f"{sname_clean}|{uni_clean}"
                if key not in seen_names:
                    seen_names.add(key)
                    country = ''
                    if '澳门' in best_uni:
                        country = '中国澳门'
                    elif '多伦多' in best_uni or '加拿大' in best_uni or 'UBC' in best_uni or 'McGill' in best_uni or '英属哥伦比亚' in best_uni:
                        country = '加拿大'
                    elif '伦敦' in best_uni or '帝国' in best_uni or '英国' in best_uni:
                        country = '英国'
                    elif any(kw in best_uni for kw in ['加州', '斯坦福', '麻省', '哈佛', '耶鲁', '普林斯顿', '哥伦比亚', '芝加哥', '宾夕法尼亚', '西北', '约翰霍普金斯', '密歇根', '威斯康星', '伊利诺伊', '普渡', '佐治亚', '北卡', '弗吉尼亚', '卡内基梅隆', '莱斯', '埃默里', '范德堡', '波士顿', '东北', '乔治城', '塔夫茨', '布兰迪斯', '凯莱', '沃顿', '布斯', '哈斯', '斯特恩', '纽约']):
                        country = '美国'
                    records.append((sname, best_uni, "", country, school or "未知", url, title))
                    logger.info(f"提取到: {sname} - {best_uni}")

    # ── 策略4: 全文文本回退 ──
    if not records:
        sentences = re.split(r'[。！!；;\n]', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
            if not PAT_OFFER.search(sentence):
                continue
            sname = _extract_name_from_text(sentence)
            uni = _find_university(sentence)
            if not uni:
                continue
            country = ""
            m = PAT_COUNTRY.search(sentence)
            if m:
                country = m.group()
            if not sname:
                sname = ""
            elif sname in seen_names:
                continue
            if sname:
                seen_names.add(sname)
            records.append((sname, uni, "", country, school or "未知", url, title))
            if len(records) >= 20:
                break

    return records


def _extract_name_from_text(text: str) -> str:
    """从文本中提取最可能的学生名"""
    for pat in [PAT_NAME_CONGRATS, PAT_NAME_TONGXUE, PAT_NAME_ACHIEVE]:
        m = pat.search(text)
        if m:
            candidate = m.group(1).strip()
            if _is_likely_name(candidate):
                return candidate
    m = PAT_NAME_ALPHA_TONGXUE.search(text)
    if m:
        return m.group(1).strip() + "同学"
    
    # 额外检查：直接匹配"恭喜J同学"格式（不带标点分隔）
    m = re.search(r'恭喜([A-Za-z]{1,2})同学', text)
    if m:
        return m.group(1).strip() + "同学"
    
    return ""


UNIVERSITY_ABBREVIATIONS = {
    '澳大': '澳门大学',
    '澳科大': '澳门科技大学',
    '澳门科大': '澳门科技大学',
    '澳门理工': '澳门理工大学',
    '澳门城市': '澳门城市大学',
    '澳门旅游': '澳门旅游大学',
    '澳门镜湖': '澳门镜湖护理学院',
    
    '加州伯克利': '加州大学伯克利分校',
    '加州洛杉矶': '加州大学洛杉矶分校',
    '加州理工': '加州理工学院',
    '加州圣地亚哥': '加州大学圣地亚哥分校',
    '加州戴维斯': '加州大学戴维斯分校',
    '加州圣巴巴拉': '加州大学圣巴巴拉分校',
    '加州欧文': '加州大学欧文分校',
    '密歇根': '密歇根大学',
    '西北大学': '西北大学',
    '约翰霍普金斯': '约翰霍普金斯大学',
    '宾夕法尼亚州立': '宾夕法尼亚州立大学',
    '德州奥斯汀': '德克萨斯大学奥斯汀分校',
    '威斯康星': '威斯康星大学麦迪逊分校',
    '伊利诺伊': '伊利诺伊大学厄巴纳-香槟分校',
    '普渡': '普渡大学',
    '佐治亚理工': '佐治亚理工学院',
    '北卡教堂山': '北卡罗来纳大学教堂山分校',
    '弗吉尼亚': '弗吉尼亚大学',
    '卡内基梅隆': '卡内基梅隆大学',
    '莱斯': '莱斯大学',
    '埃默里': '埃默里大学',
    '范德堡': '范德堡大学',
    '华盛顿大学': '华盛顿大学',
    '波士顿大学': '波士顿大学',
    '波士顿学院': '波士顿学院',
    '东北大学': '东北大学',
    '乔治城': '乔治城大学',
    '塔夫茨': '塔夫茨大学',
    '布兰迪斯': '布兰迪斯大学',
    '凯莱': '凯莱商学院',
    '凯洛格': '凯洛格商学院',
    '沃顿': '沃顿商学院',
    '布斯': '布斯商学院',
    '哈斯': '哈斯商学院',
    '斯特恩': '斯特恩商学院',
    '纽大': '纽约大学',
}

def _is_valid_university_name(uni: str) -> bool:
    """验证大学名称是否合理"""
    if not uni or len(uni) < 2:
        return False
    
    # 长度检查：大学名称通常在2-15个中文字符之间
    chinese_chars = [c for c in uni if '\u4e00' <= c <= '\u9fff']
    if len(chinese_chars) > 15:
        return False
    
    # 黑名单：包含这些词的绝对不是大学名
    invalid_keywords = [
        '通过后方可', '祝贺', '第一批', '我们', '他们', '你们',
        '进入', '方可', '绩', '成绩', '录取率', '申请', '包括',
        '涵盖', '涉及', '共有', '新增', '汇总', '顶尖', '世界',
        '全球', '知名', '著名', '多所', '哪些', '学生', '老师',
        '家长', '家长', '朋友', '同学', '校友', '恭喜', '喜报',
        '捷报', '荣获', '顺利', '成功', '获得', '拿到', '收到',
        '斩获', '拿下', '喜获', '揽获',
    ]
    for keyword in invalid_keywords:
        if keyword in uni:
            return False
    
    # 如果包含动词前缀，很可能是叙述文字而非大学名
    verb_prefixes = ['通过', '进入', '获得', '拿到', '收到', '斩获', '恭喜', '祝贺', '我们', '他们']
    for prefix in verb_prefixes:
        if uni.startswith(prefix):
            return False
    
    # 必须包含大学标识词（大学、学院、公学等）或是已知缩写
    valid_suffixes = ['大学', '学院', '公学', '中学', '高中', '理工', '科大']
    known_abbreviations = ['MIT', 'UCL', 'CMU', 'NYU', 'UCLA', 'USC', 'LSE', 'KCL', 'ANU', 'UBC', 'UIUC', 'BU', 'BC', 'UW', 'UMich', 'UCSD', 'UCSB', 'UCD', 'UCI']
    
    has_valid_suffix = any(suffix in uni for suffix in valid_suffixes)
    is_known_abbr = any(abbr in uni for abbr in known_abbreviations)
    
    if not has_valid_suffix and not is_known_abbr:
        return False
    
    return True


def _find_university(text: str) -> str:
    """从文本中找到最可能的大学名 - 优先匹配国外大学库"""
    offer_related = ['录取', 'offer', 'OFFER', '喜报', '捷报', '收到', '获得', '斩获', '拿下', '拿到', '荣获', '喜获', '揽获']
    
    # 策略1: 在录取关键词附近优先匹配国外大学库
    for keyword in offer_related:
        idx = text.find(keyword)
        if idx != -1:
            context = text[max(0, idx - 100):idx + 200]
            # 优先匹配完整大学名称（按长度降序，优先匹配较长名称）
            found_unis = []
            for uni in FOREIGN_UNIVERSITIES:
                if uni in context:
                    found_unis.append(uni)
            if found_unis:
                # 优先选择较长的大学名称（更准确）
                found_unis.sort(key=lambda x: -len(x))
                return found_unis[0]
    
    # 策略2: 匹配整个文本中的国外大学库
    found_unis = []
    for uni in FOREIGN_UNIVERSITIES:
        if uni in text:
            found_unis.append(uni)
    if found_unis:
        # 优先匹配较长名称
        found_unis.sort(key=lambda x: -len(x))
        return found_unis[0]
    
    # 策略3: 原有的 PAT_UNI_SHORT 匹配
    m = PAT_UNI_SHORT.search(text)
    if m:
        short_name = m.group()
        return UNIVERSITY_ABBREVIATIONS.get(short_name, short_name)
    
    # 策略4: 原有的大学/学院关键词匹配（增加验证）
    for keyword in offer_related:
        idx = text.find(keyword)
        if idx != -1:
            context = text[max(0, idx - 100):idx + 200]
            for kw in ['大学', '学院']:
                pos = context.rfind(kw)
                if pos >= 0:
                    start = max(0, pos - 12)
                    prefix = context[start:pos]
                    prefix_ch = ''.join(c for c in prefix if '\u4e00' <= c <= '\u9fff')
                    if 2 <= len(prefix_ch) <= 12:
                        uni = prefix_ch + kw
                        # 新增：验证大学名称合理性
                        if not _is_valid_university_name(uni):
                            continue
                        bad_start = {'到','的','了','是','有','为','被','让','把','给','也','就','都','还','要','会','能','可','应','该','想','说','看','叫','进','出','来','去','做','拿','收','获','得','取','找','选','集','汇','申','请','录取','收获','拿到','收到','获得','喜获','揽获','斩获','拿下','荣获','顺利','成功','包括','涵盖','涉及','共有','新增','汇总','顶尖','美国','英国','世界','全球','知名','著名','多所','哪些','哪些大','录取率','录取率低','中国学生','华威中国','学生录取'}
                        if uni[:1] not in bad_start and uni[:2] not in bad_start and uni[:3] not in bad_start:
                            return uni
    
    for kw in ['大学', '学院']:
        pos = text.rfind(kw)
        if pos >= 0:
            start = max(0, pos - 12)
            prefix = text[start:pos]
            prefix_ch = ''.join(c for c in prefix if '\u4e00' <= c <= '\u9fff')
            if 2 <= len(prefix_ch) <= 12:
                uni = prefix_ch + kw
                # 新增：验证大学名称合理性
                if not _is_valid_university_name(uni):
                    continue
                bad_start = {'到','的','了','是','有','为','被','让','把','给','也','就','都','还','要','会','能','可','应','该','想','说','看','叫','进','出','来','去','做','拿','收','获','得','取','找','选','集','汇','申','请','录取','收获','拿到','收到','获得','喜获','揽获','斩获','拿下','荣获','顺利','成功','包括','涵盖','涉及','共有','新增','汇总','顶尖','美国','英国','世界','全球','知名','著名','多所','哪些','哪些大','录取率','录取率低','中国学生','华威中国','学生录取'}
                if uni[:1] not in bad_start and uni[:2] not in bad_start and uni[:3] not in bad_start:
                    return uni
    
    m = PAT_UNI_EN1.search(text)
    if m:
        uni = m.group(1).strip()
        if 5 <= len(uni) <= 40:
            return uni
    m = PAT_UNI_EN2.search(text)
    if m:
        uni = m.group(1).strip()
        if 5 <= len(uni) <= 40:
            return uni
    
    short_uni = re.search(r'\b(?:UCL|MIT|CMU|NYU|UCLA|USC|LSE|KCL|ANU|UBC|UIUC|BU|BC|UW|UMich|UCSD|UCSB|UCD|UCI)\b', text)
    if short_uni:
        return short_uni.group()
    return ""


def _clean_university_name(uni: str) -> str:
    """清理大学名称中的多余文字"""
    if not uni:
        return uni
    
    cleaned = uni
    
    patterns_to_remove = [
        r'^\d+号\s*',
        r'^\d+、\s*',
        r'^\d+\s*',
        r'^[、，,，.。！!]+',
    ]
    
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, '', cleaned).strip()
    
    uni_keywords = [
        '澳门大学', '澳门科技大学', '澳门理工大学', '澳门旅游大学', '澳门城市大学',
        '香港大学', '香港中文大学', '香港科技大学', '香港城市大学', '香港理工大学', '香港浸会大学',
        '清华大学', '北京大学', '复旦大学', '上海交通大学', '浙江大学', '南京大学',
        '中国科学技术大学', '中国人民大学', '北京师范大学', '中山大学', '武汉大学',
        '华中科技大学', '哈尔滨工业大学', '西安交通大学', '东南大学', '南开大学',
        '天津大学', '四川大学', '吉林大学', '山东大学', '厦门大学', '重庆大学',
        '兰州大学', '同济大学',
        '加州大学伯克利分校', '加州大学洛杉矶分校', '加州理工学院', '斯坦福大学', '麻省理工学院',
        '哈佛大学', '耶鲁大学', '普林斯顿大学', '哥伦比亚大学', '芝加哥大学', '宾夕法尼亚大学',
        '西北大学', '约翰霍普金斯大学', '密歇根大学', '德克萨斯大学奥斯汀分校', '威斯康星大学麦迪逊分校',
        '伊利诺伊大学厄巴纳-香槟分校', '普渡大学', '佐治亚理工学院', '北卡罗来纳大学教堂山分校',
        '弗吉尼亚大学', '卡内基梅隆大学', '莱斯大学', '埃默里大学', '范德堡大学', '华盛顿大学',
        '波士顿大学', '波士顿学院', '东北大学', '乔治城大学', '塔夫茨大学', '布兰迪斯大学',
        '凯莱商学院', '凯洛格商学院', '沃顿商学院', '布斯商学院', '哈斯商学院', '斯特恩商学院',
        '纽约大学',
    ]
    
    for keyword in uni_keywords:
        if keyword in cleaned:
            cleaned = keyword
            break
    
    if not any(kw in cleaned for kw in ['大学', '学院']):
        for kw in ['UCL', 'MIT', 'CMU', 'NYU', 'UCLA', 'USC', 'LSE', 'KCL', 'ANU', 'UBC', 'UIUC', 'BU', 'BC', 'UW']:
            if kw in cleaned:
                cleaned = kw
                break
    
    prefixes_to_remove = ['喜获', '斩获', '拿到', '收到', '获得', '顺利', '成功', '拱顶建筑便是', '级准', '年',
                          '招生办公室', '在报名系统和', '和实施接受', '附件', '本科招生网',
                          '招生办', '报名系统', '实施接受', '网', '系统', '办公室', '和', '在']
    for prefix in prefixes_to_remove:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
            break
    
    middle_patterns = [
        r'.*?([\u4e00-\u9fff]+大学)',
        r'.*?([\u4e00-\u9fff]+学院)',
    ]
    if not any(kw in cleaned for kw in uni_keywords):
        for pattern in middle_patterns:
            match = re.search(pattern, cleaned)
            if match:
                cleaned = match.group(1)
                break
    
    suffixes = ['录取', '通知', 'offer', '首封', '本科生', '研究生', '硕士', '博士', '申请', '封', '送达']
    for suffix in suffixes:
        if cleaned.endswith(suffix):
            cleaned = cleaned[:-len(suffix)].strip()
    
    if len(cleaned) < 2:
        return uni
    
    return cleaned


async def process_single_task_async(tid: int) -> dict:
    """异步处理单个采集任务"""

    conn = get_db_connection()
    c = conn.cursor()

    try:
        exec_sql(c, "SELECT * FROM collection_tasks WHERE id = %s" if DB_TYPE == "mysql" else "SELECT * FROM collection_tasks WHERE id = ?", (tid,))
        row = c.fetchone()
        if not row or row["task_status"] != 2:
            return {"task_id": tid, "status": "skipped"}
        url = row["article_url"]
        recognition_model = row["recognition_model"] if "recognition_model" in row.keys() else ""

        html = await _fetch_html(url)
        tree = _parse_html(html)
        title = _extract_title(tree)
        if not title:
            m = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
            if m:
                title = m.group(1).strip()
        school = _extract_school(tree)
        exec_sql(c, "UPDATE collection_tasks SET title = %s, source_school_name = %s WHERE id = %s" if DB_TYPE == "mysql" else "UPDATE collection_tasks SET title = ?, source_school_name = ? WHERE id = ?", (title or "", school or "未知", tid))
        
        # 只使用大模型整页识别
        all_record_dicts = []
        
        try:
            from app.image_extractor import extract_from_url_fullpage
            extract_result = await asyncio.wait_for(
                extract_from_url_fullpage(url),
                timeout=60.0
            )
            extracted_records = extract_result.get("records", [])
            for r in extracted_records:
                uni = r.university_cn or ""
                if uni:
                    uni = _clean_university_name(uni)
                rec = {
                    "student_name_cn": r.student_name_cn or "",
                    "student_name_en": r.student_name_en or "",
                    "university_cn": uni,
                    "university_en": r.university_en or "",
                    "major_cn": r.major_cn or "",
                    "major_en": r.major_en or "",
                    "country": r.country or "",
                    "admission_year": r.admission_year or "",
                    "scholarship_amount": r.scholarship_amount or "",
                    "scholarship_currency": r.scholarship_currency or "",
                    "admission_type": r.admission_type or "",
                    "admission_status": r.admission_status or "",
                    "article_url": r.article_url or url,
                    "article_title": extract_result.get("page_title", title) or "",
                    "data_source": r.data_source or school or "",
                }
                if rec["student_name_cn"] or rec["university_cn"]:
                    all_record_dicts.append(rec)
            logger.info(f"整页识别提取到 {len(extracted_records)} 条记录 (task {tid})")
        except asyncio.TimeoutError:
            logger.warning(f"整页识别超时 (task {tid})")
        except Exception as e:
            logger.warning(f"整页识别失败: {e} (task {tid})")

        all_record_dicts = [r for r in all_record_dicts if r.get("student_name_cn") or r.get("university_cn")]

        if all_record_dicts:
            from app.smart_corrector import correct_records
            try:
                all_record_dicts = await correct_records(all_record_dicts)
                logger.info(f"SmartCorrector: corrected {len(all_record_dicts)} records for task {tid}")
            except Exception as e:
                logger.warning(f"SmartCorrector: correction failed for task {tid}: {e}")

        review_status = "pending"

        if all_record_dicts:
            allowed_fields = [
                "student_name_cn", "student_name_en", "student_grade",
                "country", "country_en",
                "university_cn", "university_en", "university_type", "university_ranking",
                "major_cn", "major_en", "major_category",
                "admission_type", "admission_status",
                "admission_year",
                "scholarship_amount", "scholarship_currency", "scholarship_type",
                "article_url", "article_title",
                "recognition_model", "notes",
                "data_source"
            ]
            required_fields = ["student_name_cn", "university_cn"]
            
            # 过滤掉学生姓名和大学名称都为空或"未知"的记录
            all_record_dicts = [r for r in all_record_dicts if (r.get("student_name_cn") and r.get("student_name_cn") != "未知") or (r.get("university_cn") and r.get("university_cn") != "未知")]
            
            for rec in all_record_dicts:
                rec["review_status"] = review_status
                rec["recognition_model"] = recognition_model
                clean = {}
                for k, v in rec.items():
                    if k in allowed_fields:
                        if k in required_fields:
                            clean[k] = v or "未知"
                        elif v:
                            clean[k] = v
                if "scholarship_amount" in clean:
                    try:
                        amt = str(clean["scholarship_amount"]).replace(",", "").replace("$", "").replace("£", "").replace("€", "").strip()
                        clean["scholarship_amount"] = float(amt)
                    except (ValueError, TypeError):
                        del clean["scholarship_amount"]
                if "admission_year" in clean:
                    try:
                        clean["admission_year"] = int(clean["admission_year"])
                    except (ValueError, TypeError):
                        del clean["admission_year"]
                columns = list(clean.keys())
                columns.append("created_at")
                if DB_TYPE == "mysql":
                    placeholders = ["%s"] * len(columns[:-1]) + ["CURRENT_TIMESTAMP"]
                else:
                    placeholders = ["?"] * len(columns[:-1]) + ["CURRENT_TIMESTAMP"]
                values = [clean[col] for col in columns[:-1]]
                query = f"INSERT INTO admission_records_staging ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
                c.execute(query, values)

        extracted_count = len(all_record_dicts)
        ai_passed = 0
        ai_rejected = 0
        exec_sql(c,
            "UPDATE collection_tasks SET task_status = %s, extracted_count = %s, completed_at = CURRENT_TIMESTAMP WHERE id = %s" if DB_TYPE == "mysql" else "UPDATE collection_tasks SET task_status = 3, extracted_count = ?, completed_at = CURRENT_TIMESTAMP WHERE id = ?",
            (3, extracted_count, tid),
        )
        conn.commit()
        return {"task_id": tid, "status": "success", "extracted": extracted_count, "ai_passed": ai_passed, "ai_rejected": ai_rejected}
    except Exception as e:
        err_str = str(e)
        try:
            exec_sql(c, "SELECT retry_count, max_retry FROM collection_tasks WHERE id = %s" if DB_TYPE == "mysql" else "SELECT retry_count, max_retry FROM collection_tasks WHERE id = ?", (tid,))
            rr = c.fetchone()
            retry = (rr.get("retry_count") if isinstance(rr, dict) else rr[0] or 0) + 1 if rr else 1
            maxr = rr.get("max_retry") if isinstance(rr, dict) else rr[1] if rr else 3
            err = err_str[:500]

            is_anti_crawl = any(kw in err_str for kw in ["403", "anti_bot", "cooldown", "anti_crawl"])

            if is_anti_crawl and retry <= maxr:
                backoff = min(30 + retry * 15, 180)
                if DB_TYPE == "mysql":
                    c.execute(
                        "UPDATE collection_tasks SET task_status = 0, retry_count = %s, error_message = %s, next_retry_at = DATE_ADD(NOW(), INTERVAL {} SECOND) WHERE id = %s".format(backoff),
                        (retry, err, tid))
                else:
                    exec_sql(c,
                        "UPDATE collection_tasks SET task_status = 0, retry_count = ?, error_message = ?, next_retry_at = datetime('now', '+{} seconds') WHERE id = ?".format(backoff),
                        (retry, err, tid))
            elif retry <= maxr:
                exec_sql(c, "UPDATE collection_tasks SET task_status = 0, retry_count = %s, error_message = %s WHERE id = %s" if DB_TYPE == "mysql" else "UPDATE collection_tasks SET task_status = 0, retry_count = ?, error_message = ? WHERE id = ?", (retry, err, tid))
            else:
                exec_sql(c, "UPDATE collection_tasks SET task_status = 4, retry_count = %s, error_message = %s WHERE id = %s" if DB_TYPE == "mysql" else "UPDATE collection_tasks SET task_status = 4, retry_count = ?, error_message = ? WHERE id = ?", (retry, err, tid))
            conn.commit()
        except Exception:
            pass
        return {"task_id": tid, "status": "error", "error": err_str[:200]}
    finally:
        conn.close()


def get_anti_crawl_state() -> dict:
    """获取当前反爬状态"""
    return {
        "consecutive_failures": _anti_crawl_state["consecutive_failures"],
        "cooldown_until": _anti_crawl_state["cooldown_until"],
        "is_in_cooldown": _is_in_cooldown(),
        "cooldown_remaining": _get_cooldown_remaining(),
        "total_requests": _anti_crawl_state["total_requests"],
        "total_403": _anti_crawl_state["total_403"],
    }
