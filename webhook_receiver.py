#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Webhook 接收器
使用 Flask 创建 webhook 端点，接收 POST 请求
"""

import logging
import json
from datetime import datetime
from flask import Flask, request, jsonify
from typing import Dict, Any, Optional, Callable

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webhook.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WebhookReceiver:
    """Webhook 接收器类"""
    
    def __init__(self, app_name: str = "WebhookReceiver", secret: Optional[str] = None):
        """
        初始化 Webhook 接收器
        
        Args:
            app_name: Flask 应用名称
            secret: 可选的 webhook 密钥，用于验证请求
        """
        self.app = Flask(app_name)
        self.secret = secret
        self.handlers: Dict[str, Callable] = {}
        self._setup_routes()
    
    def _setup_routes(self):
        """设置路由"""
        # 健康检查端点
        @self.app.route('/health', methods=['GET'])
        def health():
            return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200
        
        # 默认 webhook 端点
        @self.app.route('/webhook', methods=['POST'])
        def webhook():
            return self._handle_webhook()
        
        # 自定义路径 webhook 端点
        @self.app.route('/webhook/<path:endpoint>', methods=['POST'])
        def webhook_custom(endpoint):
            return self._handle_webhook(endpoint)
    
    def _verify_secret(self, headers: Dict) -> bool:
        """
        验证 webhook 密钥
        
        Args:
            headers: 请求头
            
        Returns:
            bool: 验证是否通过
        """
        if not self.secret:
            return True
        
        received_secret = headers.get('X-Webhook-Secret') or headers.get('Authorization', '').replace('Bearer ', '')
        return received_secret == self.secret
    
    def _handle_webhook(self, endpoint: str = 'default') -> tuple:
        """
        处理 webhook 请求
        
        Args:
            endpoint: webhook 端点路径
            
        Returns:
            tuple: (响应数据, 状态码)
        """
        try:
            # 记录请求信息
            logger.info(f"收到 webhook 请求 - 端点: {endpoint}, IP: {request.remote_addr}")
            
            # 验证密钥
            if not self._verify_secret(request.headers):
                logger.warning(f"Webhook 密钥验证失败 - 端点: {endpoint}, IP: {request.remote_addr}")
                return jsonify({"error": "Unauthorized", "message": "Invalid secret"}), 401
            
            # 获取请求数据
            content_type = request.headers.get('Content-Type', '').lower()
            
            if 'application/json' in content_type:
                data = request.get_json() or {}
            elif 'application/x-www-form-urlencoded' in content_type:
                data = dict(request.form)
            elif 'multipart/form-data' in content_type:
                data = dict(request.form)
            else:
                # 尝试解析 JSON
                try:
                    data = request.get_json() or {}
                except:
                    data = {"raw": request.data.decode('utf-8', errors='ignore')}
            
            # 记录请求数据
            logger.info(f"Webhook 数据 - 端点: {endpoint}, 数据: {json.dumps(data, ensure_ascii=False)}")
            
            # 获取请求头信息
            headers_info = dict(request.headers)
            
            # 构建 webhook 信息
            webhook_info = {
                "endpoint": endpoint,
                "timestamp": datetime.now().isoformat(),
                "method": request.method,
                "headers": headers_info,
                "data": data,
                "remote_addr": request.remote_addr
            }
            
            # 调用注册的处理器
            if endpoint in self.handlers:
                try:
                    result = self.handlers[endpoint](webhook_info)
                    logger.info(f"处理器执行成功 - 端点: {endpoint}")
                    return jsonify({
                        "status": "success",
                        "message": "Webhook received and processed",
                        "result": result
                    }), 200
                except Exception as e:
                    logger.error(f"处理器执行失败 - 端点: {endpoint}, 错误: {str(e)}", exc_info=True)
                    return jsonify({
                        "status": "error",
                        "message": f"Handler error: {str(e)}"
                    }), 500
            else:
                # 默认处理：只记录
                logger.info(f"使用默认处理 - 端点: {endpoint}")
                return jsonify({
                    "status": "success",
                    "message": "Webhook received",
                    "endpoint": endpoint,
                    "data": data
                }), 200
        
        except Exception as e:
            logger.error(f"处理 webhook 请求时发生错误: {str(e)}", exc_info=True)
            return jsonify({
                "status": "error",
                "message": f"Internal server error: {str(e)}"
            }), 500
    
    def register_handler(self, endpoint: str, handler: Callable):
        """
        注册 webhook 处理器
        
        Args:
            endpoint: webhook 端点路径
            handler: 处理函数，接收 webhook_info 字典作为参数
        """
        self.handlers[endpoint] = handler
        logger.info(f"注册处理器 - 端点: {endpoint}")
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """
        运行 Flask 应用
        
        Args:
            host: 主机地址
            port: 端口号
            debug: 是否开启调试模式
        """
        logger.info(f"启动 Webhook 接收器 - 地址: {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


# 便捷函数
def create_receiver(secret: Optional[str] = None) -> WebhookReceiver:
    """
    创建 Webhook 接收器实例
    
    Args:
        secret: 可选的 webhook 密钥
        
    Returns:
        WebhookReceiver: 接收器实例
    """
    return WebhookReceiver(secret=secret)


if __name__ == "__main__":
    # 示例使用
    receiver = WebhookReceiver(secret="your-secret-key")
    
    # 注册自定义处理器
    def handle_github_webhook(webhook_info):
        """处理 GitHub webhook"""
        data = webhook_info.get('data', {})
        event = webhook_info.get('headers', {}).get('X-GitHub-Event', 'unknown')
        logger.info(f"GitHub 事件: {event}")
        # 在这里处理你的业务逻辑
        return {"processed": True, "event": event}
    
    receiver.register_handler('github', handle_github_webhook)
    
    # 启动服务器
    receiver.run(host='0.0.0.0', port=5000, debug=True)

