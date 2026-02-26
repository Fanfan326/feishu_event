#!/bin/bash
# 启动飞书事件监听服务

cd "$(dirname "$0")"

echo "============================================================"
echo "启动飞书事件监听服务"
echo "============================================================"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 python3，请先安装 Python 3"
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
echo "启动服务..."
echo "服务地址: http://0.0.0.0:5000"
echo "事件回调端点: http://your-domain:5000/feishu/event"
echo ""
echo "按 Ctrl+C 停止服务"
echo "============================================================"
echo ""

# 启动服务
python3 feishu_event_handler.py

