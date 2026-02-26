# 飞书机器人@消息自动同步 - 快速开始

## 功能说明

当飞书群里的机器人被@时，自动同步Grafana数据并发送到飞书群。

## 快速启动

### 方式1：使用启动脚本（推荐）

```bash
./start_feishu_event.sh
```

### 方式2：直接运行

```bash
python3 feishu_event_handler.py
```

服务会在 `http://0.0.0.0:5000` 启动

## 配置步骤

### 1. 配置公网访问

飞书需要回调你的服务器，所以需要公网可访问的地址。

**选项A：使用 ngrok（推荐用于测试）**

1. 安装 ngrok: https://ngrok.com/download
2. 启动服务：
   ```bash
   python3 feishu_event_handler.py
   ```
3. 在另一个终端运行：
   ```bash
   ngrok http 5000
   ```
4. 复制 ngrok 提供的 HTTPS URL，例如：`https://xxxx.ngrok.io`

**选项B：部署到公网服务器**

- 将服务部署到有公网IP的服务器
- 确保防火墙开放5000端口
- 建议使用 nginx 反向代理并配置 HTTPS

### 2. 在飞书开放平台配置事件订阅

1. 登录 [飞书开放平台](https://open.feishu.cn/)
2. 进入你的应用（APP_ID: `cli_a62d008d262c100c`）
3. 进入「事件订阅」页面
4. 配置以下内容：

   **请求地址URL：**
   ```
   https://your-domain.ngrok.io/feishu/event
   ```
   或
   ```
   http://your-server-ip:5000/feishu/event
   ```

   **订阅事件：**
   - ✅ `im.message.receive_v1` - 接收消息事件

5. 点击「保存」，飞书会自动发送验证请求
6. 如果配置正确，会显示「验证成功」

### 3. 测试功能

1. 在飞书群里@机器人，例如：
   ```
   @机器人 同步数据
   ```
   或
   ```
   @机器人
   ```

2. 机器人会自动：
   - 检测到被@
   - 获取Grafana数据（截图 + 数据）
   - 发送消息到群聊

## 验证服务是否正常运行

### 检查健康状态

```bash
curl http://localhost:5000/health
```

应该返回：
```json
{
  "status": "healthy",
  "timestamp": "2025-12-25T16:00:00",
  "service": "feishu_event_handler"
}
```

### 查看日志

```bash
tail -f feishu_event.log
```

## 常见问题

### Q: 收不到事件回调？

A: 检查以下几点：
1. 服务器是否可公网访问
2. 防火墙是否开放5000端口
3. 飞书开放平台的事件订阅配置是否正确
4. 查看日志文件：`./feishu_event.log`

### Q: @机器人没有反应？

A: 检查：
1. 日志文件，查看是否收到事件
2. 确认事件类型是否为 `im.message.receive_v1`
3. 检查@检测逻辑（查看日志中的"检测到机器人被@"消息）

### Q: 如何后台运行？

A: 使用 nohup：
```bash
nohup python3 feishu_event_handler.py > feishu_event.log 2>&1 &
```

或使用 screen：
```bash
screen -S feishu_event
python3 feishu_event_handler.py
# 按 Ctrl+A 然后 D 退出screen
```

## 服务端点说明

- `POST /feishu/event` - 飞书事件回调端点（飞书会调用这个）
- `GET /health` - 健康检查端点
- `GET /` - 服务信息端点

## 注意事项

1. ✅ 确保服务器可以访问Grafana
2. ✅ 确保飞书API密钥有效（APP_ID 和 APP_SECRET）
3. ✅ 建议使用HTTPS（可以通过nginx反向代理）
4. ✅ 定期检查日志文件，确保服务正常运行

## 下一步

配置完成后，在飞书群里@机器人即可自动同步Grafana数据！

