# Webhook 系统测试指南

## 快速测试步骤

### 方法1: 自动测试（推荐）

**步骤1: 启动接收器服务器**

在一个终端窗口中运行：
```bash
cd /Users/francinapeng/Public
python test_webhook_server.py
```

你会看到：
```
============================================================
Webhook 接收器已启动
============================================================
端点:
  - GET  http://localhost:5000/health
  - POST http://localhost:5000/webhook
  - POST http://localhost:5000/webhook/test
  - POST http://localhost:5000/webhook/payment
密钥: my-secret-key
============================================================
```

**步骤2: 运行测试（新开一个终端）**

在另一个终端窗口中运行：
```bash
cd /Users/francinapeng/Public
python run_tests.py
```

这将自动运行所有测试并显示结果。

### 方法2: 手动测试

#### 测试1: 健康检查
```bash
curl http://localhost:5000/health
```

#### 测试2: 发送webhook到默认端点
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: my-secret-key" \
  -d '{"message": "测试消息", "test": true}'
```

#### 测试3: 发送到自定义端点
```bash
curl -X POST http://localhost:5000/webhook/test \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: my-secret-key" \
  -d '{"test_message": "这是测试"}'
```

#### 测试4: 发送支付通知
```bash
curl -X POST http://localhost:5000/webhook/payment \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: my-secret-key" \
  -d '{"order_id": "ORD-123", "amount": 99.99, "status": "completed"}'
```

#### 测试5: 测试密钥验证（应该返回401）
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: wrong-secret" \
  -d '{"message": "测试"}'
```

#### 测试6: 使用Python发送器测试
```python
from webhook_sender import WebhookSender

sender = WebhookSender()
result = sender.send(
    url="http://localhost:5000/webhook/test",
    data={"from": "sender", "message": "Hello"},
    secret="my-secret-key"
)
print(result)
```

### 方法3: 使用测试脚本（交互式）

```bash
python webhook_test.py
```

然后选择：
- `1` - 测试接收器
- `2` - 测试发送器
- `3` - 测试全部

## 预期结果

### 成功响应示例
```json
{
  "status": "success",
  "message": "Webhook received and processed",
  "result": {
    "processed": true,
    "message": "Test handler executed"
  }
}
```

### 错误响应示例（密钥错误）
```json
{
  "error": "Unauthorized",
  "message": "Invalid secret"
}
```

## 查看日志

所有操作都会记录到 `webhook.log` 文件中：
```bash
tail -f webhook.log
```

## 常见问题

**Q: 端口5000已被占用？**
A: 修改 `test_webhook_server.py` 中的端口号，例如改为 5001

**Q: 连接被拒绝？**
A: 确保接收器服务器已启动

**Q: 密钥验证失败？**
A: 确保请求头中包含正确的密钥：`X-Webhook-Secret: my-secret-key`

