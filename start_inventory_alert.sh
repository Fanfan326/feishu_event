#!/bin/bash
# GPU库存监控启动脚本

cd "$(dirname "$0")"

echo "================================"
echo "GPU库存监控系统"
echo "================================"
echo ""
echo "选择运行模式："
echo "  1) 立即检查一次库存"
echo "  2) 定时监控（每天自动检查）"
echo "  3) 后台运行（nohup方式）"
echo ""
read -p "请选择 [1-3]: " choice

case $choice in
    1)
        echo "立即检查库存..."
        python3 inventory_alert.py --check
        ;;
    2)
        echo "启动定时监控..."
        python3 inventory_alert.py --schedule
        ;;
    3)
        echo "启动后台监控..."
        nohup python3 inventory_alert.py --schedule > inventory_alert.log 2>&1 &
        echo "✅ 已在后台启动，日志文件: inventory_alert.log"
        echo "查看日志: tail -f inventory_alert.log"
        echo "停止监控: pkill -f inventory_alert.py"
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac
