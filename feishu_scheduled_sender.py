#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书定时消息发送工具
每天北京时间 10:30 自动发送文本消息到飞书
"""

import schedule
import time
from datetime import datetime, timezone, timedelta
from feishu_webhook import FeishuWebhook

# 飞书 Webhook URL
WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/68fdfa32-b99d-4628-a4d7-fdd36695df66"

# 要发送的消息内容（可以修改为你需要的内容）
MESSAGE_CONTENT = """每日提醒

这是自动发送的每日消息。
时间: {current_time}

如有需要，请修改 MESSAGE_CONTENT 变量来更改消息内容。"""

# 用于防止重复发送的标记
last_sent_date = None


def get_beijing_time():
    """获取北京时间（UTC+8）"""
    beijing_tz = timezone(timedelta(hours=8))
    return datetime.now(beijing_tz)


def send_daily_message():
    """发送每日消息"""
    try:
        # 获取北京时间
        beijing_now = get_beijing_time()
        current_time = beijing_now.strftime("%Y-%m-%d %H:%M:%S")
        
        # 格式化消息内容
        message = MESSAGE_CONTENT.format(current_time=current_time)
        
        # 创建 webhook 客户端并发送消息
        webhook = FeishuWebhook(WEBHOOK_URL)
        success = webhook.send_text(message)
        
        if success:
            print(f"[{current_time} 北京时间] ✅ 消息已成功发送到飞书")
        else:
            print(f"[{current_time} 北京时间] ❌ 消息发送失败")
            
    except Exception as e:
        beijing_now = get_beijing_time()
        current_time = beijing_now.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time} 北京时间] ❌ 发送消息时发生错误: {str(e)}")


def check_and_send():
    """检查是否到了北京时间 10:30，如果是则发送消息"""
    global last_sent_date
    beijing_now = get_beijing_time()
    
    # 检查是否是 10:30
    if beijing_now.hour == 10 and beijing_now.minute == 30:
        # 检查今天是否已经发送过
        today = beijing_now.date()
        if last_sent_date != today:
            last_sent_date = today
            send_daily_message()
            return True
    return False


def main():
    """主函数"""
    print("=" * 60)
    print("飞书定时消息发送工具")
    print("=" * 60)
    print(f"Webhook URL: {WEBHOOK_URL}")
    print("定时任务: 每天北京时间 10:30 自动发送消息")
    print("=" * 60)
    
    # 测试发送一次（可选）
    test_send = input("\n是否先测试发送一次消息? (y/n，默认n): ").strip().lower()
    if test_send == 'y':
        print("\n正在测试发送...")
        send_daily_message()
        print()
    
    # 显示当前北京时间
    beijing_now = get_beijing_time()
    print(f"\n当前北京时间: {beijing_now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 定时任务已取消
    # 如需重新启用，取消下面这行的注释
    # schedule.every().minute.do(check_and_send)
    
    print("\n⚠️  定时任务已取消")
    print("📅 10:30 自动发送功能已禁用")
    print("💡 如需重新启用，请编辑脚本取消相关代码的注释")
    print("=" * 60)
    
    print("\n程序已退出（定时任务已取消，无需持续运行）")


if __name__ == "__main__":
    main()

