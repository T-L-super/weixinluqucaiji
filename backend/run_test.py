import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
import time
import json

def get_anti_crawl_status():
    try:
        r = requests.get('http://localhost:8000/api/anti-crawl/status')
        return r.json() if r.ok else None
    except Exception as e:
        print(f"获取反爬状态失败: {e}")
        return None

def start_batch_tasks():
    try:
        r = requests.post(
            'http://localhost:8000/api/collection-tasks/batch-start',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({})
        )
        return r.json() if r.ok else None
    except Exception as e:
        print(f"启动任务失败: {e}")
        return None

def get_task_stats():
    try:
        r = requests.get('http://localhost:8000/api/stats/overview')
        data = r.json() if r.ok else {}
        return data.get('tasks', {})
    except Exception as e:
        print(f"获取任务统计失败: {e}")
        return {}

print("=" * 70)
print("微信反爬优化效果测试")
print("=" * 70)

print("\n1. 检查初始状态")
anti_state = get_anti_crawl_status()
if anti_state:
    print(f"   连续失败: {anti_state['consecutive_failures']}")
    print(f"   冷却中: {anti_state['is_in_cooldown']}")
    print(f"   总请求: {anti_state['total_requests']}")
    print(f"   403次数: {anti_state['total_403']}")

print("\n2. 获取任务统计")
stats = get_task_stats()
print(f"   总任务: {stats.get('total', 0)}")
print(f"   待执行: {stats.get('pending', 0)}")
print(f"   执行中: {stats.get('processing', 0)}")
print(f"   已完成: {stats.get('completed', 0)}")

print("\n3. 开始执行任务（系统限制单次最多100条）")
print("-" * 70)

result = start_batch_tasks()
if result:
    started = result.get('started', 0)
    print(f"\n✓ 已启动 {started} 个任务")
    print(f"📊 并发数: {result.get('concurrent', 1)}")
    print(f"⌛ 反爬保护已启用")
    
    if result.get('anti_crawl'):
        print(f"\n反爬状态:")
        print(f"  连续失败: {result['anti_crawl']['consecutive_failures']}")
        print(f"  冷却中: {result['anti_crawl']['is_in_cooldown']}")
    
    print(f"\n4. 监控执行进度...")
    print("-" * 70)
    
    for i in range(60):
        time.sleep(10)
        
        anti_state = get_anti_crawl_status()
        stats = get_task_stats()
        
        print(f"\n[{i+1}] 进度:")
        print(f"  待执行: {stats.get('pending', 0)}")
        print(f"  执行中: {stats.get('processing', 0)}")
        print(f"  已完成: {stats.get('completed', 0)}")
        print(f"  失败: {stats.get('failed', 0)}")
        
        if anti_state:
            print(f"\n  反爬状态:")
            print(f"    连续失败: {anti_state['consecutive_failures']}")
            print(f"    冷却中: {anti_state['is_in_cooldown']}")
            print(f"    总请求: {anti_state['total_requests']}")
            print(f"    403次数: {anti_state['total_403']}")
            
            if anti_state['is_in_cooldown']:
                print(f"\n    ⚠ 反爬冷却触发！剩余 {anti_state['cooldown_remaining']:.0f} 秒")
                break
        
        if stats.get('processing', 0) == 0 and stats.get('pending', 0) == 0:
            print("\n✓ 所有任务已完成")
            break

print("\n" + "=" * 70)
print("测试完成!")
print("=" * 70)

stats = get_task_stats()
anti_state = get_anti_crawl_status()

print(f"\n【最终统计】")
print(f"  待执行: {stats.get('pending', 0)}")
print(f"  执行中: {stats.get('processing', 0)}")
print(f"  已完成: {stats.get('completed', 0)}")
print(f"  失败: {stats.get('failed', 0)}")

if anti_state:
    print(f"\n【反爬状态】")
    print(f"  总请求: {anti_state['total_requests']}")
    print(f"  403次数: {anti_state['total_403']}")
    print(f"  连续失败: {anti_state['consecutive_failures']}")
    print(f"  冷却中: {anti_state['is_in_cooldown']}")
    
    if anti_state['total_requests'] > 0:
        success_rate = ((anti_state['total_requests'] - anti_state['total_403']) / anti_state['total_requests']) * 100
        print(f"\n【成功率】")
        print(f"  请求成功率: {success_rate:.1f}% ({anti_state['total_requests'] - anti_state['total_403']}/{anti_state['total_requests']})")

print("\n" + "=" * 70)
