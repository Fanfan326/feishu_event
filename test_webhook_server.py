#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用的 Webhook 接收器服务器
"""

from webhook_receiver import WebhookReceiver

# 创建接收器
receiver = WebhookReceiver(secret="my-secret-key")

# 注册测试处理器
def handle_test(webhook_info):
    """测试处理器"""
    data = webhook_info.get('data', {})
    print(f"\n[处理器] 收到测试消息: {data}")
    return {"processed": True, "message": "Test handler executed"}

def handle_payment(webhook_info):
    """支付处理器"""
    data = webhook_info.get('data', {})
    print(f"\n[处理器] 收到支付通知:")
    print(f"  订单号: {data.get('order_id', 'N/A')}")
    print(f"  金额: {data.get('amount', 'N/A')}")
    return {"processed": True, "order_id": data.get('order_id')}

# 注册处理器
receiver.register_handler('test', handle_test)
receiver.register_handler('payment', handle_payment)

print("=" * 60)
print("Webhook 接收器已启动")
print("=" * 60)
print("端点:")
print("  - GET  http://localhost:5000/health")
print("  - POST http://localhost:5000/webhook")
print("  - POST http://localhost:5000/webhook/test")
print("  - POST http://localhost:5000/webhook/payment")
print("密钥: my-secret-key")
print("=" * 60)

# 启动服务器
receiver.run(host='0.0.0.0', port=5000, debug=False)

