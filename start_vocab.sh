#!/bin/bash
# 词汇训练工具启动脚本

# 设置 API Key（请替换为你的真实 Key）
export PPIO_API_KEY="${PPIO_API_KEY:-your-ppio-key-here}"

# 启动程序
cd /Users/francinapeng/Public
python3 vocab_trainer.py
