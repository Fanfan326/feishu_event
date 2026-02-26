#!/bin/bash
# 词汇训练工具启动脚本

# 清除代理设置
unset ALL_PROXY
unset all_proxy
unset HTTP_PROXY
unset HTTPS_PROXY
unset http_proxy
unset https_proxy

# 设置 API Key
export PPIO_API_KEY="sk__6-1_QVbH5APf546zf7vlhFWtGmm3ktr1wZZ2T8KHX8"

echo "🎓 启动词汇训练工具..."
echo ""

# 运行程序
cd /Users/francinapeng/Public
python3 vocab_trainer.py
