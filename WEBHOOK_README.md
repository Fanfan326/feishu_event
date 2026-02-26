# Webhook 接收器和发送器

一个完整的 Python Webhook 系统，包含接收器和发送器功能，支持错误处理和日志记录。

## 功能特性

### Webhook 接收器
- ✅ 使用 Flask 创建 webhook 端点
- ✅ 支持接收 POST 请求
- ✅ 支持多个自定义端点
- ✅ 密钥验证（可选）
- ✅ 自动解析 JSON、表单数据
- ✅ 自定义处理器支持
- ✅ 完整的错误处理和日志记录

### Webhook 发送器
- ✅ 发送 POST 请求到外部服务
- ✅ 自动重试机制
- ✅ 批量发送支持
- ✅ 超时控制
- ✅ 完整的错误处理和日志记录
- ✅ 响应时间统计

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

### 1. Webhook 接收器

#### 基本使用

```python
from webhook_receiver import WebhookReceiver

# 创建接收器（可选：设置密钥）
receiver = WebhookReceiver(secret="your-secret-key")

# 启动服务器
receiver.run(host='0.0.0.0', port=5000)
```

#### 注册自定义处理器

```python
def handle_payment(webhook_info):
    """处理支付 webhook"""
    data = webhook_info.get('data', {})
    # 处理业务逻辑
    return {"processed": True}

# 注册处理器
receiver.register_handler('payment', handle_payment)
```

#### 端点说明

- `GET /health` - 健康检查
- `POST /webhook` - 默认 webhook 端点
- `POST /webhook/<endpoint>` - 自定义端点（如 `/webhook/payment`）

#### 请求示例

```bash
# 发送到默认端点
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: your-secret-key" \
  -d '{"message": "Hello"}'

# 发送到自定义端点
curl -X POST http://localhost:5000/webhook/payment \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: your-secret-key" \
  -d '{"order_id": "123", "amount": 99.99}'
```

### 2. Webhook 发送器

#### 基本使用

```python
from webhook_sender import WebhookSender

# 创建发送器
sender = WebhookSender(timeout=10, max_retries=3)

# 发送 webhook
result = sender.send(
    url="https://example.com/webhook",
    data={"message": "Hello"},
    secret="your-secret"
)

if result['success']:
    print("发送成功")
else:
    print(f"发送失败: {result['error']}")
```

#### 批量发送

```python
urls = [
    "https://service1.com/webhook",
    "https://service2.com/webhook"
]

results = sender.send_batch(
    urls=urls,
    data={"message": "Batch message"},
    secret="secret"
)
```

#### 带重试的发送

```python
result = sender.send_with_retry(
    url="https://example.com/webhook",
    data={"message": "Important"},
    max_attempts=5
)
```

## 完整示例

### 示例1: 启动接收器

```python
from webhook_receiver import WebhookReceiver

receiver = WebhookReceiver(secret="my-secret")

def handle_notification(webhook_info):
    data = webhook_info.get('data', {})
    print(f"收到通知: {data.get('title')}")
    return {"processed": True}

receiver.register_handler('notification', handle_notification)
receiver.run(port=5000)
```

### 示例2: 发送 webhook

```python
from webhook_sender import WebhookSender

sender = WebhookSender()

result = sender.send(
    url="http://localhost:5000/webhook/notification",
    data={"title": "测试", "content": "这是一条测试消息"},
    secret="my-secret"
)
```

### 示例3: 接收并转发

```python
from webhook_receiver import WebhookReceiver
from webhook_sender import WebhookSender

receiver = WebhookReceiver()
sender = WebhookSender()

def forward_handler(webhook_info):
    # 接收到 webhook 后转发到其他服务
    result = sender.send(
        url="https://external-service.com/webhook",
        data=webhook_info.get('data', {})
    )
    return {"forwarded": result['success']}

receiver.register_handler('forward', forward_handler)
receiver.run()
```

## 错误处理

### 接收器错误处理

- 自动捕获所有异常
- 记录详细错误日志
- 返回友好的错误响应
- 密钥验证失败返回 401

### 发送器错误处理

- 网络超时处理
- 连接错误处理
- HTTP 错误状态码处理
- 自动重试机制
- 详细错误信息记录

## 日志记录

所有操作都会记录到：
- 控制台输出
- `webhook.log` 文件

日志包含：
- 请求/响应信息
- 错误详情
- 时间戳
- IP 地址

## 测试

### 运行示例

```bash
# 运行综合示例
python webhook_example.py

# 运行测试脚本
python webhook_test.py
```

### 手动测试接收器

1. 启动接收器：
```bash
python webhook_receiver.py
```

2. 在另一个终端测试：
```bash
python webhook_test.py
```

或使用 curl：
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: your-secret-key" \
  -d '{"test": "message"}'
```

## 配置选项

### 接收器配置

```python
receiver = WebhookReceiver(
    app_name="MyApp",      # Flask 应用名称
    secret="secret-key"    # 可选：webhook 密钥
)

receiver.run(
    host='0.0.0.0',        # 监听地址
    port=5000,             # 端口
    debug=False            # 调试模式
)
```

### 发送器配置

```python
sender = WebhookSender(
    timeout=10,            # 超时时间（秒）
    max_retries=3,         # 最大重试次数
    retry_backoff=1.0      # 重试退避时间（秒）
)
```

## 安全建议

1. **使用密钥验证**：设置 `secret` 参数保护你的 webhook 端点
2. **HTTPS**：生产环境使用 HTTPS
3. **IP 白名单**：在 Flask 层面添加 IP 白名单
4. **速率限制**：考虑添加速率限制防止滥用

## 文件说明

- `webhook_receiver.py` - Webhook 接收器核心代码
- `webhook_sender.py` - Webhook 发送器核心代码
- `webhook_example.py` - 综合使用示例
- `webhook_test.py` - 测试脚本
- `requirements.txt` - 依赖包列表

## 依赖包

- `flask>=3.0.0` - Web 框架
- `requests>=2.31.0` - HTTP 客户端
- `urllib3>=2.0.0` - HTTP 库

## 常见问题

### Q: 如何验证 webhook 请求？

A: 设置 `secret` 参数，请求需要在 Header 中包含 `X-Webhook-Secret` 或 `Authorization: Bearer <secret>`

### Q: 如何处理大量并发请求？

A: 使用生产级 WSGI 服务器如 Gunicorn：
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 webhook_receiver:receiver.app
```

### Q: 如何添加自定义验证逻辑？

A: 在处理器函数中添加验证逻辑，或修改 `_verify_secret` 方法

## 许可证

MIT License

