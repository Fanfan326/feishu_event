# 红线价格查询机器人 - 配置指南

## 配置清单

### ☑️ 第一步：创建飞书应用（10分钟）

1. **访问飞书开放平台**
   ```
   https://open.feishu.cn/app
   ```

2. **创建应用**
   - 点击"创建企业自建应用"
   - 应用名称：红线价格查询机器人
   - 上传图标（可选）

3. **启用机器人**
   - 应用功能 → 机器人 → 启用

4. **配置权限**
   - 权限管理 → 勾选以下权限：
     - ✅ 获取与发送单聊、群组消息
     - ✅ 读取用户发给机器人的单聊消息
     - ✅ 获取群组信息

5. **获取凭证**
   - 凭证与基础信息 → 复制：
     - `App ID`: cli_xxxxxxxxxx
     - `App Secret`: xxxxxxxxxx

6. **记录这些信息**（等会要用）
   ```
   FEISHU_APP_ID=cli_xxxxxxxxxx
   FEISHU_APP_SECRET=xxxxxxxxxx
   ```

---

### ☑️ 第二步：配置 CMDB API

请提供以下信息：

1. **API 基础地址**
   ```
   http://your-cmdb-api.com/api
   ```

2. **认证 Token**
   ```
   Bearer YOUR_TOKEN
   ```

3. **价格查询接口**
   - 路径：`/pricing/baseline` 或其他
   - 方法：GET
   - 参数：`gpu_type` (可选)

4. **返回格式示例**
   请提供一个实际的 API 返回 JSON，例如：
   ```json
   {
     "prices": [
       {
         "gpu_model": "A100-80GB",
         "price_per_hour": 2.50,
         "currency": "USD",
         "region": "国内"
       }
     ]
   }
   ```

---

### ☑️ 第三步：部署到云服务器

#### 方式1：使用部署脚本（推荐）

1. **上传文件到服务器**
   ```bash
   scp price_bot.py price_query.py deploy_price_bot.sh root@your-server:/tmp/
   ```

2. **连接服务器**
   ```bash
   ssh root@your-server
   ```

3. **运行部署脚本**
   ```bash
   cd /tmp
   chmod +x deploy_price_bot.sh
   sudo bash deploy_price_bot.sh
   ```

4. **编辑配置文件**
   脚本会提示你编辑 `/opt/price_bot/.env`，填入：
   - 飞书 App ID 和 Secret
   - CMDB API 地址和 Token
   - PPIO API Key

5. **完成**
   脚本会自动：
   - 安装依赖
   - 配置 Supervisor（自动重启）
   - 配置 Nginx（反向代理）
   - 启动服务

#### 方式2：手动部署

```bash
# 1. 创建目录
mkdir -p /opt/price_bot
cd /opt/price_bot

# 2. 上传文件
# 上传 price_bot.py, price_query.py 到此目录

# 3. 安装依赖
pip3 install fastapi uvicorn httpx openai

# 4. 创建配置文件
cat > .env << EOF
FEISHU_APP_ID=cli_xxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxx
CMDB_API_URL=http://your-cmdb-api.com/api
CMDB_API_TOKEN=your-token
PPIO_API_KEY=your-ppio-key
USE_MOCK_DATA=false
EOF

# 5. 启动服务（后台运行）
nohup python3 price_bot.py > bot.log 2>&1 &

# 6. 查看日志
tail -f bot.log
```

---

### ☑️ 第四步：配置飞书事件订阅

1. **获取服务器公网地址**
   ```
   http://your-server-ip/webhook
   ```

2. **返回飞书开放平台**
   - 应用管理 → 事件订阅
   - 请求地址配置：`http://your-server-ip/webhook`
   - 加密策略：可不配置（建议配置）

3. **订阅事件**
   - 添加事件：`im.message.receive_v1`
   - 保存

4. **发布应用**
   - 应用发布 → 创建版本
   - 申请发布（内部应用无需审核）

---

### ☑️ 第五步：测试机器人

1. **在飞书中添加机器人**
   - 打开飞书
   - 搜索"红线价格查询机器人"
   - 添加到群聊或单聊

2. **测试基本功能**
   ```
   @红线价格机器人 帮助
   @红线价格机器人 A100红线价格
   @红线价格机器人 红线价格列表
   ```

3. **查看日志**
   ```bash
   # Supervisor 日志
   tail -f /var/log/price-bot.out.log

   # 或手动运行的日志
   tail -f /opt/price_bot/bot.log
   ```

---

## 常见问题

### Q1: 机器人收不到消息？
- 检查事件订阅 URL 是否正确
- 确认服务器防火墙开放了 80 端口
- 查看服务器日志是否有收到请求

### Q2: 价格查询失败？
- 检查 CMDB_API_URL 是否正确
- 验证 CMDB_API_TOKEN 是否有效
- 先设置 `USE_MOCK_DATA=true` 测试

### Q3: 服务启动失败？
```bash
# 查看详细错误
supervisorctl tail -f price-bot stderr

# 或手动启动查看错误
cd /opt/price_bot
source venv/bin/activate
python price_bot.py
```

---

## 下一步

配置完成后：
1. ✅ 机器人能响应消息
2. ✅ 能查询红线价格
3. ✅ 服务自动重启

现在需要你提供：
- 飞书 App ID 和 App Secret
- CMDB API 地址和返回格式

我来帮你完成剩余配置！
