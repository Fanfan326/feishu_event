#!/usr/bin/env python3
"""
GPU库存监控和采购提醒系统

功能：
1. 每天定时检查GPU库存
2. 当库存低于阈值时，发送飞书私聊提醒
3. 避免重复提醒

使用方法：
1. 配置 inventory_alert_config.json 文件
2. 立即检查：python inventory_alert.py --check
3. 定时运行：python inventory_alert.py --schedule
"""

import json
import os
import requests
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv
import gpu_inventory

# 加载环境变量
load_dotenv()

# 配置文件路径
CONFIG_FILE = "inventory_alert_config.json"
ALERT_HISTORY_FILE = ".inventory_alert_history.json"

# 飞书配置
APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")


def load_config() -> Dict:
    """加载配置文件"""
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ 配置文件不存在: {CONFIG_FILE}")
        return {}

    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_alert_history() -> Dict:
    """加载提醒历史"""
    if not os.path.exists(ALERT_HISTORY_FILE):
        return {}

    try:
        with open(ALERT_HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}


def save_alert_history(history: Dict):
    """保存提醒历史"""
    with open(ALERT_HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def should_send_alert(gpu_type: str, history: Dict) -> bool:
    """
    判断是否应该发送提醒
    避免24小时内重复提醒同一个GPU类型
    """
    if gpu_type not in history:
        return True

    last_alert_time = datetime.fromisoformat(history[gpu_type])
    time_since_last_alert = datetime.now() - last_alert_time

    # 24小时内不重复提醒
    return time_since_last_alert > timedelta(hours=24)


def get_tenant_access_token() -> Optional[str]:
    """获取飞书 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("code") == 0:
            return data["tenant_access_token"]
        else:
            print(f"❌ 获取token失败: {data}")
            return None
    except Exception as e:
        print(f"❌ 获取token异常: {e}")
        return None


def send_feishu_message(user_id: str, content: str) -> bool:
    """
    发送飞书私聊消息

    Args:
        user_id: 用户ID（open_id 或 user_id）
        content: 消息内容（支持Markdown）
    """
    token = get_tenant_access_token()
    if not token:
        return False

    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 构建消息
    payload = {
        "receive_id": user_id,
        "msg_type": "interactive",
        "content": json.dumps({
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": "⚠️ GPU库存预警"},
                "template": "orange"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": content}
                }
            ]
        }, ensure_ascii=False)
    }

    try:
        # 先尝试 open_id
        response = requests.post(
            url + "?receive_id_type=open_id",
            headers=headers,
            json=payload,
            timeout=10
        )

        if response.json().get("code") == 0:
            print(f"✅ 消息发送成功 (open_id: {user_id})")
            return True

        # 如果失败，尝试 user_id
        response = requests.post(
            url + "?receive_id_type=user_id",
            headers=headers,
            json=payload,
            timeout=10
        )

        if response.json().get("code") == 0:
            print(f"✅ 消息发送成功 (user_id: {user_id})")
            return True
        else:
            print(f"❌ 消息发送失败: {response.json()}")
            return False

    except Exception as e:
        print(f"❌ 发送消息异常: {e}")
        return False


def check_inventory_and_alert():
    """检查库存并发送提醒"""
    print("\n" + "="*60)
    print(f"🔍 开始检查GPU库存 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # 加载配置
    config = load_config()
    if not config:
        print("❌ 无法加载配置文件")
        return

    thresholds = config.get("gpu_thresholds", {})
    notification = config.get("notification", {})
    user_ids = notification.get("user_ids", [])

    if not user_ids or user_ids == ["请填写飞书用户ID"]:
        print("❌ 请先在配置文件中设置用户ID")
        return

    # 加载提醒历史
    history = load_alert_history()

    # 检查每种GPU的库存
    alerts = []

    for gpu_type, threshold_config in thresholds.items():
        min_free = threshold_config["min_free"]
        description = threshold_config["description"]

        # 查询库存
        inventory = gpu_inventory.get_gpu_inventory_by_type(gpu_type)

        if not inventory:
            print(f"⚠️  {description} ({gpu_type}): 无库存数据")
            continue

        free_count = inventory.get("free", 0)
        total_count = inventory.get("total", 0)

        print(f"📊 {description} ({gpu_type}): 空闲 {free_count}/{total_count} 张 (阈值: {min_free})")

        # 检查是否低于阈值
        if free_count < min_free:
            if should_send_alert(gpu_type, history):
                shortage = min_free - free_count
                alerts.append({
                    "gpu_type": gpu_type,
                    "description": description,
                    "free": free_count,
                    "total": total_count,
                    "min_free": min_free,
                    "shortage": shortage
                })
                print(f"  🔴 库存不足！建议采购 {shortage} 张以上")
            else:
                print(f"  ⏰ 已在24小时内提醒过，跳过")
        else:
            print(f"  ✅ 库存充足")

    # 发送提醒
    if alerts:
        print(f"\n📢 发现 {len(alerts)} 种GPU库存不足，准备发送提醒...")

        # 构建消息内容
        message_lines = [
            "**发现以下GPU库存不足，建议尽快发起采购：**\n"
        ]

        for alert in alerts:
            message_lines.append(
                f"🔴 **{alert['description']}** ({alert['gpu_type']})\n"
                f"   - 当前空闲：{alert['free']} 张\n"
                f"   - 安全库存：{alert['min_free']} 张\n"
                f"   - 建议采购：**{alert['shortage']} 张以上**\n"
            )

        message_lines.append(
            f"\n📅 检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        message_content = "\n".join(message_lines)

        # 发送给所有配置的用户
        success_count = 0
        for user_id in user_ids:
            if send_feishu_message(user_id, message_content):
                success_count += 1

        # 更新提醒历史
        if success_count > 0:
            now = datetime.now().isoformat()
            for alert in alerts:
                history[alert['gpu_type']] = now
            save_alert_history(history)
            print(f"\n✅ 提醒已发送给 {success_count}/{len(user_ids)} 个用户")
        else:
            print("\n❌ 消息发送失败")
    else:
        print("\n✅ 所有GPU库存充足，无需提醒")

    print("="*60 + "\n")


def run_scheduled():
    """定时运行"""
    config = load_config()
    if not config:
        print("❌ 无法加载配置文件")
        return

    check_time = config.get("notification", {}).get("check_time", "10:00")

    print("="*60)
    print("🤖 GPU库存监控系统已启动")
    print(f"⏰ 每天 {check_time} 自动检查库存")
    print("📧 当库存不足时会自动发送飞书提醒")
    print("="*60)

    # 设置定时任务
    schedule.every().day.at(check_time).do(check_inventory_and_alert)

    # 显示下次运行时间
    next_run = schedule.next_run()
    if next_run:
        print(f"\n⏱️  下次检查时间: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")

    # 持续运行
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n\n👋 监控系统已停止")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "--check":
            # 立即检查
            check_inventory_and_alert()
        elif sys.argv[1] == "--schedule":
            # 定时运行
            run_scheduled()
        else:
            print("用法:")
            print("  python inventory_alert.py --check      # 立即检查一次")
            print("  python inventory_alert.py --schedule   # 定时运行")
    else:
        print("用法:")
        print("  python inventory_alert.py --check      # 立即检查一次")
        print("  python inventory_alert.py --schedule   # 定时运行")
