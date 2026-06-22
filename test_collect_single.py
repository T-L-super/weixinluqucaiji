import sys
sys.path.insert(0, 'collector')
sys.path.insert(0, 'backend/app')

from wechat_collector import WeChatArticleCollector
from extractor import WeChatArticleExtractor

url = 'https://mp.weixin.qq.com/s/Z10iL5ZpGpEEPs_YZEABpg'

print(f"=== 测试采集 URL: {url} ===")

# 1. 先尝试抓取文章内容
collector = WeChatArticleCollector()
print("\n【步骤1】抓取文章内容...")
article_result = collector.fetch_article(url)

if article_result.success:
    print(f"✓ 抓取成功")
    print(f"  标题: {article_result.title}")
    print(f"  学校: {article_result.school}")
    print(f"  HTML长度: {len(article_result.html)} 字符")
else:
    print(f"✗ 抓取失败: {article_result.error}")
    sys.exit(1)

# 2. 尝试提取数据
print("\n【步骤2】提取录取信息...")
extractor = WeChatArticleExtractor()
try:
    records = extractor.extract(article_result.html, article_result.title, url)
    print(f"✓ 提取完成")
    print(f"  提取到 {len(records)} 条记录")
    
    for i, record in enumerate(records, 1):
        print(f"\n  记录 {i}:")
        print(f"    姓名: {record.student_name_cn}")
        print(f"    大学: {record.university_cn}")
        print(f"    专业: {record.major_cn}")
        print(f"    国家: {record.country}")
        
except Exception as e:
    print(f"✗ 提取失败: {str(e)}")
    import traceback
    traceback.print_exc()
