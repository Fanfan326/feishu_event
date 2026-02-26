# 飞书 Webhook 工具

这是一个用于向飞书群聊发送消息的 Python 工具包。

## 安装

```bash
pip install -r requirements.txt
```

## 获取 Webhook URL

1. 在飞书群聊中，点击右上角的设置图标
2. 选择"群机器人" → "添加机器人" → "自定义机器人"
3. 设置机器人名称和头像
4. 创建后复制 Webhook URL

## 快速开始

### 方式一：使用示例脚本

1. 编辑 `feishu_webhook_example.py`，将 `WEBHOOK_URL` 替换为你的 Webhook URL
2. 运行示例：
```bash
python feishu_webhook_example.py
```

### 方式二：在代码中使用

```python
from feishu_webhook import FeishuWebhook

# 初始化
webhook = FeishuWebhook("你的 Webhook URL")

# 发送文本消息
webhook.send_text("这是一条测试消息")

# 发送 Markdown 消息
webhook.send_markdown("标题", "**加粗文本**\n普通文本")

# 发送卡片消息
webhook.send_card(
    title="通知",
    content="这是一条重要通知",
    button_text="查看详情",
    button_url="https://example.com"
)
```

## 功能说明

### 1. 发送纯文本消息
最简单的方式，适合发送普通通知。

```python
webhook.send_text("系统运行正常")
```

### 2. 发送 Markdown 消息
支持 Markdown 格式，适合发送格式化的内容。

**换行说明：**
- 单行换行：使用 `\n`
- 段落分隔：使用 `\n\n`（两个换行符）
- 也可以使用三引号字符串，自动保留换行

```python
# 方式1: 使用 \n 显式换行
webhook.send_markdown("报告", "**重要**\n- 项目1\n- 项目2")

# 方式2: 使用三引号字符串（推荐，更易读）
content = """**重要**

- 项目1
- 项目2"""
webhook.send_markdown("报告", content)
```

### 3. 发送卡片消息
支持标题、内容和可选按钮，适合发送结构化通知。

```python
webhook.send_card(
    title="任务完成",
    content="任务已成功完成",
    button_text="查看详情",  # 可选
    button_url="https://example.com"  # 可选
)
```

## 示例场景

### 系统监控告警
```python
webhook.send_card(
    title="系统告警",
    content="**CPU使用率过高**\n当前: 95%\n阈值: 80%",
    button_text="查看监控",
    button_url="https://monitor.example.com"
)
```

### 任务完成通知
```python
webhook.send_text("✅ 数据处理任务已完成\n处理记录数: 1000条")
```

### 每日报告
```python
# 使用 \n 进行换行
webhook.send_markdown(
    "每日数据报告",
    "**今日统计**\n\n- 访问量: 10,234\n- 新用户: 156"
)

# 或使用三引号字符串
content = """**今日统计**

- 访问量: 10,234
- 新用户: 156"""
webhook.send_markdown("每日数据报告", content)
```

## 注意事项

- Webhook URL 请妥善保管，不要泄露
- 飞书对消息发送频率有限制，请避免频繁发送
- 消息内容支持 UTF-8 编码，可以发送中文

## Markdown 换行示例

查看 `feishu_markdown_example.py` 了解详细的换行使用方法，包括：
- 单行换行
- 段落换行
- 混合格式
- 代码块
- 表格
- 实际使用场景

## 文件说明

- `feishu_webhook.py` - 核心工具类
- `feishu_webhook_example.py` - 使用示例
- `feishu_markdown_example.py` - Markdown 换行详细示例
- `requirements.txt` - 依赖包列表

