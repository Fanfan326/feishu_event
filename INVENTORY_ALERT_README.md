# GPU库存监控和采购提醒系统

## 功能说明

当GPU库存低于设定阈值时，自动通过飞书私聊发送采购提醒。

## 配置步骤

### 1. 获取飞书用户ID

有两种方式获取飞书用户ID：

**方式一：通过飞书管理后台**
- 登录飞书管理后台
- 进入 "通讯录" → 找到要接收通知的用户
- 查看用户详情，获取 `user_id` 或 `open_id`

**方式二：让机器人帮你查询**
- 在飞书群里@机器人，发送 `/userid`
- 机器人会回复你的 user_id

### 2. 编辑配置文件

编辑 `inventory_alert_config.json`：

```json
{
  "gpu_thresholds": {
    "4090": {
      "min_free": 100,
      "description": "RTX 4090"
    },
    "H100": {
      "min_free": 20,
      "description": "H100"
    }
  },
  "notification": {
    "user_ids": ["替换为实际的用户ID"],
    "check_time": "10:00"
  }
}
```

**说明：**
- `min_free`: 空闲卡数低于此值时触发告警
- `user_ids`: 接收通知的用户ID列表（可以填多个）
- `check_time`: 每天检查的时间（格式：HH:MM）

### 3. 调整阈值

根据实际需求修改各GPU类型的 `min_free` 值：

```json
"4090": {"min_free": 100},   // 4090空闲卡少于100张时提醒
"H100": {"min_free": 20},    // H100空闲卡少于20张时提醒
"A100": {"min_free": 30}     // A100空闲卡少于30张时提醒
```

## 使用方法

### 方式一：使用启动脚本（推荐）

```bash
./start_inventory_alert.sh
```

然后选择：
1. 立即检查一次库存
2. 定时监控（前台运行）
3. 后台运行

### 方式二：直接运行Python脚本

**立即检查一次：**
```bash
python3 inventory_alert.py --check
```

**定时监控（前台）：**
```bash
python3 inventory_alert.py --schedule
```

**后台运行：**
```bash
nohup python3 inventory_alert.py --schedule > inventory_alert.log 2>&1 &
```

## 查看日志

```bash
tail -f inventory_alert.log
```

## 停止监控

```bash
pkill -f inventory_alert.py
```

## 提醒机制

- ✅ 避免重复提醒：同一GPU类型在24小时内只提醒一次
- ✅ 自动记录：提醒历史保存在 `.inventory_alert_history.json`
- ✅ 支持多人：可以同时给多个用户发送提醒

## 消息格式示例

```
⚠️ GPU库存预警

发现以下GPU库存不足，建议尽快发起采购：

🔴 RTX 4090 (4090)
   - 当前空闲：85 张
   - 安全库存：100 张
   - 建议采购：15 张以上

🔴 H100 (H100)
   - 当前空闲：12 张
   - 安全库存：20 张
   - 建议采购：8 张以上

📅 检查时间：2026-02-26 10:00:00
```

## 故障排查

### 1. 无法发送消息

检查 `.env` 文件中的配置：
```bash
FEISHU_APP_ID=xxx
FEISHU_APP_SECRET=xxx
```

### 2. 用户ID错误

- 确认使用的是正确的 `user_id` 或 `open_id`
- 确认机器人有权限给该用户发送消息

### 3. 库存数据查询失败

- 检查 Grafana API 配置是否正确
- 确认网络连接正常

## 技术架构

```
┌─────────────────────────────────────┐
│  inventory_alert.py                 │
│  (监控脚本)                          │
└──────────┬──────────────────────────┘
           │
           ├─ 读取配置 → inventory_alert_config.json
           │
           ├─ 查询库存 → gpu_inventory.py → Grafana API
           │
           ├─ 检查阈值 → 判断是否需要提醒
           │
           ├─ 发送消息 → 飞书API (私聊)
           │
           └─ 记录历史 → .inventory_alert_history.json
```

## 定时任务（可选）

如果想让系统开机自动运行，可以添加到 crontab：

```bash
# 编辑 crontab
crontab -e

# 添加一行（每天10点运行）
0 10 * * * cd /Users/francinapeng/Public && python3 inventory_alert.py --check
```

或使用 launchd（macOS）或 systemd（Linux）服务。
