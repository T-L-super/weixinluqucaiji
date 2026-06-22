import sys
sys.path.insert(0, 'd:/大学录取信息整理系统/collector')

try:
    from extractor import WeChatArticleExtractor, AdmissionRecord
    print("extractor.py 导入成功")
except Exception as e:
    print(f"extractor.py 导入失败: {e}")

try:
    from queue_manager import TaskQueueManager, TaskResult, process_article_task
    print("queue_manager.py 导入成功")
except Exception as e:
    print(f"queue_manager.py 导入失败: {e}")

try:
    from skill_main import AdmissionCollectorSkill
    print("skill_main.py 导入成功")
except Exception as e:
    print(f"skill_main.py 导入失败: {e}")

print("测试完成")