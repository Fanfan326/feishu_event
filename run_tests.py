#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动运行所有测试（非交互式）
"""

import requests
import json
import time
from webhook_sender import WebhookSender


def test_health_check():
    """测试健康检查"""
    print("\n" + "=" * 60)
    print("测试1: 健康检查端点")
    print("=" * 60)
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        print(f"✅ 状态码: {response.status_code}")
        print(f"✅ 响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        print("   提示: 请确保接收器已启动")
        return False


def test_default_webhook():
    """测试默认webhook端点"""
    print("\n" + "=" * 60)
    print("测试2: 默认 webhook 端点")
    print("=" * 60)
    try:
        response = requests.post(
            "http://localhost:5000/webhook",
            json={"message": "测试消息", "test": True, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")},
            headers={"X-Webhook-Secret": "my-secret-key", "Content-Type": "application/json"},
            timeout=5
        )
        print(f"✅ 状态码: {response.status_code}")
        print(f"✅ 响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_custom_endpoint():
    """测试自定义端点"""
    print("\n" + "=" * 60)
    print("测试3: 自定义端点 (test)")
    print("=" * 60)
    try:
        response = requests.post(
            "http://localhost:5000/webhook/test",
            json={"test_message": "这是测试消息", "number": 123},
            headers={"X-Webhook-Secret": "my-secret-key", "Content-Type": "application/json"},
            timeout=5
        )
        print(f"✅ 状态码: {response.status_code}")
        print(f"✅ 响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_payment_endpoint():
    """测试支付端点"""
    print("\n" + "=" * 60)
    print("测试4: 支付端点 (payment)")
    print("=" * 60)
    try:
        response = requests.post(
            "http://localhost:5000/webhook/payment",
            json={
                "order_id": "ORD-12345",
                "amount": 199.99,
                "status": "completed",
                "currency": "USD"
            },
            headers={"X-Webhook-Secret": "my-secret-key", "Content-Type": "application/json"},
            timeout=5
        )
        print(f"✅ 状态码: {response.status_code}")
        print(f"✅ 响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_secret_validation():
    """测试密钥验证"""
    print("\n" + "=" * 60)
    print("测试5: 密钥验证（错误密钥）")
    print("=" * 60)
    try:
        response = requests.post(
            "http://localhost:5000/webhook",
            json={"message": "测试"},
            headers={"X-Webhook-Secret": "wrong-secret", "Content-Type": "application/json"},
            timeout=5
        )
        print(f"✅ 状态码: {response.status_code} (预期: 401)")
        print(f"✅ 响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response.status_code == 401
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_form_data():
    """测试表单数据"""
    print("\n" + "=" * 60)
    print("测试6: 表单数据")
    print("=" * 60)
    try:
        response = requests.post(
            "http://localhost:5000/webhook",
            data={"field1": "value1", "field2": "value2"},
            headers={"X-Webhook-Secret": "my-secret-key"},
            timeout=5
        )
        print(f"✅ 状态码: {response.status_code}")
        print(f"✅ 响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_sender():
    """测试发送器"""
    print("\n" + "=" * 60)
    print("测试7: Webhook 发送器 - 发送到本地接收器")
    print("=" * 60)
    sender = WebhookSender()
    
    result = sender.send(
        url="http://localhost:5000/webhook/test",
        data={"from": "sender_test", "message": "Hello from sender", "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")},
        headers={"X-Custom-Header": "test-value"},
        secret="my-secret-key"
    )
    
    if result['success']:
        print(f"✅ 发送成功")
        print(f"✅ 状态码: {result.get('status_code')}")
        if result.get('response_data'):
            print(f"✅ 响应数据: {json.dumps(result['response_data'], ensure_ascii=False, indent=2)}")
    else:
        print(f"❌ 发送失败: {result.get('error', 'Unknown error')}")
    
    return result['success']


def test_sender_external():
    """测试发送器发送到外部服务"""
    print("\n" + "=" * 60)
    print("测试8: Webhook 发送器 - 发送到外部服务 (httpbin)")
    print("=" * 60)
    sender = WebhookSender()
    
    result = sender.send(
        url="https://httpbin.org/post",
        data={"test": "message", "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")},
        secret="test-secret"
    )
    
    if result['success']:
        print(f"✅ 发送成功")
        print(f"✅ 状态码: {result.get('status_code')}")
        print(f"✅ 耗时: {result.get('elapsed_time', 0):.2f}秒")
    else:
        print(f"❌ 发送失败: {result.get('error', 'Unknown error')}")
    
    return result['success']


def test_batch_send():
    """测试批量发送"""
    print("\n" + "=" * 60)
    print("测试9: 批量发送")
    print("=" * 60)
    sender = WebhookSender()
    
    results = sender.send_batch(
        urls=[
            "http://localhost:5000/webhook/test",
            "http://localhost:5000/webhook/test"
        ],
        data={"batch_test": True, "message": "Batch message"},
        secret="my-secret-key"
    )
    
    success_count = sum(1 for r in results if r.get('success'))
    print(f"✅ 成功: {success_count}/{len(results)}")
    
    for i, result in enumerate(results, 1):
        status = "✅" if result['success'] else "❌"
        print(f"  {status} URL {i}: {result.get('url', 'N/A')} - {result.get('status_code', 'N/A')}")
    
    return success_count == len(results)


def main():
    """运行所有测试"""
    print("=" * 60)
    print("Webhook 系统测试")
    print("=" * 60)
    print("\n等待服务器启动...")
    time.sleep(2)
    
    results = []
    
    # 测试接收器
    results.append(("健康检查", test_health_check()))
    time.sleep(0.5)
    
    results.append(("默认端点", test_default_webhook()))
    time.sleep(0.5)
    
    results.append(("自定义端点", test_custom_endpoint()))
    time.sleep(0.5)
    
    results.append(("支付端点", test_payment_endpoint()))
    time.sleep(0.5)
    
    results.append(("密钥验证", test_secret_validation()))
    time.sleep(0.5)
    
    results.append(("表单数据", test_form_data()))
    time.sleep(0.5)
    
    # 测试发送器
    results.append(("发送器-本地", test_sender()))
    time.sleep(0.5)
    
    results.append(("发送器-外部", test_sender_external()))
    time.sleep(0.5)
    
    results.append(("批量发送", test_batch_send()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")


if __name__ == "__main__":
    main()

