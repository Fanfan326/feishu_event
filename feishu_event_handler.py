#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书事件监听服务
当机器人被@时，自动同步Grafana数据并发送到飞书群
"""

import asyncio
import json
import logging
import hmac
import hashlib
import base64
from datetime import datetime
from flask import Flask, request, jsonify
from typing import Dict, Any, Optional
import Instance

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./feishu_event.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 飞书配置（从Instance.py导入）
APP_ID = Instance.APP_ID
APP_SECRET = Instance.APP_SECRET
ENCRYPT_KEY = ""  # 如果配置了加密，填入加密密钥（在飞书开放平台事件订阅中配置）
VERIFICATION_TOKEN = ""  # 事件订阅验证Token（可选，在飞书开放平台事件订阅中配置）

app = Flask(__name__)


def verify_signature(timestamp: str, nonce: str, body: str, signature: str) -> bool:
    """
    验证飞书事件签名
    
    Args:
        timestamp: 时间戳
        nonce: 随机字符串
        body: 请求体
        signature: 签名
        
    Returns:
        bool: 验证是否通过
    """
    if not ENCRYPT_KEY:
        return True  # 如果没有配置加密密钥，跳过验证
    
    # 构建待签名字符串
    string_to_sign = f"{timestamp}{nonce}{ENCRYPT_KEY}{body}"
    
    # 计算签名
    hmac_code = hmac.new(
        ENCRYPT_KEY.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    
    # Base64编码
    sign = base64.b64encode(hmac_code).decode('utf-8')
    
    return sign == signature


def get_tenant_access_token() -> Optional[str]:
    """
    获取飞书 tenant_access_token
    
    Returns:
        str: tenant_access_token
    """
    import httpx
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}
    
    try:
        with httpx.Client() as client:
            resp = client.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if data.get("code", 0) == 0:
                return data["tenant_access_token"]
            else:
                logger.error(f"获取tenant_access_token失败: {data}")
                return None
    except Exception as e:
        logger.error(f"获取tenant_access_token异常: {str(e)}")
        return None


def is_bot_mentioned(event_data: Dict) -> bool:
    """
    检查机器人是否被@
    
    Args:
        event_data: 事件数据
        
    Returns:
        bool: 是否被@
    """
    try:
        # 获取事件和消息内容
        event = event_data.get('event', {})
        message = event.get('message', {})
        
        logger.info(f"收到消息事件，消息类型: {message.get('message_type', 'unknown')}")
        
        # 方法1: 检查mentions字段（最准确，飞书会在这里列出被@的用户）
        mentions = message.get('mentions', [])
        if mentions:
            logger.info(f"检测到@列表: {mentions}")
            # 检查是否@了机器人（通过检查open_id或user_id）
            # 如果有mentions且不为空，通常说明有@操作
            for mention in mentions:
                if isinstance(mention, dict):
                    # 检查是否@了机器人
                    # 飞书会在mentions中包含被@的用户信息
                    logger.info(f"@的用户信息: {mention}")
            # 如果有mentions，说明有@操作，返回True
            return True
        
        # 方法2: 检查消息内容中的@标记
        content = message.get('content', '')
        message_type = message.get('message_type', '')
        
        if message_type == 'text' and content:
            # 解析文本消息
            try:
                if isinstance(content, str):
                    text_content = json.loads(content)
                else:
                    text_content = content
                
                text = text_content.get('text', '')
                logger.info(f"消息文本内容: {text}")
                
                # 检查是否包含@标记
                if '@' in text:
                    logger.info("消息中包含@标记")
                    # 如果消息中包含@，可能是@了机器人
                    return True
                    
            except json.JSONDecodeError as e:
                logger.debug(f"解析消息内容失败: {e}")
                # 如果不是JSON格式，直接检查字符串
                if '@' in str(content):
                    logger.info("消息内容中包含@字符")
                    return True
        
        # 方法3: 检查消息中是否包含@机器人的特殊标记
        # 飞书会在消息中标记被@的用户，格式可能是 <at user_id="xxx">@用户名</at>
        content_str = str(content)
        if '<at' in content_str.lower() or '@' in content_str:
            logger.info("消息中包含@标记（HTML格式）")
            return True
        
        logger.debug("未检测到@机器人的标记")
        return False
    except Exception as e:
        logger.error(f"检查@状态失败: {str(e)}", exc_info=True)
        import traceback
        logger.error(traceback.format_exc())
        return False


def handle_bot_mention_async(event_data: Dict):
    """
    异步处理机器人被@的事件
    
    Args:
        event_data: 事件数据
    """
    try:
        logger.info("检测到机器人被@，开始同步Grafana数据...")
        
        # 调用Instance.py中的发送函数
        success = asyncio.run(Instance.send_feishu_message())
        
        if success:
            logger.info("Grafana数据同步成功")
        else:
            logger.warning("Grafana数据同步失败")
        
        return success
    except Exception as e:
        logger.error(f"处理@事件失败: {str(e)}", exc_info=True)
        return False


@app.route('/feishu/event', methods=['POST'])
def feishu_event():
    """
    飞书事件回调端点
    """
    try:
        # 获取请求头
        timestamp = request.headers.get('X-Lark-Request-Timestamp', '')
        nonce = request.headers.get('X-Lark-Request-Nonce', '')
        signature = request.headers.get('X-Lark-Signature', '')
        
        # 获取请求体
        body = request.get_data(as_text=True)
        data = request.get_json() or {}
        
        logger.info(f"收到飞书事件 - 类型: {data.get('type', 'unknown')}")
        
        # 验证签名（如果配置了）
        if ENCRYPT_KEY and signature:
            if not verify_signature(timestamp, nonce, body, signature):
                logger.warning("签名验证失败")
                return jsonify({"error": "Invalid signature"}), 401
        
        # 处理URL验证（首次配置事件订阅时）
        if data.get('type') == 'url_verification':
            challenge = data.get('challenge', '')
            logger.info("收到URL验证请求")
            return jsonify({"challenge": challenge}), 200
        
        # 处理事件
        event_type = data.get('header', {}).get('event_type', '')
        
        if event_type == 'im.message.receive_v1':
            # 接收消息事件
            event_data = data.get('event', {})
            
            # 检查是否@了机器人
            if is_bot_mentioned(data):
                logger.info("检测到机器人被@")
                # 使用线程池异步处理，避免阻塞
                import threading
                thread = threading.Thread(target=handle_bot_mention_async, args=(data,))
                thread.daemon = True
                thread.start()
                return jsonify({"code": 0, "msg": "success"}), 200
            else:
                logger.debug("消息中未@机器人，忽略")
                return jsonify({"code": 0, "msg": "ignored"}), 200
        
        # 其他事件类型
        logger.info(f"收到未处理的事件类型: {event_type}")
        return jsonify({"code": 0, "msg": "success"}), 200
        
    except Exception as e:
        logger.error(f"处理飞书事件失败: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "feishu_event_handler"
    }), 200


@app.route('/', methods=['GET'])
def index():
    """首页"""
    return jsonify({
        "service": "飞书事件监听服务",
        "version": "1.0.0",
        "endpoints": {
            "/feishu/event": "飞书事件回调端点",
            "/health": "健康检查"
        }
    }), 200


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("启动飞书事件监听服务")
    logger.info("=" * 60)
    logger.info("服务端点:")
    logger.info("  - POST /feishu/event : 飞书事件回调")
    logger.info("  - GET  /health       : 健康检查")
    logger.info("=" * 60)
    logger.info("配置说明:")
    logger.info("  1. 在飞书开放平台配置事件订阅")
    logger.info("  2. 设置事件回调URL: http://your-server:5000/feishu/event")
    logger.info("  3. 订阅事件: im.message.receive_v1")
    logger.info("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)

