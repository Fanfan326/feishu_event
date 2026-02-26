# 飞书 Webhook 故障排除指南

## 常见错误：incoming webhook access token invalid

### 错误原因

这个错误通常表示：
1. **Webhook URL 不正确** - URL 可能被复制错误或格式不正确
2. **Webhook URL 已过期** - 机器人可能被删除或重新创建
3. **Webhook URL 被撤销** - 群管理员可能撤销了机器人
4. **URL 格式错误** - URL 可能缺少部分内容

### 解决方案

#### 1. 检查 Webhook URL 格式

正确的飞书 Webhook URL 格式应该是：
```
https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

或者（国际版）：
```
https://open.larkoffice.com/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**检查要点：**
- ✅ 必须以 `https://` 开头
- ✅ 包含 `open.feishu.cn` 或 `larkoffice.com`
- ✅ 包含 `/hook/` 路径
- ✅ 末尾有长字符串（UUID格式）

#### 2. 重新获取 Webhook URL

**步骤：**
1. 打开飞书群聊
2. 点击右上角 **设置** 图标
3. 选择 **群机器人** → **添加机器人** → **自定义机器人**
4. 设置机器人名称和头像
5. 创建后，**完整复制** Webhook URL
6. 确保复制时没有遗漏任何字符

#### 3. 验证 Webhook URL 是否有效

使用测试功能验证：
```python
from feishu_webhook import FeishuWebhook

webhook = FeishuWebhook("your-webhook-url")
webhook.test_connection()
```

或者运行 `test.py` 时选择测试连接。

#### 4. 检查机器人状态

在飞书群聊中：
- 确认机器人是否还在群中
- 检查机器人是否被禁用
- 确认是否有权限发送消息

### 其他常见错误

#### 错误：请求失败 / 网络错误

**可能原因：**
- 网络连接问题
- 防火墙阻止
- 代理设置问题

**解决方案：**
1. 检查网络连接
2. 检查防火墙设置
3. 如果在公司网络，联系 IT 部门

#### 错误：消息发送频率过高

**可能原因：**
- 短时间内发送了太多消息

**解决方案：**
- 降低发送频率
- 合并多条消息为一条发送

### 调试技巧

#### 1. 启用详细日志

代码已经包含详细的错误信息，查看：
- 错误代码
- 错误消息
- 建议的解决方案

#### 2. 使用测试消息

先发送简单的测试消息：
```python
webhook.send_text("测试")
```

如果测试消息成功，说明连接正常，问题可能在消息格式。

#### 3. 检查消息内容

- 确保消息内容不为空
- 检查特殊字符是否导致问题
- 尝试发送纯文本消息测试

### 获取帮助

如果以上方法都无法解决问题：

1. **检查飞书官方文档**
   - 飞书开放平台：https://open.feishu.cn/

2. **验证 Webhook URL**
   - 在浏览器中访问 Webhook URL（会返回错误，但可以验证 URL 是否可访问）

3. **重新创建机器人**
   - 删除旧机器人
   - 创建新机器人
   - 获取新的 Webhook URL

### 预防措施

1. **保存 Webhook URL**
   - 将有效的 Webhook URL 保存在安全的地方
   - 不要分享给未授权的人

2. **定期测试**
   - 定期测试 Webhook 连接
   - 及时发现 URL 失效问题

3. **使用环境变量**
   - 将 Webhook URL 存储在环境变量中
   - 避免硬编码在代码中







