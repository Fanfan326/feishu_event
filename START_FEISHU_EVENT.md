# 启动飞书@机器人自动同步Grafana功能

## 功能说明

当在飞书群里@机器人时，会自动：
1. 检测到@消息
2. 获取Grafana数据（截图 + 数据）
3. 发送消息到飞书群

## 快速启动步骤

### 1. 启动事件监听服务

```bash
python3 feishu_event_handler.py
```

服务会在 `http://0.0.0.0:5000` 启动

### 2. 配置公网访问（重要！）

飞书需要回调你的服务器，所以需要公网可访问的地址。

**使用 ngrok（推荐用于测试）：**

```bash
# 在另一个终端运行
ngrok http 5000
```

会得到一个公网URL，例如：`https://xxxx.ngrok.io`

### 3. 在飞书开放平台配置事件订阅

1. 登录 [飞书开放平台](https://open.feishu.cn/)
2. 进入你的应用（APP_ID: `cli_a62d008d262c100c`）
3. 进入「事件订阅」页面
4. 配置：
   - **请求地址URL**: `https://xxxx.ngrok.io/feishu/event`
   - **订阅事件**: ✅ `im.message.receive_v1`（接收消息事件）
5. 点击「保存」，飞书会自动发送验证请求
6. 如果配置正确，会显示「验证成功」

### 4. 测试功能

在飞书群里@机器人：
```
@机器人 同步数据
```

机器人会自动：
- ✅ 检测到被@
- ✅ 获取Grafana数据
- ✅ 发送包含截图和数据的消息到群聊

## 验证服务是否正常运行

### 检查健康状态

```bash
curl http://localhost:5000/health
```

### 查看日志

```bash
tail -f feishu_event.log
```

## 常见问题

### Q: 收不到事件回调？

A: 检查：
1. 服务器是否可公网访问
2. ngrok是否正常运行
3. 飞书开放平台的事件订阅配置是否正确
4. 查看日志文件：`./feishu_event.log`

### Q: @机器人没有反应？

A: 检查：
1. 日志文件，查看是否收到事件
2. 确认事件类型是否为 `im.message.receive_v1`
3. 检查@检测逻辑（查看日志中的"检测到机器人被@"消息）

## 后台运行

```bash
# 使用 nohup
nohup python3 feishu_event_handler.py > feishu_event.log 2>&1 &

# 或使用 screen
screen -S feishu_event
python3 feishu_event_handler.py
# 按 Ctrl+A 然后 D 退出screen
```

## 注意事项

1. ✅ 确保服务器可以访问Grafana
2. ✅ 确保飞书API密钥有效（APP_ID 和 APP_SECRET）
3. ✅ 建议使用HTTPS（可以通过nginx反向代理）
4. ✅ 定期检查日志文件，确保服务正常运行

