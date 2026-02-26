"""
飞书自动回复机器人
当有人@机器人询问资源数量时，自动回复引导信息
"""

import json
import re
import hashlib
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ============ 配置区域 ============
APP_ID = "your_app_id"  # 替换为你的 App ID
APP_SECRET = "your_app_secret"  # 替换为你的 App Secret
VERIFICATION_TOKEN = "your_verification_token"  # 替换为你的 Verification Token
ENCRYPT_KEY = ""  # 如果启用了加密，填写 Encrypt Key

# 自动回复内容
AUTO_REPLY_MESSAGE = '请在"售前常见问题答疑群"里艾特库存自动回复机器人'

# 关键词匹配规则（正则表达式）
# 匹配类似：xxx还有吗、xxx有几卡、xxx有多少、xxx还剩多少 等询问资源数量的问题
RESOURCE_PATTERNS = [
    r".{1,20}还有吗",
    r".{1,20}有几[卡张台个块]",
    r".{1,20}有多少",
    r".{1,20}还剩多少",
    r".{1,20}剩余多少",
    r".{1,20}库存",
    r".{1,20}还有没有",
    r".{1,20}有没有",
    r"还有.{1,20}吗",
    r"有.{1,20}资源吗",
]
# ============ 配置区域结束 ============


class FeishuBot:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None

    def get_tenant_access_token(self):
        """获取 tenant_access_token"""
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        data = {"app_id": self.app_id, "app_secret": self.app_secret}

        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        if result.get("code") == 0:
            self.access_token = result.get("tenant_access_token")
            return self.access_token
        else:
            print(f"获取 token 失败: {result}")
            return None

    def reply_message(self, message_id, content):
        """回复消息"""
        if not self.access_token:
            self.get_tenant_access_token()

        url = f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}/reply"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json; charset=utf-8",
        }
        data = {
            "content": json.dumps({"text": content}),
            "msg_type": "text",
        }

        response = requests.post(url, headers=headers, json=data)
        return response.json()


bot = FeishuBot(APP_ID, APP_SECRET)

# 用于消息去重，避免重复处理
processed_messages = set()


def is_resource_query(text):
    """判断消息是否是询问资源数量的问题"""
    for pattern in RESOURCE_PATTERNS:
        if re.search(pattern, text):
            return True
    return False


@app.route("/webhook/event", methods=["POST"])
def handle_event():
    """处理飞书事件回调"""
    data = request.json

    # 处理 URL 验证请求
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})

    # 验证 token
    if data.get("token") != VERIFICATION_TOKEN:
        return jsonify({"error": "Invalid token"}), 403

    # 处理事件
    header = data.get("header", {})
    event = data.get("event", {})

    # 只处理消息接收事件
    if header.get("event_type") == "im.message.receive_v1":
        message = event.get("message", {})
        message_id = message.get("message_id")

        # 消息去重
        if message_id in processed_messages:
            return jsonify({"code": 0})
        processed_messages.add(message_id)

        # 限制去重集合大小，防止内存泄漏
        if len(processed_messages) > 10000:
            processed_messages.clear()

        # 获取消息内容
        msg_type = message.get("message_type")
        if msg_type == "text":
            content = json.loads(message.get("content", "{}"))
            text = content.get("text", "")

            # 检查是否是询问资源的消息
            if is_resource_query(text):
                print(f"收到资源询问消息: {text}")
                result = bot.reply_message(message_id, AUTO_REPLY_MESSAGE)
                print(f"回复结果: {result}")

    return jsonify({"code": 0})


@app.route("/health", methods=["GET"])
def health_check():
    """健康检查接口"""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    print("飞书自动回复机器人启动中...")
    print(f"关键词匹配规则: {RESOURCE_PATTERNS}")
    print(f"自动回复内容: {AUTO_REPLY_MESSAGE}")
    app.run(host="0.0.0.0", port=3000, debug=True)
