#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
红线价格查询模块
从 CMDB API 获取红线价格（内部定价参考），供业务方定价使用
"""

import httpx
import json
import logging
from typing import Optional, Dict, List
from openai import OpenAI
import os

logger = logging.getLogger(__name__)

# CMDB API 配置
CMDB_API_URL = os.getenv("CMDB_API_URL", "http://your-cmdb-api.com/api")
CMDB_API_TOKEN = os.getenv("CMDB_API_TOKEN", "your-token-here")

# PPIO API 配置 - 用于智能理解
PPIO_API_KEY = os.getenv("PPIO_API_KEY", "your-ppio-key")
PPIO_BASE_URL = "https://api.ppinfra.com/v3/openai"

# 创建 PPIO 客户端用于智能理解
ppio_client = OpenAI(
    api_key=PPIO_API_KEY,
    base_url=PPIO_BASE_URL
)


async def fetch_price_from_cmdb(gpu_type: Optional[str] = None) -> Dict:
    """
    从 CMDB API 获取红线价格

    Args:
        gpu_type: GPU 型号，如 "A100", "H100", "4090"。为空则返回所有价格

    Returns:
        {
            "success": True/False,
            "data": [
                {
                    "gpu_model": "A100-80GB",
                    "price_per_hour": 2.50,
                    "price_per_day": 50.00,
                    "currency": "USD",
                    "region": "国内/海外",
                    "update_time": "2024-01-15"
                }
            ],
            "error": "错误信息"
        }
    """
    try:
        # 构建请求
        url = f"{CMDB_API_URL}/pricing/baseline"
        headers = {
            "Authorization": f"Bearer {CMDB_API_TOKEN}",
            "Content-Type": "application/json"
        }

        params = {}
        if gpu_type:
            params["gpu_type"] = gpu_type

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "data": data.get("prices", []),
                    "error": None
                }
            else:
                logger.error(f"CMDB API 返回错误: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "data": [],
                    "error": f"API 错误: {response.status_code}"
                }

    except Exception as e:
        logger.error(f"查询价格失败: {str(e)}")
        return {
            "success": False,
            "data": [],
            "error": str(e)
        }


def format_price_message(price_data: List[Dict], gpu_type: Optional[str] = None) -> str:
    """
    格式化价格信息为飞书消息

    Args:
        price_data: 价格数据列表
        gpu_type: GPU 型号（可选）

    Returns:
        格式化后的消息文本
    """
    if not price_data:
        return "❌ 未找到红线价格信息"

    # 按 GPU 型号分组
    grouped = {}
    for item in price_data:
        model = item.get("gpu_model", "未知型号")
        if model not in grouped:
            grouped[model] = []
        grouped[model].append(item)

    # 构建消息
    lines = ["💰 **红线价格查询结果**\n"]

    if gpu_type:
        lines.append(f"查询型号: {gpu_type}\n")

    lines.append("---\n")

    for model, prices in grouped.items():
        lines.append(f"**{model}**")

        for price in prices:
            region = price.get("region", "全球")
            price_hour = price.get("price_per_hour", 0)
            price_day = price.get("price_per_day", 0)
            currency = price.get("currency", "USD")
            update_time = price.get("update_time", "未知")

            lines.append(f"  📍 {region}")
            lines.append(f"     • 小时价: {currency} {price_hour:.2f}/小时")
            lines.append(f"     • 日价: {currency} {price_day:.2f}/天")
            lines.append(f"     • 更新时间: {update_time}")

        lines.append("")

    lines.append("---")
    lines.append("⚠️ **说明**: 以上为红线价格（内部定价参考），业务方可在此基础上定价")

    return "\n".join(lines)


def parse_price_query(text: str) -> Optional[str]:
    """
    从用户消息中提取 GPU 型号

    Args:
        text: 用户消息

    Returns:
        GPU 型号，如 "A100", "H100", "4090" 等，找不到返回 None
    """
    text_upper = text.upper()

    # GPU 型号列表
    gpu_types = [
        "A100", "A100-80GB", "A100-40GB",
        "H100", "H100-80GB",
        "H200", "H200-141GB",
        "H20",
        "L40S", "L40",
        "RTX4090", "4090",
        "RTX3090", "3090",
        "RTX5090", "5090",
        "A6000", "6000",
        "A800",
        "V100"
    ]

    for gpu in gpu_types:
        if gpu in text_upper:
            # 标准化返回格式
            if "4090" in gpu:
                return "RTX4090"
            elif "3090" in gpu:
                return "RTX3090"
            elif "5090" in gpu:
                return "RTX5090"
            elif "6000" in gpu:
                return "A6000"
            else:
                return gpu

    return None


async def intelligent_price_query(user_message: str) -> str:
    """
    使用 AI 智能理解用户问题并查询价格

    Args:
        user_message: 用户消息

    Returns:
        回复消息
    """
    try:
        # 先用简单规则提取 GPU 型号
        gpu_type = parse_price_query(user_message)

        # 判断是否是价格查询
        price_keywords = ["红线价格", "价格", "多少钱", "定价", "报价"]
        is_price_query = any(kw in user_message for kw in price_keywords)

        if not is_price_query:
            return ""  # 不是价格查询，返回空让其他模块处理

        # 调用 PPIO Claude API 理解用户意图
        system_prompt = """你是一个GPU价格查询助手。
你的任务是：
1. 判断用户是否在查询GPU价格
2. 提取用户想查询的GPU型号
3. 如果无法确定型号，询问用户具体型号

支持的GPU型号：A100, H100, H200, H20, L40S, L40, RTX4090, RTX3090, RTX5090, A6000, A800, V100

请以JSON格式回复：
{
  "is_price_query": true/false,
  "gpu_type": "GPU型号" 或 null,
  "clarification_needed": "需要询问用户的问题" 或 null
}"""

        response = ppio_client.chat.completions.create(
            model="claude-3-5-sonnet-20241022",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=500
        )

        ai_response = response.choices[0].message.content

        # 解析 AI 响应
        try:
            result = json.loads(ai_response)

            if not result.get("is_price_query"):
                return ""  # 不是价格查询

            if result.get("clarification_needed"):
                return result["clarification_needed"]

            # 获取 GPU 型号
            ai_gpu_type = result.get("gpu_type") or gpu_type

        except json.JSONDecodeError:
            # AI 返回格式错误，使用简单规则
            ai_gpu_type = gpu_type

        # 查询价格
        price_result = await fetch_price_from_cmdb(ai_gpu_type)

        if price_result["success"]:
            return format_price_message(price_result["data"], ai_gpu_type)
        else:
            return f"❌ 查询失败: {price_result['error']}"

    except Exception as e:
        logger.error(f"智能价格查询失败: {str(e)}")
        return f"❌ 查询出错: {str(e)}"


async def handle_price_query(user_message: str) -> Optional[str]:
    """
    处理价格查询请求（主入口）

    Args:
        user_message: 用户消息

    Returns:
        回复消息，如果不是价格查询返回 None
    """
    # 检查是否包含价格相关关键词
    price_keywords = ["红线价格", "价格", "多少钱", "定价", "报价", "红线"]

    if not any(kw in user_message for kw in price_keywords):
        return None  # 不是价格查询

    # 提取 GPU 型号
    gpu_type = parse_price_query(user_message)

    # 情况1: 直接关键词匹配（如"A100红线价格"）
    if gpu_type:
        logger.info(f"关键词匹配价格查询: {gpu_type}")
        price_result = await fetch_price_from_cmdb(gpu_type)

        if price_result["success"]:
            return format_price_message(price_result["data"], gpu_type)
        else:
            return f"❌ 查询失败: {price_result['error']}"

    # 情况2: 查询所有价格（如"红线价格列表"、"价格汇总"）
    menu_keywords = ["列表", "汇总", "全部", "所有", "都有哪些"]
    if any(kw in user_message for kw in menu_keywords):
        logger.info("查询所有红线价格")
        price_result = await fetch_price_from_cmdb(None)

        if price_result["success"]:
            return format_price_message(price_result["data"], None)
        else:
            return f"❌ 查询失败: {price_result['error']}"

    # 情况3: 智能理解（如"A100多少钱一小时"）
    logger.info(f"使用智能理解查询价格: {user_message}")
    return await intelligent_price_query(user_message)


# 测试用的模拟数据（当 CMDB API 不可用时）
MOCK_PRICE_DATA = [
    {
        "gpu_model": "A100-80GB",
        "price_per_hour": 2.50,
        "price_per_day": 50.00,
        "currency": "USD",
        "region": "国内",
        "update_time": "2024-01-15"
    },
    {
        "gpu_model": "A100-80GB",
        "price_per_hour": 2.80,
        "price_per_day": 56.00,
        "currency": "USD",
        "region": "海外",
        "update_time": "2024-01-15"
    },
    {
        "gpu_model": "H100-80GB",
        "price_per_hour": 4.00,
        "price_per_day": 80.00,
        "currency": "USD",
        "region": "国内",
        "update_time": "2024-01-15"
    },
    {
        "gpu_model": "RTX4090",
        "price_per_hour": 0.99,
        "price_per_day": 19.80,
        "currency": "USD",
        "region": "国内",
        "update_time": "2024-01-15"
    }
]


async def fetch_price_from_cmdb_mock(gpu_type: Optional[str] = None) -> Dict:
    """模拟 CMDB API（用于测试）"""
    if gpu_type:
        filtered = [p for p in MOCK_PRICE_DATA if gpu_type.upper() in p["gpu_model"].upper()]
        return {"success": True, "data": filtered, "error": None}
    else:
        return {"success": True, "data": MOCK_PRICE_DATA, "error": None}


# 在测试环境下使用模拟数据
if os.getenv("USE_MOCK_DATA", "false").lower() == "true":
    fetch_price_from_cmdb = fetch_price_from_cmdb_mock
    logger.info("⚠️  使用模拟价格数据")


if __name__ == "__main__":
    # 测试代码
    import asyncio

    async def test():
        print("=" * 60)
        print("红线价格查询测试")
        print("=" * 60)

        test_queries = [
            "A100红线价格",
            "H100多少钱",
            "4090的红线价格是多少",
            "所有GPU的红线价格列表"
        ]

        for query in test_queries:
            print(f"\n查询: {query}")
            result = await handle_price_query(query)
            print(result)
            print("-" * 60)

    asyncio.run(test())
