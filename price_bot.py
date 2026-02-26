#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
红线价格查询机器人（独立版）
专门用于查询GPU红线价格，给业务方定价参考
"""

import asyncio
import json
import logging
import os
from typing import Optional
from fastapi import FastAPI, Request, Header
from fastapi.responses import JSONResponse
import uvicorn
import httpx

# 导入价格查询模块
from price_query import handle_price_query

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# 飞书应用配置
APP_ID = os.getenv("FEISHU_APP_ID", "your-app-id")
APP_SECRET = os.getenv("FEISHU_APP_SECRET", "your-app-secret")
VERIFICATION_TOKEN = os.getenv("FEISHU_VERIFICATION_TOKEN", "")


async def get_tenant_access_token() -> Optional[str]:
    """获取飞书 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, json=payload)
            result = response.json()

            if result.get("code") == 0:
                return result.get("tenant_access_token")
            else:
                logger.error(f"获取 token 失败: {result}")
                return None
    except Exception as e:
        logger.error(f"获取 token 异常: {str(e)}")
        return None


async def send_text_message(chat_id: str, text: str) -> bool:
    """发送文本消息到飞书群聊"""
    token = await get_tenant_access_token()
    if not token:
        return False

    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": text}, ensure_ascii=False)
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, headers=headers, json=payload)
            result = response.json()

            if result.get("code") == 0:
                logger.info(f"消息已发送: {chat_id}")
                return True
            else:
                logger.error(f"发送消息失败: {result}")
                return False
    except Exception as e:
        logger.error(f"发送消息异常: {str(e)}")
        return False


async def send_card_message(chat_id: str, title: str, content: str) -> bool:
    """发送卡片消息到飞书群聊"""
    token = await get_tenant_access_token()
    if not token:
        return False

    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 构建卡片内容
    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": title},
            "template": "blue"
        },
        "elements": [
            {
                "tag": "markdown",
                "content": content
            }
        ]
    }

    payload = {
        "receive_id": chat_id,
        "msg_type": "interactive",
        "content": json.dumps({"card": card}, ensure_ascii=False)
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, headers=headers, json=payload)
            result = response.json()

            if result.get("code") == 0:
                logger.info(f"卡片消息已发送: {chat_id}")
                return True
            else:
                logger.error(f"发送卡片失败: {result}")
                return False
    except Exception as e:
        logger.error(f"发送卡片异常: {str(e)}")
        return False


def parse_message_text(text: str) -> str:
    """移除@机器人标记"""
    import re
    text = re.sub(r'@_user_\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


async def handle_user_message(chat_id: str, message_text: str):
    """处理用户消息"""
    try:
        # 清理消息
        clean_text = parse_message_text(message_text)
        logger.info(f"收到消息: {clean_text}")

        # 空消息，发送帮助
        if not clean_text:
            help_text = """💰 **红线价格查询机器人**

🔍 **使用方法**：
• 查询单个型号：`A100红线价格`
• 查询所有价格：`红线价格列表`
• 智能提问：`H100多少钱一小时`

📋 **支持的GPU型号**：
A100, H100, H200, H20, L40S, L40, RTX4090, RTX3090, RTX5090, A6000, A800, V100

⚠️ 红线价格为内部定价参考，业务方可在此基础上定价"""
            await send_text_message(chat_id, help_text)
            return

        # 帮助命令
        if clean_text.lower() in ["help", "帮助", "?", "使用说明"]:
            help_text = """💰 **红线价格查询机器人**

🔍 **使用方法**：
• 查询单个型号：`A100红线价格`
• 查询所有价格：`红线价格列表`
• 智能提问：`H100多少钱一小时`

📋 **支持的GPU型号**：
A100, H100, H200, H20, L40S, L40, RTX4090, RTX3090, RTX5090, A6000, A800, V100

⚠️ 红线价格为内部定价参考，业务方可在此基础上定价

📞 **联系方式**：
有问题请联系价格管理团队"""
            await send_text_message(chat_id, help_text)
            return

        # 查询价格
        reply = await handle_price_query(clean_text)

        if reply:
            # 使用卡片消息展示价格
            await send_card_message(chat_id, "💰 红线价格查询", reply)
        else:
            # 不是价格查询
            fallback = """❓ 没理解你的意思~

试试这样问：
• `A100红线价格`
• `红线价格列表`
• `H100多少钱`

输入 `帮助` 查看使用说明"""
            await send_text_message(chat_id, fallback)

    except Exception as e:
        logger.error(f"处理消息异常: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        await send_text_message(chat_id, f"❌ 处理失败: {str(e)}")


@app.post("/webhook")
async def handle_webhook(
    request: Request,
    x_lark_request_timestamp: Optional[str] = Header(None, alias="X-Lark-Request-Timestamp"),
    x_lark_request_nonce: Optional[str] = Header(None, alias="X-Lark-Request-Nonce"),
    x_lark_signature: Optional[str] = Header(None, alias="X-Lark-Signature"),
):
    """处理飞书 Webhook 回调"""
    try:
        body = await request.body()
        data = json.loads(body.decode('utf-8'))

        # URL 验证
        if "challenge" in data:
            challenge = data.get("challenge")
            logger.info(f"URL验证: {challenge}")
            return JSONResponse(content={"challenge": challenge})

        # 处理消息事件
        event = data.get("event", {})
        event_type = event.get("type")

        logger.info(f"收到事件: {event_type}")

        if event_type == "im.message.receive_v1":
            message = event.get("message", {})
            chat_id = message.get("chat_id")
            content = json.loads(message.get("content", "{}"))
            text = content.get("text", "")

            # 检查是否@了机器人
            mentions = message.get("mentions", [])
            is_mention_bot = any(m.get("type") == "bot" for m in mentions)

            if is_mention_bot or len(mentions) == 0:  # @机器人 或 私聊
                # 异步处理消息
                asyncio.create_task(handle_user_message(chat_id, text))

        return JSONResponse(content={"code": 0, "msg": "success"})

    except Exception as e:
        logger.error(f"处理 webhook 异常: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return JSONResponse(content={"code": 1, "msg": str(e)}, status_code=500)


@app.get("/health")
async def health():
    """健康检查"""
    return JSONResponse(content={"status": "ok", "service": "Price Bot"})


@app.get("/")
async def root():
    """根路径"""
    return JSONResponse(content={
        "service": "红线价格查询机器人",
        "version": "1.0.0",
        "endpoints": {
            "webhook": "/webhook",
            "health": "/health"
        }
    })


def main():
    """启动服务"""
    port = int(os.getenv("PORT", "8001"))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info("=" * 60)
    logger.info("🤖 红线价格查询机器人启动")
    logger.info(f"📡 监听地址: http://{host}:{port}")
    logger.info(f"🔗 Webhook URL: http://{host}:{port}/webhook")
    logger.info("=" * 60)

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
