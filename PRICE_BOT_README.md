# 红线价格查询机器人

专门用于查询GPU红线价格（内部定价参考）的飞书机器人。

## 功能特性

- ✅ 关键词匹配查询（如："A100红线价格"）
- ✅ 菜单展示所有价格（如："红线价格列表"）
- ✅ 智能理解用户问题（如："H100多少钱一小时"）
- ✅ 从 CMDB API 获取实时价格数据
- ✅ 支持模拟数据测试模式

## 快速开始

### 1. 安装依赖

```bash
cd /Users/francinapeng/Public
pip install fastapi uvicorn httpx openai
```

### 2. 配置环境变量

复制配置文件并修改：

```bash
cp .env.price_bot .env
```

编辑 `.env` 文件，填入你的配置：

```bash
# 飞书机器人配置（在飞书开放平台创建应用获取）
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
FEISHU_VERIFICATION_TOKEN=xxx

# CMDB API 配置（稍后提供）
CMDB_API_URL=http://your-cmdb-api.com/api
CMDB_API_TOKEN=your-token

# PPIO API 配置
PPIO_API_KEY=your-ppio-key

# 测试模式（先用模拟数据）
USE_MOCK_DATA=true
```

### 3. 启动机器人

```bash
# 加载环境变量
export $(cat .env | xargs)

# 启动服务
python price_bot.py
```

服务将在 `http://0.0.0.0:8001` 启动。

### 4. 配置飞书机器人

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 配置机器人权限：
   - 获取与发送单聊、群组消息
   - 读取用户发给机器人的单聊消息
   - 获取群组信息
4. 配置事件订阅：
   - 事件 URL: `http://your-server:8001/webhook`
   - 订阅事件: `im.message.receive_v1`

## 使用方法

在飞书中@机器人：

### 查询单个GPU价格
```
@红线价格机器人 A100红线价格
@红线价格机器人 H100多少钱
@红线价格机器人 4090的价格
```

### 查询所有价格
```
@红线价格机器人 红线价格列表
@红线价格机器人 所有GPU的价格
```

### 智能提问
```
@红线价格机器人 H100一小时多少钱
@红线价格机器人 A100的红线价格是多少
```

### 获取帮助
```
@红线价格机器人 帮助
@红线价格机器人 help
```

## 支持的GPU型号

- NVIDIA A系列：A100, A6000, A800
- NVIDIA H系列：H100, H200, H20
- NVIDIA L系列：L40, L40S
- NVIDIA RTX系列：RTX 4090, RTX 3090, RTX 5090
- NVIDIA V系列：V100

## 文件说明

- `price_bot.py` - 机器人主程序
- `price_query.py` - 价格查询模块
- `.env.price_bot` - 配置模板
- `PRICE_BOT_README.md` - 本文档

## CMDB API 接口规范

机器人需要 CMDB 提供以下 API：

### 查询价格接口

**端点**: `GET /pricing/baseline`

**参数**:
- `gpu_type` (可选): GPU型号，如 "A100", "H100"

**返回格式**:
```json
{
  "prices": [
    {
      "gpu_model": "A100-80GB",
      "price_per_hour": 2.50,
      "price_per_day": 50.00,
      "currency": "USD",
      "region": "国内",
      "update_time": "2024-01-15"
    }
  ]
}
```

**认证方式**: Bearer Token

```bash
Authorization: Bearer YOUR_TOKEN
```

## 测试

### 本地测试（使用模拟数据）

```bash
# 设置测试模式
export USE_MOCK_DATA=true

# 测试价格查询模块
python price_query.py
```

### 测试机器人

```bash
# 启动机器人
python price_bot.py

# 健康检查
curl http://localhost:8001/health
```

## 日志

日志会输出到控制台，包含：
- 收到的消息
- 价格查询结果
- API 调用状态
- 错误信息

## 故障排查

### 机器人收不到消息
- 检查飞书应用的事件订阅配置
- 确认 Webhook URL 可以从外网访问
- 查看机器人日志

### 价格查询失败
- 检查 CMDB API 配置是否正确
- 验证 API Token 是否有效
- 先使用 `USE_MOCK_DATA=true` 测试

### PPIO API 调用失败
- 检查 PPIO_API_KEY 是否正确
- 查看网络连接是否正常

## 后续扩展

- [ ] 支持价格对比（不同地区、不同时间）
- [ ] 价格趋势图表
- [ ] 价格预警功能
- [ ] 导出价格表格

## 联系方式

有问题请联系价格管理团队。
