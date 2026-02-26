#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Webhook 发送器
用于向外部服务发送 webhook 请求
"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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


class WebhookSender:
    """Webhook 发送器类"""
    
    def __init__(self, timeout: int = 10, max_retries: int = 3, retry_backoff: float = 1.0):
        """
        初始化 Webhook 发送器
        
        Args:
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            retry_backoff: 重试退避时间（秒）
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        
        # 配置重试策略
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=retry_backoff,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST", "PUT", "PATCH"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session = requests.Session()
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def send(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        secret: Optional[str] = None,
        method: str = "POST"
    ) -> Dict[str, Any]:
        """
        发送 webhook 请求
        
        Args:
            url: 目标 URL
            data: 要发送的数据
            headers: 自定义请求头
            secret: 可选的密钥，会添加到 Authorization 头
            method: HTTP 方法（默认 POST）
            
        Returns:
            Dict: 包含响应信息的字典
        """
        try:
            # 准备请求数据
            payload = data or {}
            
            # 准备请求头
            request_headers = {
                "Content-Type": "application/json",
                "User-Agent": "WebhookSender/1.0"
            }
            
            if headers:
                request_headers.update(headers)
            
            if secret:
                request_headers["X-Webhook-Secret"] = secret
                request_headers["Authorization"] = f"Bearer {secret}"
            
            # 记录请求
            logger.info(f"发送 webhook - URL: {url}, 方法: {method}")
            logger.debug(f"请求数据: {json.dumps(payload, ensure_ascii=False)}")
            
            # 发送请求
            start_time = time.time()
            response = self.session.request(
                method=method,
                url=url,
                json=payload,
                headers=request_headers,
                timeout=self.timeout
            )
            elapsed_time = time.time() - start_time
            
            # 记录响应
            logger.info(
                f"Webhook 响应 - URL: {url}, "
                f"状态码: {response.status_code}, "
                f"耗时: {elapsed_time:.2f}秒"
            )
            
            # 尝试解析响应
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text}
            
            # 构建结果
            result = {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "response_data": response_data,
                "elapsed_time": elapsed_time,
                "timestamp": datetime.now().isoformat()
            }
            
            if not result["success"]:
                logger.warning(f"Webhook 发送失败 - URL: {url}, 状态码: {response.status_code}")
                result["error"] = f"HTTP {response.status_code}: {response.text[:200]}"
            
            return result
        
        except requests.exceptions.Timeout:
            error_msg = f"请求超时 - URL: {url}, 超时时间: {self.timeout}秒"
            logger.error(error_msg)
            return {
                "success": False,
                "error": "Request timeout",
                "error_message": error_msg,
                "timestamp": datetime.now().isoformat()
            }
        
        except requests.exceptions.ConnectionError as e:
            error_msg = f"连接错误 - URL: {url}, 错误: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": "Connection error",
                "error_message": error_msg,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            error_msg = f"发送 webhook 时发生错误 - URL: {url}, 错误: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "error": "Unknown error",
                "error_message": error_msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def send_batch(
        self,
        urls: List[str],
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        secret: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        批量发送 webhook 到多个 URL
        
        Args:
            urls: URL 列表
            data: 要发送的数据
            headers: 自定义请求头
            secret: 可选的密钥
            
        Returns:
            List[Dict]: 每个 URL 的响应结果列表
        """
        results = []
        logger.info(f"批量发送 webhook - 目标数量: {len(urls)}")
        
        for url in urls:
            result = self.send(url, data, headers, secret)
            results.append({
                "url": url,
                **result
            })
            # 避免请求过快
            time.sleep(0.1)
        
        success_count = sum(1 for r in results if r.get("success"))
        logger.info(f"批量发送完成 - 成功: {success_count}/{len(urls)}")
        
        return results
    
    def send_with_retry(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        secret: Optional[str] = None,
        max_attempts: int = 3
    ) -> Dict[str, Any]:
        """
        带重试的发送（手动重试逻辑）
        
        Args:
            url: 目标 URL
            data: 要发送的数据
            headers: 自定义请求头
            secret: 可选的密钥
            max_attempts: 最大尝试次数
            
        Returns:
            Dict: 响应结果
        """
        last_result = None
        
        for attempt in range(1, max_attempts + 1):
            logger.info(f"尝试发送 webhook (第 {attempt}/{max_attempts} 次) - URL: {url}")
            
            result = self.send(url, data, headers, secret)
            last_result = result
            
            if result.get("success"):
                logger.info(f"Webhook 发送成功 (第 {attempt} 次尝试) - URL: {url}")
                return result
            
            if attempt < max_attempts:
                wait_time = self.retry_backoff * attempt
                logger.warning(f"发送失败，等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
        
        logger.error(f"Webhook 发送失败（已尝试 {max_attempts} 次） - URL: {url}")
        return last_result or {
            "success": False,
            "error": "All retry attempts failed",
            "timestamp": datetime.now().isoformat()
        }


# 便捷函数
def create_sender(timeout: int = 10, max_retries: int = 3) -> WebhookSender:
    """
    创建 Webhook 发送器实例
    
    Args:
        timeout: 请求超时时间
        max_retries: 最大重试次数
        
    Returns:
        WebhookSender: 发送器实例
    """
    return WebhookSender(timeout=timeout, max_retries=max_retries)


if __name__ == "__main__":
    # 示例使用
    sender = WebhookSender()
    
    # 发送测试 webhook
    result = sender.send(
        url="https://httpbin.org/post",
        data={"message": "测试消息", "timestamp": datetime.now().isoformat()},
        secret="test-secret"
    )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))

