# 飞书机器人@消息自动同步Grafana数据配置指南

## 功能说明

当飞书群里的机器人被@（艾特）时，自动同步Grafana数据并发送到飞书群。

## 配置步骤

### 1. 启动事件监听服务

```bash
python3 feishu_event_handler.py
```

服务会在 `http://0.0.0.0:5000` 启动，监听飞书事件回调。

### 2. 配置公网访问（重要）

由于飞书需要回调你的服务器，你需要：

**选项A：使用内网穿透工具（推荐用于测试）**
- 使用 ngrok: `ngrok http 5000`
- 使用 frp 或其他内网穿透工具
- 获取公网URL，例如：`https://your-domain.ngrok.io`

**选项B：部署到公网服务器**
- 将服务部署到有公网IP的服务器
- 确保防火墙开放5000端口

### 3. 在飞书开放平台配置事件订阅

1. 登录 [飞书开放平台](https://open.feishu.cn/)
2. 进入你的应用（APP_ID: `cli_a62d008d262c100c`）
3. 进入「事件订阅」页面
4. 配置以下内容：

   **请求地址URL：**
   ```
   http://your-public-domain:5000/feishu/event
   ```
   或
   ```
   https://your-domain.ngrok.io/feishu/event
   ```

   **订阅事件：**
   - `im.message.receive_v1` - 接收消息事件

5. 保存配置

### 4. 验证配置

配置完成后，飞书会发送一个验证请求到你的服务器。如果配置正确，服务器会自动响应验证。

### 5. 测试功能

在飞书群里@机器人，例如：
```
@机器人 同步数据
```

机器人会自动：
1. 检测到被@
2. 获取Grafana数据
3. 发送包含截图和数据的消息到群聊

## 配置说明

### 环境变量（可选）

如果需要配置加密密钥，可以在代码中设置：

```python
ENCRYPT_KEY = "your-encrypt-key"  # 从飞书开放平台获取
VERIFICATION_TOKEN = "your-token"  # 从飞书开放平台获取
```

### 日志文件

- 事件日志：`./feishu_event.log`
- Instance日志：`./feishu_sla_report.log`

## 故障排查

### 1. 收不到事件回调

- 检查服务器是否可公网访问
- 检查防火墙是否开放5000端口
- 检查飞书开放平台的事件订阅配置是否正确
- 查看日志文件：`./feishu_event.log`

### 2. @机器人没有反应

- 检查日志文件，查看是否收到事件
- 确认事件类型是否为 `im.message.receive_v1`
- 检查@检测逻辑是否正确

### 3. 签名验证失败

- 如果配置了加密密钥，确保 `ENCRYPT_KEY` 正确
- 检查飞书开放平台的加密密钥配置

## 运行方式

### 开发模式

```bash
python3 feishu_event_handler.py
```

### 生产模式（使用gunicorn）

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 feishu_event_handler:app
```

### 后台运行（使用nohup）

```bash
nohup python3 feishu_event_handler.py > feishu_event.log 2>&1 &
```

## 注意事项

1. 确保服务器可以访问Grafana（需要网络连通）
2. 确保飞书API密钥有效
3. 建议使用HTTPS（可以通过nginx反向代理）
4. 定期检查日志文件，确保服务正常运行

