#!/bin/bash
# 红线价格查询机器人 - 云服务器部署脚本

set -e

echo "=================================="
echo "红线价格查询机器人部署脚本"
echo "=================================="

# 配置
APP_DIR="/opt/price_bot"
SERVICE_NAME="price-bot"
PORT=8001

# 检查 root 权限
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用 root 权限运行: sudo bash deploy_price_bot.sh"
    exit 1
fi

echo "📦 1. 安装系统依赖..."
if command -v apt-get &> /dev/null; then
    # Ubuntu/Debian
    apt-get update
    apt-get install -y python3 python3-pip python3-venv nginx supervisor
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    yum install -y python3 python3-pip nginx supervisor
else
    echo "❌ 不支持的系统"
    exit 1
fi

echo "📁 2. 创建应用目录..."
mkdir -p $APP_DIR
cd $APP_DIR

echo "📝 3. 复制应用文件..."
# 这里需要你上传 price_bot.py 和 price_query.py 到服务器
# scp price_bot.py price_query.py user@server:/opt/price_bot/

echo "🐍 4. 创建 Python 虚拟环境..."
python3 -m venv venv
source venv/bin/activate

echo "📦 5. 安装 Python 依赖..."
pip install --upgrade pip
pip install fastapi uvicorn httpx openai

echo "⚙️  6. 创建配置文件..."
cat > $APP_DIR/.env << 'EOF'
# 飞书机器人配置
FEISHU_APP_ID=cli_xxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxx
FEISHU_VERIFICATION_TOKEN=xxxxxxxxxx

# CMDB API 配置
CMDB_API_URL=http://your-cmdb-api.com/api
CMDB_API_TOKEN=your-token-here

# PPIO API 配置
PPIO_API_KEY=your-ppio-key

# 服务配置
PORT=8001
HOST=0.0.0.0

# 测试模式
USE_MOCK_DATA=false
EOF

echo "⚠️  请编辑配置文件: nano $APP_DIR/.env"
echo ""
read -p "配置文件已编辑完成？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 请先编辑配置文件后重新运行"
    exit 1
fi

echo "🔧 7. 创建 Supervisor 配置..."
cat > /etc/supervisor/conf.d/price-bot.conf << EOF
[program:price-bot]
directory=$APP_DIR
command=$APP_DIR/venv/bin/python price_bot.py
user=root
autostart=true
autorestart=true
stderr_logfile=/var/log/price-bot.err.log
stdout_logfile=/var/log/price-bot.out.log
environment=PATH="$APP_DIR/venv/bin"
EOF

echo "🌐 8. 配置 Nginx 反向代理..."
cat > /etc/nginx/sites-available/price-bot << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/price-bot /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

echo "🔄 9. 重启服务..."
supervisorctl reread
supervisorctl update
supervisorctl restart price-bot

nginx -t && systemctl restart nginx

echo "✅ 部署完成！"
echo ""
echo "=================================="
echo "服务信息"
echo "=================================="
echo "应用目录: $APP_DIR"
echo "Webhook URL: http://your-server-ip/webhook"
echo "健康检查: http://your-server-ip/health"
echo ""
echo "日志查看:"
echo "  tail -f /var/log/price-bot.out.log"
echo "  tail -f /var/log/price-bot.err.log"
echo ""
echo "服务管理:"
echo "  supervisorctl status price-bot"
echo "  supervisorctl restart price-bot"
echo "  supervisorctl stop price-bot"
echo "=================================="
