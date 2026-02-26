#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书 Webhook 使用示例
演示如何使用 FeishuWebhook 类发送各种类型的消息
"""

from feishu_webhook import FeishuWebhook

# 请替换为你的飞书 Webhook URL
# 获取方式：在飞书群聊中添加自定义机器人，获取 Webhook URL
WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/your-webhook-url-here"


def example_send_text():
    """示例1: 发送纯文本消息"""
    print("\n=== 示例1: 发送纯文本消息 ===")
    webhook = FeishuWebhook(WEBHOOK_URL)
    webhook.send_text("这是一条测试消息\n时间: 2024-01-01 12:00:00")


def example_send_markdown():
    """示例2: 发送 Markdown 格式消息"""
    print("\n=== 示例2: 发送 Markdown 消息 ===")
    webhook = FeishuWebhook(WEBHOOK_URL)
    
    # 方式1: 使用三引号字符串，自动保留换行
    markdown_content = """**系统通知**

- 状态: ✅ 运行正常
- CPU使用率: 45%
- 内存使用率: 60%

> 这是一条重要通知"""
    
    # 方式2: 使用 \n 显式换行
    markdown_content2 = "**系统通知**\n\n- 状态: ✅ 运行正常\n- CPU使用率: 45%\n- 内存使用率: 60%\n\n> 这是一条重要通知"
    
    webhook.send_markdown("系统监控报告", markdown_content)


def example_send_card():
    """示例3: 发送卡片消息（带按钮）"""
    print("\n=== 示例3: 发送卡片消息 ===")
    webhook = FeishuWebhook(WEBHOOK_URL)
    
    content = """
**任务完成通知**

任务名称: 数据处理任务
完成时间: 2024-01-01 12:00:00
处理记录数: 1000条
状态: ✅ 成功
"""
    webhook.send_card(
        title="任务完成",
        content=content,
        button_text="查看详情",
        button_url="https://example.com/task/123"
    )


def example_send_notification():
    """示例4: 发送通知消息（不带按钮）"""
    print("\n=== 示例4: 发送通知消息 ===")
    webhook = FeishuWebhook(WEBHOOK_URL)
    
    content = """
**提醒**

明天下午2点有重要会议，请准时参加。

会议主题: 项目进度讨论
参会人员: 全体成员
"""
    webhook.send_card(
        title="会议提醒",
        content=content
    )


def example_error_notification():
    """示例5: 发送错误通知"""
    print("\n=== 示例5: 发送错误通知 ===")
    webhook = FeishuWebhook(WEBHOOK_URL)
    
    error_content = """
**⚠️ 系统错误**

错误类型: 数据库连接失败
发生时间: 2024-01-01 12:00:00
错误信息: Connection timeout

请尽快处理！
"""
    webhook.send_card(
        title="系统告警",
        content=error_content,
        button_text="查看日志",
        button_url="https://example.com/logs"
    )


def example_daily_report():
    """示例6: 发送日报"""
    print("\n=== 示例6: 发送日报 ===")
    webhook = FeishuWebhook(WEBHOOK_URL)
    
    # 使用 \n 进行换行，空行用 \n\n
    report_content = "**今日数据统计**\n\n📊 访问量: 10,234\n👥 新用户: 156\n💰 收入: ¥12,345\n📈 增长率: +15.6%\n\n数据更新时间: 2024-01-01 23:59:59"
    
    webhook.send_markdown("每日数据报告", report_content)


def main():
    """主函数 - 运行所有示例"""
    print("=" * 50)
    print("飞书 Webhook 使用示例")
    print("=" * 50)
    
    # 检查是否配置了 Webhook URL
    if "your-webhook-url-here" in WEBHOOK_URL:
        print("\n⚠️  请先配置 WEBHOOK_URL！")
        print("编辑此文件，将 WEBHOOK_URL 替换为你的飞书 Webhook URL")
        return
    
    print("\n选择要运行的示例:")
    print("1. 发送纯文本消息")
    print("2. 发送 Markdown 消息")
    print("3. 发送卡片消息（带按钮）")
    print("4. 发送通知消息（不带按钮）")
    print("5. 发送错误通知")
    print("6. 发送日报")
    print("7. 运行所有示例")
    print("0. 退出")
    
    choice = input("\n请选择 (0-7): ").strip()
    
    examples = {
        "1": example_send_text,
        "2": example_send_markdown,
        "3": example_send_card,
        "4": example_send_notification,
        "5": example_error_notification,
        "6": example_daily_report,
    }
    
    if choice == "0":
        print("退出")
        return
    elif choice == "7":
        # 运行所有示例
        for func in examples.values():
            func()
            import time
            time.sleep(1)  # 避免发送过快
    elif choice in examples:
        examples[choice]()
    else:
        print("❌ 无效的选择")


if __name__ == "__main__":
    main()

