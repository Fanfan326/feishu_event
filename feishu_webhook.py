#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书 Webhook 消息发送工具
支持发送文本消息到飞书群聊
"""

import requests
import json
from typing import Optional, Dict, Any


class FeishuWebhook:
    """飞书 Webhook 客户端"""
    
    def __init__(self, webhook_url: str):
        """
        初始化飞书 Webhook 客户端
        
        Args:
            webhook_url: 飞书机器人的 Webhook URL
        """
        self.webhook_url = webhook_url.strip()
        self._validate_url()
    
    def _validate_url(self):
        """
        验证 Webhook URL 格式
        """
        if not self.webhook_url:
            raise ValueError("Webhook URL 不能为空")
        
        # 检查 URL 格式
        if not self.webhook_url.startswith('https://'):
            raise ValueError("Webhook URL 必须以 https:// 开头")
        
        # 检查是否是飞书 Webhook URL
        if 'open.feishu.cn' not in self.webhook_url and 'larkoffice.com' not in self.webhook_url:
            print("⚠️  警告: Webhook URL 可能不是飞书的有效地址")
    
    def test_connection(self) -> bool:
        """
        测试 Webhook 连接
        
        Returns:
            bool: 连接是否成功
        """
        print("正在测试 Webhook 连接...")
        test_payload = {
            "msg_type": "text",
            "content": {
                "text": "连接测试"
            }
        }
        return self._send(test_payload)
    
    def send_text(self, text: str) -> bool:
        """
        发送纯文本消息
        
        Args:
            text: 要发送的文本内容
            
        Returns:
            bool: 发送是否成功
        """
        payload = {
            "msg_type": "text",
            "content": {
                "text": text
            }
        }
        return self._send(payload)
    
    def send_markdown(self, title: str, content: str) -> bool:
        """
        发送 Markdown 格式消息
        
        Args:
            title: 消息标题
            content: Markdown 格式的内容（支持 \\n 换行）
            
        Returns:
            bool: 发送是否成功
        """
        # 确保换行符被正确处理
        # 飞书markdown中，单个换行使用 \n，段落之间使用空行
        formatted_content = content
        
        payload = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title
                    },
                    "template": "blue"
                },
                "elements": [
                    {
                        "tag": "markdown",
                        "content": formatted_content
                    }
                ]
            }
        }
        return self._send(payload)
    
    def send_card(self, title: str, content: str, button_text: Optional[str] = None, 
                  button_url: Optional[str] = None) -> bool:
        """
        发送卡片消息
        
        Args:
            title: 卡片标题
            content: 卡片内容（支持 \\n 换行）
            button_text: 按钮文本（可选）
            button_url: 按钮链接（可选）
            
        Returns:
            bool: 发送是否成功
        """
        elements = [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": content
                }
            }
        ]
        
        if button_text and button_url:
            elements.append({
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": button_text
                        },
                        "type": "default",
                        "url": button_url
                    }
                ]
            })
        
        payload = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title
                    },
                    "template": "blue"
                },
                "elements": elements
            }
        }
        return self._send(payload)
    
    def _send(self, payload: Dict[str, Any]) -> bool:
        """
        发送消息到飞书
        
        Args:
            payload: 消息负载
            
        Returns:
            bool: 发送是否成功
        """
        try:
            headers = {
                "Content-Type": "application/json"
            }
            response = requests.post(
                self.webhook_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") == 0:
                print("✅ 消息发送成功")
                return True
            else:
                error_msg = result.get('msg', '未知错误')
                error_code = result.get('code', 'N/A')
                
                print(f"❌ 消息发送失败")
                print(f"   错误代码: {error_code}")
                print(f"   错误信息: {error_msg}")
                
                # 针对常见错误提供解决方案
                if 'invalid' in error_msg.lower() or 'token' in error_msg.lower():
                    print("\n💡 可能的解决方案:")
                    print("   1. 检查 Webhook URL 是否正确")
                    print("   2. 确认 Webhook URL 是否已过期或被撤销")
                    print("   3. 在飞书群聊中重新创建机器人并获取新的 Webhook URL")
                    print("   4. 确保 Webhook URL 格式正确（应以 https://open.feishu.cn/open-apis/bot/v2/hook/ 开头）")
                
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {str(e)}")
            print("\n💡 可能的解决方案:")
            print("   1. 检查网络连接")
            print("   2. 确认 Webhook URL 是否正确")
            print("   3. 检查防火墙设置")
            return False
        except Exception as e:
            print(f"❌ 发生错误: {str(e)}")
            return False


def main():
    """示例用法"""
    # 请替换为你的飞书 Webhook URL
    # 获取方式：在飞书群聊中添加自定义机器人，获取 Webhook URL
    webhook_url = input("请输入飞书 Webhook URL: ").strip()
    
    if not webhook_url:
        print("❌ Webhook URL 不能为空")
        return
    
    webhook = FeishuWebhook(webhook_url)
    
    print("\n选择消息类型:")
    print("1. 纯文本消息")
    print("2. Markdown 消息")
    print("3. 卡片消息")
    
    choice = input("\n请选择 (1-3): ").strip()
    
    if choice == "1":
        text = input("请输入要发送的文本: ")
        webhook.send_text(text)
    
    elif choice == "2":
        title = input("请输入标题: ")
        content = input("请输入 Markdown 内容: ")
        webhook.send_markdown(title, content)
    
    elif choice == "3":
        title = input("请输入卡片标题: ")
        content = input("请输入卡片内容: ")
        has_button = input("是否添加按钮? (y/n): ").strip().lower()
        
        button_text = None
        button_url = None
        if has_button == "y":
            button_text = input("请输入按钮文本: ")
            button_url = input("请输入按钮链接: ")
        
        webhook.send_card(title, content, button_text, button_url)
    
    else:
        print("❌ 无效的选择")


if __name__ == "__main__":
    main()

