#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPIO API 接入示例 - Claude 模型调用
"""

import os
from openai import OpenAI

# PPIO API 配置
PPIO_API_KEY = os.getenv("PPIO_API_KEY", "your-api-key-here")  # 替换为你的 API Key
PPIO_BASE_URL = "https://api.ppinfra.com/v3/openai"  # PPIO API 地址

# 创建客户端
client = OpenAI(
    api_key=PPIO_API_KEY,
    base_url=PPIO_BASE_URL
)


def chat(messages, model="claude-3-5-sonnet-20241022", temperature=0.7, max_tokens=4096):
    """
    调用 PPIO Claude API

    Args:
        messages: 消息列表 [{"role": "user", "content": "你好"}]
        model: 模型名称
        temperature: 温度参数
        max_tokens: 最大输出 token

    Returns:
        模型回复内容
    """
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content


def chat_stream(messages, model="claude-3-5-sonnet-20241022", temperature=0.7, max_tokens=4096):
    """
    流式调用 PPIO Claude API
    """
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True
    )
    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


# 使用示例
if __name__ == "__main__":
    # 示例 1: 普通对话
    print("=" * 50)
    print("普通对话示例")
    print("=" * 50)

    messages = [
        {"role": "system", "content": "你是一个有帮助的助手。"},
        {"role": "user", "content": "用一句话介绍你自己"}
    ]

    response = chat(messages)
    print(f"回复: {response}")

    # 示例 2: 流式对话
    print("\n" + "=" * 50)
    print("流式对话示例")
    print("=" * 50)

    messages = [
        {"role": "user", "content": "写一首关于编程的短诗"}
    ]

    print("回复: ", end="", flush=True)
    for text in chat_stream(messages):
        print(text, end="", flush=True)
    print()
