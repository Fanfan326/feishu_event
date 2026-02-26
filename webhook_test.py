#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Webhook 测试脚本
用于测试 webhook 接收器和发送器
"""

import requests
import json
import time
from webhook_sender import WebhookSender


def test_receiver():
    """测试接收器"""
    base_url = "http://localhost:5000"
    
    print("=" * 60)
    print("测试 Webhook 接收器")
    print("=" * 60)
    
    # 测试1: 健康检查
    print("\n1. 测试健康检查端点")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        print("   提示: 请先启动接收器 (python webhook_receiver.py)")
        return
    
    # 测试2: 发送到默认端点
    print("\n2. 测试默认 webhook 端点")
    try:
        response = requests.post(
            f"{base_url}/webhook",
            json={"message": "测试消息", "test": True},
            headers={"X-Webhook-Secret": "my-secret-key"},
            timeout=5
        )
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 测试3: 发送到自定义端点
    print("\n3. 测试自定义端点 (payment)")
    try:
        response = requests.post(
            f"{base_url}/webhook/payment",
            json={
                "order_id": "TEST-12345",
                "amount": 199.99,
                "status": "completed"
            },
            headers={"X-Webhook-Secret": "my-secret-key"},
            timeout=5
        )
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 测试4: 测试密钥验证
    print("\n4. 测试密钥验证（错误密钥）")
    try:
        response = requests.post(
            f"{base_url}/webhook",
            json={"message": "测试"},
            headers={"X-Webhook-Secret": "wrong-secret"},
            timeout=5
        )
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 测试5: 测试表单数据
    print("\n5. 测试表单数据")
    try:
        response = requests.post(
            f"{base_url}/webhook",
            data={"field1": "value1", "field2": "value2"},
            headers={"X-Webhook-Secret": "my-secret-key"},
            timeout=5
        )
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")


def test_sender():
    """测试发送器"""
    print("\n" + "=" * 60)
    print("测试 Webhook 发送器")
    print("=" * 60)
    
    sender = WebhookSender()
    
    # 测试1: 发送到 httpbin
    print("\n1. 发送到 httpbin.org")
    result = sender.send(
        url="https://httpbin.org/post",
        data={"test": "message", "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")},
        secret="test-secret"
    )
    print(f"   成功: {result['success']}")
    if result.get('status_code'):
        print(f"   状态码: {result['status_code']}")
    if result.get('error'):
        print(f"   错误: {result['error']}")
    
    # 测试2: 发送到本地接收器
    print("\n2. 发送到本地接收器")
    result = sender.send(
        url="http://localhost:5000/webhook",
        data={"from": "sender_test", "message": "Hello from sender"},
        headers={"X-Custom-Header": "test-value"},
        secret="my-secret-key"
    )
    print(f"   成功: {result['success']}")
    if result.get('status_code'):
        print(f"   状态码: {result['status_code']}")
    if result.get('error'):
        print(f"   错误: {result['error']}")
    
    # 测试3: 批量发送
    print("\n3. 批量发送测试")
    results = sender.send_batch(
        urls=["https://httpbin.org/post", "https://httpbin.org/post"],
        data={"batch_test": True}
    )
    for i, result in enumerate(results, 1):
        print(f"   URL {i}: {'成功' if result['success'] else '失败'}")


def main():
    """主函数"""
    print("\n选择测试:")
    print("1. 测试接收器（需要先启动接收器）")
    print("2. 测试发送器")
    print("3. 测试全部")
    print("0. 退出")
    
    choice = input("\n请选择 (0-3): ").strip()
    
    if choice == "1":
        test_receiver()
    elif choice == "2":
        test_sender()
    elif choice == "3":
        test_receiver()
        test_sender()
    elif choice == "0":
        print("退出")
    else:
        print("无效的选择")


if __name__ == "__main__":
    main()

