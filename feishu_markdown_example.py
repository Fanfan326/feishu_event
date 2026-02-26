#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书 Markdown 换行示例
演示如何在飞书 webhook 中正确使用换行
"""

from feishu_webhook import FeishuWebhook

# 请替换为你的 Webhook URL
WEBHOOK_URL = "your-webhook-url-here"


def example_single_line_break():
    """示例1: 单行换行（使用 \n）"""
    print("示例1: 单行换行")
    webhook = FeishuWebhook(WEBHOOK_URL)
    
    # 使用 \n 进行单行换行
    content = "第一行\n第二行\n第三行"
    webhook.send_markdown("单行换行示例", content)


def example_paragraph_break():
    """示例2: 段落换行（使用 \n\n）"""
    print("示例2: 段落换行")
    webhook = FeishuWebhook(WEBHOOK_URL)
    
    # 使用 \n\n 进行段落分隔
    content = "第一段内容\n\n第二段内容\n\n第三段内容"
    webhook.send_markdown("段落换行示例", content)


def example_mixed_formatting():
    """示例3: 混合格式（标题、列表、换行）"""
    print("示例3: 混合格式")
    webhook = FeishuWebhook(WEBHOOK_URL)
    
    # 混合使用换行和格式
    content = """**标题**

这是第一段内容

- 列表项1
- 列表项2
- 列表项3

这是第二段内容

> 引用内容"""
    
    webhook.send_markdown("混合格式示例", content)


def example_code_block():
    """示例4: 代码块和换行"""
    print("示例4: 代码块")
    webhook = FeishuWebhook(WEBHOOK_URL)
    
    content = """**代码示例**

```python
def hello():
    print("Hello")
    print("World")
```

这是代码块后的内容"""
    
    webhook.send_markdown("代码块示例", content)


def example_table():
    """示例5: 表格和换行"""
    print("示例5: 表格")
    webhook = FeishuWebhook(WEBHOOK_URL)
    
    content = """**数据表格**

| 项目 | 数值 | 状态 |
|------|------|------|
| CPU  | 45%  | 正常 |
| 内存 | 60%  | 正常 |
| 磁盘 | 80%  | 警告 |

**说明**: 以上数据为实时监控结果"""
    
    webhook.send_markdown("表格示例", content)


def example_multi_line_text():
    """示例6: 多行文本（推荐方式）"""
    print("示例6: 多行文本")
    webhook = FeishuWebhook(WEBHOOK_URL)
    
    # 方式1: 使用三引号字符串（推荐，更易读）
    content = """**系统通知**

系统运行状态正常

**详细信息:**
- 服务状态: ✅ 正常
- 响应时间: 120ms
- 错误率: 0.01%

**注意事项:**
请定期检查系统日志"""
    
    # 方式2: 使用 \n 显式换行
    content2 = "**系统通知**\n\n系统运行状态正常\n\n**详细信息:**\n- 服务状态: ✅ 正常\n- 响应时间: 120ms\n- 错误率: 0.01%\n\n**注意事项:**\n请定期检查系统日志"
    
    webhook.send_markdown("多行文本示例", content)


def example_practical_usage():
    """示例7: 实际使用场景"""
    print("示例7: 实际使用场景")
    webhook = FeishuWebhook(WEBHOOK_URL)
    
    # 实际场景：发送任务完成通知
    task_content = f"""**任务完成通知**

任务名称: 数据处理任务
完成时间: 2024-01-01 12:00:00
处理记录数: 1,000条
状态: ✅ 成功

**处理详情:**
- 成功: 1,000条
- 失败: 0条
- 耗时: 5分30秒

**下一步操作:**
请检查处理结果并确认数据正确性"""
    
    webhook.send_markdown("任务完成", task_content)


def main():
    """主函数"""
    if "your-webhook-url-here" in WEBHOOK_URL:
        print("⚠️  请先配置 WEBHOOK_URL！")
        print("编辑此文件，将 WEBHOOK_URL 替换为你的飞书 Webhook URL")
        return
    
    print("=" * 60)
    print("飞书 Markdown 换行示例")
    print("=" * 60)
    print("\n选择要运行的示例:")
    print("1. 单行换行")
    print("2. 段落换行")
    print("3. 混合格式")
    print("4. 代码块")
    print("5. 表格")
    print("6. 多行文本")
    print("7. 实际使用场景")
    print("0. 退出")
    
    choice = input("\n请选择 (0-7): ").strip()
    
    examples = {
        "1": example_single_line_break,
        "2": example_paragraph_break,
        "3": example_mixed_formatting,
        "4": example_code_block,
        "5": example_table,
        "6": example_multi_line_text,
        "7": example_practical_usage,
    }
    
    if choice == "0":
        print("退出")
        return
    elif choice in examples:
        examples[choice]()
    else:
        print("❌ 无效的选择")


if __name__ == "__main__":
    main()




