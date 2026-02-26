#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本 - 检查服务器并运行基本测试
"""

import requests
import json
import sys

def check_server():
    """检查服务器是否运行"""
    try:
        response = requests.get("http://localhost:5000/health", timeout=2)
        if response.status_code == 200:
            print("✅ 服务器运行正常")
            return True
    except:
        pass
    print("❌ 服务器未运行")
    print("\n请先启动服务器:")
    print("  python test_webhook_server.py")
    return False

def test_basic():
    """基本测试"""
    print("\n" + "=" * 60)
    print("运行基本测试")
    print("=" * 60)
    
    # 测试1: 健康检查
    print("\n[测试1] 健康检查...")
    try:
        r = requests.get("http://localhost:5000/health", timeout=5)
        print(f"✅ 状态码: {r.status_code}")
        print(f"✅ 响应: {r.json()}")
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False
    
    # 测试2: 发送webhook
    print("\n[测试2] 发送webhook到默认端点...")
    try:
        r = requests.post(
            "http://localhost:5000/webhook",
            json={"message": "测试消息", "test": True},
            headers={"X-Webhook-Secret": "my-secret-key"},
            timeout=5
        )
        print(f"✅ 状态码: {r.status_code}")
        print(f"✅ 响应: {json.dumps(r.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False
    
    # 测试3: 自定义端点
    print("\n[测试3] 发送到自定义端点 (test)...")
    try:
        r = requests.post(
            "http://localhost:5000/webhook/test",
            json={"test": "custom endpoint"},
            headers={"X-Webhook-Secret": "my-secret-key"},
            timeout=5
        )
        print(f"✅ 状态码: {r.status_code}")
        print(f"✅ 响应: {json.dumps(r.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False
    
    # 测试4: 密钥验证
    print("\n[测试4] 测试密钥验证（错误密钥）...")
    try:
        r = requests.post(
            "http://localhost:5000/webhook",
            json={"message": "test"},
            headers={"X-Webhook-Secret": "wrong-secret"},
            timeout=5
        )
        if r.status_code == 401:
            print(f"✅ 状态码: {r.status_code} (预期: 401)")
            print(f"✅ 密钥验证正常工作")
        else:
            print(f"⚠️  状态码: {r.status_code} (预期: 401)")
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 基本测试完成！")
    print("=" * 60)
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Webhook 系统快速测试")
    print("=" * 60)
    
    if not check_server():
        sys.exit(1)
    
    test_basic()

