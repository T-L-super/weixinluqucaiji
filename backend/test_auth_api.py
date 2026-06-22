#!/usr/bin/env python3
# 完成时间：2026-03-20 16:05 UTC - Agent-10 用户权限管理
"""
用户认证 API 测试脚本
"""

import requests

BASE_URL = "http://localhost:8000"

def test_login():
    """测试登录"""
    print("🔐 测试登录...")
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 登录成功")
        print(f"  Token: {data['access_token'][:50]}...")
        print(f"  用户：{data['user']['username']} ({data['user']['role_name']})")
        return data['access_token']
    else:
        print(f"✗ 登录失败：{response.status_code} - {response.text}")
        return None


def test_get_me(token):
    """测试获取当前用户信息"""
    print("\n👤 测试获取当前用户信息...")
    response = requests.get(f"{BASE_URL}/api/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 获取成功")
        print(f"  用户：{data['username']}")
        print(f"  角色：{data['role_name']}")
        print(f"  权限：{data['permissions']}")
    else:
        print(f"✗ 获取失败：{response.status_code} - {response.text}")


def test_get_roles(token):
    """测试获取角色列表"""
    print("\n📋 测试获取角色列表...")
    response = requests.get(f"{BASE_URL}/api/roles", headers={
        "Authorization": f"Bearer {token}"
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 获取成功，共 {data['total']} 个角色")
        for role in data['roles']:
            print(f"  - {role['name']}: {role['description']}")
    else:
        print(f"✗ 获取失败：{response.status_code} - {response.text}")


def test_get_users(token):
    """测试获取用户列表"""
    print("\n👥 测试获取用户列表...")
    response = requests.get(f"{BASE_URL}/api/users", headers={
        "Authorization": f"Bearer {token}"
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 获取成功，共 {data['total']} 个用户")
        for user in data['users']:
            print(f"  - {user['username']} ({user['role_name']}) - {'激活' if user['is_active'] else '停用'}")
    else:
        print(f"✗ 获取失败：{response.status_code} - {response.text}")


def test_unauthorized():
    """测试未授权访问"""
    print("\n🚫 测试未授权访问...")
    response = requests.get(f"{BASE_URL}/api/auth/me")
    
    if response.status_code == 401:
        print(f"✓ 正确返回 401 未授权")
    else:
        print(f"✗ 预期 401，实际返回：{response.status_code}")


def test_wrong_password():
    """测试错误密码"""
    print("\n❌ 测试错误密码...")
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": "admin",
        "password": "wrongpassword"
    })
    
    if response.status_code == 401:
        print(f"✓ 正确返回 401 未授权")
    else:
        print(f"✗ 预期 401，实际返回：{response.status_code}")


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 用户认证 API 测试")
    print("=" * 60)
    
    try:
        # 测试未授权访问
        test_unauthorized()
        
        # 测试错误密码
        test_wrong_password()
        
        # 测试登录
        token = test_login()
        
        if token:
            # 测试获取当前用户
            test_get_me(token)
            
            # 测试获取角色列表
            test_get_roles(token)
            
            # 测试获取用户列表
            test_get_users(token)
        
        print("\n" + "=" * 60)
        print("✅ 测试完成")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器，请确保服务已启动")
        print(f"   运行：cd /root/.openclaw/workspace/大学录取信息整理系统/backend && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"\n❌ 测试出错：{e}")
