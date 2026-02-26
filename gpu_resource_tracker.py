"""
GPU 资源申请工单汇总系统

功能：
1. 从 Excel 文件导入轻流工单数据
2. 存储到本地数据库
3. 每2天汇总一次，推送到飞书群

使用方法：
1. 导入 Excel: python gpu_resource_tracker.py import gpu_data.xlsx
2. 立即汇总:   python gpu_resource_tracker.py report
3. 定时汇总:   python gpu_resource_tracker.py schedule
4. 测试飞书:   python gpu_resource_tracker.py test
"""

import json
import sqlite3
import requests
from datetime import datetime, timedelta
import schedule
import time
import threading
import sys
import os

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

# ============ 配置 ============
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/7bb40caa-944f-452d-b30e-ab962ef398b6"
DATABASE_FILE = "gpu_tickets.db"
SERVER_PORT = 5000

# ============ 数据库初始化 ============
def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT UNIQUE,
            applicant TEXT,
            gpu_type TEXT,
            gpu_count INTEGER,
            status TEXT,
            requirement TEXT,
            environment TEXT,
            apply_time TEXT,
            update_time TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("数据库初始化完成")

# ============ 数据库操作 ============
def save_ticket(data):
    """保存或更新工单"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # 根据轻流推送的数据格式，提取字段（需要根据实际情况调整）
    ticket_id = data.get("编号") or data.get("ticket_id") or data.get("id")
    applicant = data.get("申请人") or data.get("applicant")
    gpu_type = extract_gpu_type(data.get("需求概要") or data.get("gpu_type") or "")
    gpu_count = data.get("gpu_count") or 1
    status = data.get("当前流程状态") or data.get("status")
    requirement = data.get("需求概要") or data.get("requirement")
    environment = data.get("资源使用环境") or data.get("environment")
    apply_time = data.get("申请时间") or data.get("apply_time")
    update_time = data.get("更新时间") or data.get("update_time")

    cursor.execute('''
        INSERT OR REPLACE INTO tickets
        (ticket_id, applicant, gpu_type, gpu_count, status, requirement, environment, apply_time, update_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (ticket_id, applicant, gpu_type, gpu_count, status, requirement, environment, apply_time, update_time))

    conn.commit()
    conn.close()
    print(f"工单 {ticket_id} 已保存")

def extract_gpu_type(text):
    """从文本中提取 GPU 类型"""
    gpu_types = ["5090", "4090", "3090", "A100", "H20", "H100", "A800", "H800", "V100"]
    text = str(text).upper()
    for gpu in gpu_types:
        if gpu in text:
            return gpu
    return "其他"

# ============ Excel 导入 ============
def import_from_excel(file_path):
    """从 Excel 文件导入工单数据"""
    if not HAS_PANDAS:
        print("错误: 需要安装 pandas 和 openpyxl")
        print("运行: pip install pandas openpyxl")
        return False

    if not os.path.exists(file_path):
        print(f"错误: 文件不存在 - {file_path}")
        return False

    print(f"正在读取文件: {file_path}")

    # 读取 Excel（不使用表头，因为轻流导出格式特殊）
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path, header=None)
    else:
        df = pd.read_excel(file_path, header=None)

    print(f"读取到 {len(df)} 行数据")

    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # 清空旧数据（每次导入全量更新）
    cursor.execute("DELETE FROM tickets")

    imported = 0
    # 轻流导出格式：第1列是编号（数字），第2列是状态，第3列是需求标题
    for i in range(len(df)):
        row = df.iloc[i]
        # 检查第1列是否是有效的编号（数字）
        try:
            ticket_id_val = row[1]
            if pd.isna(ticket_id_val):
                continue
            ticket_id = str(int(float(ticket_id_val)))
        except (ValueError, TypeError):
            continue

        # 提取数据
        status = str(row[2]) if pd.notna(row[2]) else ""
        requirement = str(row[3]) if pd.notna(row[3]) else ""
        environment = str(row[6]) if len(row) > 6 and pd.notna(row[6]) else ""

        # 尝试从下一行获取申请人信息（轻流格式中申请人可能在下一行）
        applicant = ""
        if i + 1 < len(df):
            next_row = df.iloc[i + 1]
            if len(next_row) > 4 and pd.notna(next_row[4]):
                applicant = str(next_row[4])

        # 从需求标题中提取 GPU 类型
        gpu_type = extract_gpu_type(requirement)

        print(f"  导入: 编号={ticket_id}, 状态={status}, 需求={requirement}, GPU={gpu_type}")

        cursor.execute('''
            INSERT OR REPLACE INTO tickets
            (ticket_id, applicant, gpu_type, gpu_count, status, requirement, environment, apply_time, update_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ticket_id, applicant, gpu_type, 1, status, requirement, environment, "", ""))
        imported += 1

    conn.commit()
    conn.close()
    print(f"成功导入 {imported} 条工单记录")

# ============ 统计查询 ============
def get_statistics():
    """获取统计数据"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # 申请中的状态列表（根据实际情况调整）
    pending_statuses = ["直属主管审批", "资源需求处理中", "运维资源确认", "审批中", "申请中"]

    stats = {
        "total_pending": 0,
        "by_gpu_type": {},
        "by_status": {},
        "tickets": [],  # 工单详情列表
        "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # 总申请中工单数
    placeholders = ",".join(["?" for _ in pending_statuses])
    cursor.execute(f"SELECT COUNT(*) FROM tickets WHERE status IN ({placeholders})", pending_statuses)
    stats["total_pending"] = cursor.fetchone()[0]

    # 按 GPU 类型统计
    cursor.execute(f'''
        SELECT gpu_type, COUNT(*) FROM tickets
        WHERE status IN ({placeholders})
        GROUP BY gpu_type
    ''', pending_statuses)
    for row in cursor.fetchall():
        stats["by_gpu_type"][row[0] or "未知"] = row[1]

    # 按状态统计
    cursor.execute("SELECT status, COUNT(*) FROM tickets GROUP BY status")
    for row in cursor.fetchall():
        stats["by_status"][row[0] or "未知"] = row[1]

    # 获取所有申请中的工单详情
    cursor.execute(f'''
        SELECT ticket_id, requirement, gpu_type, status, applicant
        FROM tickets
        WHERE status IN ({placeholders})
        ORDER BY ticket_id DESC
    ''', pending_statuses)
    for row in cursor.fetchall():
        stats["tickets"].append({
            "id": row[0],
            "requirement": row[1],
            "gpu_type": row[2],
            "status": row[3],
            "applicant": row[4]
        })

    conn.close()
    return stats

# ============ 飞书推送 ============
def send_to_feishu(stats):
    """发送汇总报告到飞书"""

    # 构建 GPU 类型统计文本
    gpu_lines = []
    for gpu_type, count in stats["by_gpu_type"].items():
        gpu_lines.append(f"  • {gpu_type}: {count} 个工单")
    gpu_text = "\n".join(gpu_lines) if gpu_lines else "  暂无数据"

    # 构建状态统计文本
    status_lines = []
    for status, count in stats["by_status"].items():
        status_lines.append(f"  • {status}: {count} 个工单")
    status_text = "\n".join(status_lines) if status_lines else "  暂无数据"

    # 构建工单详情列表
    ticket_lines = []
    for ticket in stats.get("tickets", []):
        ticket_lines.append(f"  • [{ticket['id']}] {ticket['requirement']} | {ticket['gpu_type']} | {ticket['status']}")
    ticket_text = "\n".join(ticket_lines) if ticket_lines else "  暂无数据"

    # 飞书文本消息
    content = f"""📊 GPU 资源申请工单汇总

⏰ 统计时间: {stats['query_time']}

━━━━━━━━━━━━━━━━━━━━━━
📋 库存侧申请中的工单总数: {stats['total_pending']} 个工单
━━━━━━━━━━━━━━━━━━━━━━

📝 工单详情:
{ticket_text}

━━━━━━━━━━━━━━━━━━━━━━

🖥️ 按 GPU 类型统计:
{gpu_text}

━━━━━━━━━━━━━━━━━━━━━━

📌 按状态统计:
{status_text}
"""

    message = {
        "msg_type": "text",
        "content": {
            "text": content
        }
    }

    response = requests.post(FEISHU_WEBHOOK, json=message)
    if response.status_code == 200 and response.json().get("code") == 0:
        print("飞书推送成功")
    else:
        print(f"飞书推送失败: {response.text}")

    return response

# ============ 定时任务 ============
def scheduled_report():
    """定时汇总报告"""
    print(f"[{datetime.now()}] 执行定时汇总...")
    stats = get_statistics()
    send_to_feishu(stats)

# ============ 主程序 ============
def main():
    init_db()

    if len(sys.argv) < 2:
        print("用法:")
        print("  python gpu_resource_tracker.py import <文件>  - 导入 Excel/CSV 数据")
        print("  python gpu_resource_tracker.py report         - 立即发送汇总报告")
        print("  python gpu_resource_tracker.py schedule       - 启动定时任务（每2天）")
        print("  python gpu_resource_tracker.py test           - 测试飞书推送")
        return

    command = sys.argv[1]

    if command == "import":
        # 导入 Excel 数据
        if len(sys.argv) < 3:
            print("请指定文件路径，如: python gpu_resource_tracker.py import gpu_data.xlsx")
            return
        file_path = sys.argv[2]
        import_from_excel(file_path)

    elif command == "report":
        # 立即发送汇总报告
        stats = get_statistics()
        print(f"统计结果: {json.dumps(stats, ensure_ascii=False, indent=2)}")
        send_to_feishu(stats)

    elif command == "schedule":
        # 启动定时任务
        print("启动定时任务（每2天上午9点执行汇总）")
        print("保持此窗口运行，按 Ctrl+C 停止")
        schedule.every(2).days.at("09:00").do(scheduled_report)

        # 运行定时任务
        while True:
            schedule.run_pending()
            time.sleep(60)

    elif command == "test":
        # 测试飞书推送
        print("测试飞书推送...")
        test_stats = {
            "total_pending": 15,
            "by_gpu_type": {"4090": 8, "A100": 5, "H20": 2},
            "by_status": {"直属主管审批": 5, "资源需求处理中": 7, "已通过": 10, "运维资源确认": 3},
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        send_to_feishu(test_stats)

if __name__ == "__main__":
    main()
