#!/bin/bash
# 启动飞书事件监听服务并配置ngrok

cd "$(dirname "$0")"

echo "============================================================"
echo "启动飞书事件监听服务 + ngrok"
echo "============================================================"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 python3，请先安装 Python 3"
    exit 1
fi

# 检查ngrok
if ! command -v ngrok &> /dev/null; then
    echo "❌ 未找到 ngrok，请先安装: brew install ngrok/ngrok/ngrok"
    exit 1
fi

# 检查依赖
echo "检查依赖..."
python3 -c "import flask, httpx, Instance" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  缺少依赖，正在安装..."
    pip3 install -r requirements.txt
fi

echo ""
echo "启动飞书事件监听服务..."
python3 feishu_event_handler.py &
FEISHU_PID=$!
echo "服务PID: $FEISHU_PID"

# 等待服务启动
sleep 3

# 检查服务是否启动成功
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ 服务启动成功"
else
    echo "❌ 服务启动失败"
    kill $FEISHU_PID 2>/dev/null
    exit 1
fi

echo ""
echo "启动 ngrok..."
ngrok http 5000 &
NGROK_PID=$!
echo "ngrok PID: $NGROK_PID"

# 等待ngrok启动
sleep 5

# 获取ngrok URL
echo ""
echo "============================================================"
echo "获取 ngrok 公网URL..."
echo "============================================================"

NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tunnels = data.get('tunnels', [])
    for tunnel in tunnels:
        if tunnel.get('proto') == 'https':
            print(tunnel.get('public_url', ''))
            break
except:
    pass
" 2>/dev/null)

if [ -n "$NGROK_URL" ]; then
    echo ""
    echo "✅ ngrok 公网URL: $NGROK_URL"
    echo ""
    echo "============================================================"
    echo "配置步骤："
    echo "============================================================"
    echo "1. 登录飞书开放平台: https://open.feishu.cn/"
    echo "2. 进入应用（APP_ID: cli_a62d008d262c100c）"
    echo "3. 进入「事件订阅」页面"
    echo "4. 配置请求地址URL: $NGROK_URL/feishu/event"
    echo "5. 订阅事件: im.message.receive_v1"
    echo "6. 保存配置"
    echo ""
    echo "============================================================"
    echo "测试："
    echo "============================================================"
    echo "在飞书群里@机器人，例如："
    echo "  @机器人 同步数据"
    echo ""
    echo "============================================================"
    echo "按 Ctrl+C 停止服务"
    echo "============================================================"
else
    echo ""
    echo "⚠️  无法获取ngrok URL，请手动访问 http://localhost:4040 查看"
fi

# 等待用户中断
trap "echo ''; echo '正在停止服务...'; kill $FEISHU_PID $NGROK_PID 2>/dev/null; exit" INT TERM

# 保持运行
wait


