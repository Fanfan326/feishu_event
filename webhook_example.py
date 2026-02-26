#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Webhook 接收器和发送器综合示例
演示如何使用接收器和发送器
"""

import json
import threading
import time
from webhook_receiver import WebhookReceiver
from webhook_sender import WebhookSender


def example_receiver():
    """示例1: 启动 Webhook 接收器"""
    print("=" * 60)
    print("示例1: Webhook 接收器")
    print("=" * 60)
    
    # 创建接收器（可选：设置密钥）
    receiver = WebhookReceiver(secret="my-secret-key")
    
    # 注册自定义处理器
    def handle_payment_webhook(webhook_info):
        """处理支付 webhook"""
        data = webhook_info.get('data', {})
        print(f"\n收到支付通知:")
        print(f"  订单号: {data.get('order_id', 'N/A')}")
        print(f"  金额: {data.get('amount', 'N/A')}")
        print(f"  状态: {data.get('status', 'N/A')}")
        
        # 在这里处理你的业务逻辑
        # 例如：更新数据库、发送通知等
        
        return {
            "processed": True,
            "order_id": data.get('order_id'),
            "message": "Payment processed successfully"
        }
    
    def handle_notification_webhook(webhook_info):
        """处理通知 webhook"""
        data = webhook_info.get('data', {})
        print(f"\n收到通知:")
        print(f"  标题: {data.get('title', 'N/A')}")
        print(f"  内容: {data.get('content', 'N/A')}")
        
        return {"processed": True}
    
    # 注册处理器
    receiver.register_handler('payment', handle_payment_webhook)
    receiver.register_handler('notification', handle_notification_webhook)
    
    print("\nWebhook 接收器已启动")
    print("端点:")
    print("  - POST http://localhost:5000/webhook (默认)")
    print("  - POST http://localhost:5000/webhook/payment (支付)")
    print("  - POST http://localhost:5000/webhook/notification (通知)")
    print("  - GET  http://localhost:5000/health (健康检查)")
    print("\n按 Ctrl+C 停止服务器\n")
    
    # 启动服务器
    receiver.run(host='0.0.0.0', port=5000, debug=False)


def example_sender():
    """示例2: 使用 Webhook 发送器"""
    print("=" * 60)
    print("示例2: Webhook 发送器")
    print("=" * 60)
    
    sender = WebhookSender(timeout=10, max_retries=3)
    
    # 示例1: 发送简单消息
    print("\n1. 发送简单消息到 httpbin.org")
    result = sender.send(
        url="https://httpbin.org/post",
        data={
            "message": "Hello from Webhook Sender",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        secret="test-secret"
    )
    print(f"结果: {'成功' if result['success'] else '失败'}")
    if result.get('status_code'):
        print(f"状态码: {result['status_code']}")
    
    # 示例2: 发送到本地接收器
    print("\n2. 发送到本地接收器")
    result = sender.send(
        url="http://localhost:5000/webhook/payment",
        data={
            "order_id": "ORD-12345",
            "amount": 99.99,
            "status": "completed",
            "currency": "USD"
        },
        headers={"X-Custom-Header": "custom-value"},
        secret="my-secret-key"
    )
    print(f"结果: {'成功' if result['success'] else '失败'}")
    if result.get('error'):
        print(f"错误: {result['error']}")
    
    # 示例3: 批量发送
    print("\n3. 批量发送到多个端点")
    urls = [
        "https://httpbin.org/post",
        "https://httpbin.org/post",
    ]
    results = sender.send_batch(
        urls=urls,
        data={"batch_message": "This is a batch message"},
        secret="batch-secret"
    )
    for i, result in enumerate(results, 1):
        print(f"  URL {i}: {'成功' if result['success'] else '失败'}")
    
    # 示例4: 带重试的发送
    print("\n4. 带重试的发送（到不存在的URL）")
    result = sender.send_with_retry(
        url="https://httpbin.org/status/500",  # 模拟服务器错误
        data={"test": "retry"},
        max_attempts=3
    )
    print(f"结果: {'成功' if result['success'] else '失败'}")


def example_integration():
    """示例3: 接收器和发送器集成使用"""
    print("=" * 60)
    print("示例3: 接收器和发送器集成")
    print("=" * 60)
    
    # 创建接收器
    receiver = WebhookReceiver(secret="integration-secret")
    
    # 创建发送器
    sender = WebhookSender()
    
    # 注册处理器：接收到 webhook 后转发到其他服务
    def forward_webhook(webhook_info):
        """接收到 webhook 后转发到其他服务"""
        data = webhook_info.get('data', {})
        endpoint = webhook_info.get('endpoint', 'default')
        
        print(f"\n收到 webhook - 端点: {endpoint}")
        print(f"数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        # 转发到外部服务（例如：飞书、Slack等）
        forward_urls = [
            "https://httpbin.org/post",  # 示例：替换为实际的 webhook URL
        ]
        
        # 添加额外信息
        forward_data = {
            **data,
            "forwarded_from": "webhook_receiver",
            "original_endpoint": endpoint,
            "forwarded_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 批量转发
        results = sender.send_batch(
            urls=forward_urls,
            data=forward_data,
            secret="forward-secret"
        )
        
        success_count = sum(1 for r in results if r.get('success'))
        print(f"转发结果: {success_count}/{len(forward_urls)} 成功")
        
        return {
            "processed": True,
            "forwarded": True,
            "forward_results": results
        }
    
    receiver.register_handler('forward', forward_webhook)
    
    print("\n集成示例已启动")
    print("发送 POST 请求到 http://localhost:5000/webhook/forward")
    print("接收器会自动转发到配置的外部服务")
    print("\n按 Ctrl+C 停止服务器\n")
    
    receiver.run(host='0.0.0.0', port=5000, debug=False)


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("Webhook 接收器和发送器示例")
    print("=" * 60)
    
    print("\n选择要运行的示例:")
    print("1. 启动 Webhook 接收器（需要手动测试）")
    print("2. 使用 Webhook 发送器发送消息")
    print("3. 接收器和发送器集成示例")
    print("0. 退出")
    
    choice = input("\n请选择 (0-3): ").strip()
    
    if choice == "1":
        example_receiver()
    elif choice == "2":
        example_sender()
    elif choice == "3":
        example_integration()
    elif choice == "0":
        print("退出")
    else:
        print("无效的选择")


if __name__ == "__main__":
    main()

