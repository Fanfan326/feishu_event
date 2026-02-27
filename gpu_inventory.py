"""
GPU 库存查询模块
通过 Grafana API 查询 GPU 库存数据
"""

import os
import requests
from typing import Optional, Dict, List, Tuple
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Grafana API 配置
GRAFANA_URL = os.getenv("GRAFANA_URL", "https://grafana.aicloud.paigod.work")
GRAFANA_API_KEY = os.getenv("GRAFANA_API_KEY")
GRAFANA_DATASOURCE_UID = os.getenv("GRAFANA_DATASOURCE_UID", "een5ao3qgwyrkc")

# 海外机房关键词
OVERSEAS_IDC_KEYWORDS = ["dallas", "canopy", "gcore"]

# 高主频机房关键词（供应商为 bingte）
HIGH_FREQ_IDC_KEYWORDS = ["bingte"]

# GPU 类型映射（用户输入 -> 数据库中的名称）
GPU_TYPE_MAP = {
    "5090": "NVIDIA GeForce RTX 5090",
    "4090": "NVIDIA GeForce RTX 4090",
    "3090": "NVIDIA GeForce RTX 3090",
    "H100": "NVIDIA H100 80GB HBM3",
    "H20": "NVIDIA H20",
    "H200": "NVIDIA H200",
    "A100": "NVIDIA A100-SXM4-80GB",
    "L40S": "NVIDIA L40S",
    "5880": "NVIDIA RTX 5880 Ada Generation",
    "6000": "NVIDIA RTX 6000 Ada Generation",
}


def query_grafana(sql: str) -> List[Dict]:
    """
    通过 Grafana API 执行 SQL 查询

    Args:
        sql: SQL 查询语句

    Returns:
        查询结果列表，每个元素是一个字典
    """
    if not GRAFANA_API_KEY:
        raise ValueError("GRAFANA_API_KEY 未配置")

    url = f"{GRAFANA_URL}/api/ds/query"
    headers = {
        "Authorization": f"Bearer {GRAFANA_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "queries": [
            {
                "datasource": {"type": "mysql", "uid": GRAFANA_DATASOURCE_UID},
                "rawSql": sql,
                "format": "table",
                "refId": "A"
            }
        ]
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        # 解析 Grafana 返回的数据格式
        if "results" in data and "A" in data["results"]:
            frames = data["results"]["A"].get("frames", [])
            if frames:
                frame = frames[0]
                schema = frame.get("schema", {}).get("fields", [])
                values = frame.get("data", {}).get("values", [])

                # 构建列名到索引的映射
                columns = [field["name"] for field in schema]

                # 转换为字典列表
                rows = []
                if values and len(values) > 0:
                    num_rows = len(values[0]) if values[0] else 0
                    for i in range(num_rows):
                        row = {}
                        for j, col_name in enumerate(columns):
                            row[col_name] = values[j][i] if j < len(values) else None
                        rows.append(row)

                return rows

        return []
    except Exception as e:
        print(f"Grafana API 查询失败: {e}")
        return []


def is_overseas_idc(idc: str) -> bool:
    """判断是否为海外机房"""
    if not idc:
        return False
    idc_lower = idc.lower()
    return any(keyword in idc_lower for keyword in OVERSEAS_IDC_KEYWORDS)


def is_high_freq_idc(idc: str) -> bool:
    """判断是否为高主频机房（bingte 供应商）"""
    if not idc:
        return False
    idc_lower = idc.lower()
    return any(keyword in idc_lower for keyword in HIGH_FREQ_IDC_KEYWORDS)


def get_all_gpu_inventory(region: str = None, high_freq: bool = None) -> List[Dict]:
    """
    获取所有 GPU 库存汇总

    Args:
        region: "国内" 或 "海外"，None 表示全部
        high_freq: True 表示高主频，False 表示普通，None 表示全部
    """
    sql = '''
        SELECT
            gpu_product_name,
            idc,
            SUM(total_gpu_num) as total,
            SUM(free_gpu_num) as free,
            SUM(used_gpu_num) as used,
            SUM(unavailable_gpu_num) as unavailable
        FROM nexus.nexus_nodes_v2
        WHERE (deleted_time IS NULL OR deleted_time = 0)
          AND gpu_product_name != ''
        GROUP BY gpu_product_name, idc
    '''

    rows = query_grafana(sql)

    # 按 GPU 类型和高主频/普通分类汇总
    gpu_data = {}  # key: (gpu_name, is_high_freq), value: {total, free, used, unavailable}

    for row in rows:
        gpu_name = row.get("gpu_product_name", "")
        idc = row.get("idc", "")
        total = row.get("total", 0) or 0
        free = row.get("free", 0) or 0
        used = row.get("used", 0) or 0
        unavailable = row.get("unavailable", 0) or 0

        # 区域过滤
        is_overseas = is_overseas_idc(idc)
        if region == "海外" and not is_overseas:
            continue
        if region == "国内" and is_overseas:
            continue

        # 高主频过滤
        is_high = is_high_freq_idc(idc)
        if high_freq is True and not is_high:
            continue
        if high_freq is False and is_high:
            continue

        # 汇总
        key = (gpu_name, is_high)
        if key not in gpu_data:
            gpu_data[key] = {"total": 0, "free": 0, "used": 0, "unavailable": 0}

        gpu_data[key]["total"] += total
        gpu_data[key]["free"] += free
        gpu_data[key]["used"] += used
        gpu_data[key]["unavailable"] += unavailable

    # 转换为列表格式
    result = []
    for (gpu_name, is_high), data in gpu_data.items():
        result.append({
            "name": gpu_name,
            "is_high_freq": is_high,
            "total": data["total"],
            "free": data["free"],
            "used": data["used"],
            "unavailable": data["unavailable"]
        })

    # 按总数降序排序
    result.sort(key=lambda x: x["total"], reverse=True)
    return result


def get_gpu_inventory_by_type(gpu_type: str, region: str = None, high_freq: bool = None) -> Optional[Dict]:
    """
    按 GPU 类型查询库存

    Args:
        gpu_type: GPU 类型，如 "4090", "H100"
        region: "国内" 或 "海外"，None 表示全部
        high_freq: True 表示高主频，False 表示普通，None 表示全部
    """
    # 映射用户输入到数据库名称
    gpu_type_upper = gpu_type.upper()
    db_gpu_name = GPU_TYPE_MAP.get(gpu_type_upper)

    if db_gpu_name:
        # 精确匹配
        sql = f'''
            SELECT
                gpu_product_name,
                idc,
                SUM(total_gpu_num) as total,
                SUM(free_gpu_num) as free,
                SUM(used_gpu_num) as used,
                SUM(unavailable_gpu_num) as unavailable
            FROM nexus.nexus_nodes_v2
            WHERE (deleted_time IS NULL OR deleted_time = 0)
              AND gpu_product_name = '{db_gpu_name}'
            GROUP BY gpu_product_name, idc
        '''
    else:
        # 模糊匹配
        sql = f'''
            SELECT
                gpu_product_name,
                idc,
                SUM(total_gpu_num) as total,
                SUM(free_gpu_num) as free,
                SUM(used_gpu_num) as used,
                SUM(unavailable_gpu_num) as unavailable
            FROM nexus.nexus_nodes_v2
            WHERE (deleted_time IS NULL OR deleted_time = 0)
              AND gpu_product_name LIKE '%{gpu_type}%'
            GROUP BY gpu_product_name, idc
        '''

    rows = query_grafana(sql)

    # 汇总数据
    result = {"total": 0, "free": 0, "used": 0, "unavailable": 0, "name": None}

    for row in rows:
        gpu_name = row.get("gpu_product_name", "")
        idc = row.get("idc", "")
        total = row.get("total", 0) or 0
        free = row.get("free", 0) or 0
        used = row.get("used", 0) or 0
        unavailable = row.get("unavailable", 0) or 0

        # 区域过滤
        is_overseas = is_overseas_idc(idc)
        if region == "海外" and not is_overseas:
            continue
        if region == "国内" and is_overseas:
            continue

        # 高主频过滤
        is_high = is_high_freq_idc(idc)
        if high_freq is True and not is_high:
            continue
        if high_freq is False and is_high:
            continue

        result["name"] = gpu_name
        result["total"] += total
        result["free"] += free
        result["used"] += used
        result["unavailable"] += unavailable

    if result["name"]:
        result["is_high_freq"] = high_freq if high_freq is not None else False
        return result
    return None


def get_gpu_inventory_by_region(gpu_type: str = None, region: str = None) -> List[Dict]:
    """按地区查询 GPU 库存"""
    sql = '''
        SELECT
            gpu_product_name,
            idc,
            SUM(total_gpu_num) as total,
            SUM(free_gpu_num) as free,
            SUM(used_gpu_num) as used
        FROM nexus.nexus_nodes_v2
        WHERE (deleted_time IS NULL OR deleted_time = 0)
          AND gpu_product_name != ''
    '''

    if gpu_type:
        gpu_type_upper = gpu_type.upper()
        db_gpu_name = GPU_TYPE_MAP.get(gpu_type_upper)
        if db_gpu_name:
            sql += f" AND gpu_product_name = '{db_gpu_name}'"
        else:
            sql += f" AND gpu_product_name LIKE '%{gpu_type}%'"

    sql += ' GROUP BY gpu_product_name, idc ORDER BY total DESC'

    rows = query_grafana(sql)

    result = []
    for row in rows:
        idc = row.get("idc", "")

        # 区域过滤
        is_overseas = is_overseas_idc(idc)
        if region == "海外" and not is_overseas:
            continue
        if region == "国内" and is_overseas:
            continue

        result.append({
            "name": row.get("gpu_product_name", ""),
            "idc": idc,
            "is_overseas": is_overseas,
            "is_high_freq": is_high_freq_idc(idc),
            "total": row.get("total", 0) or 0,
            "free": row.get("free", 0) or 0,
            "used": row.get("used", 0) or 0
        })

    return result


def format_inventory_message(inventory: List[Dict]) -> str:
    """格式化库存信息为消息"""
    if not inventory:
        return "暂无库存数据"

    lines = ["📊 GPU 库存汇总\n"]
    for item in inventory:
        # 简化 GPU 名称显示
        name = item["name"]
        for short, full in GPU_TYPE_MAP.items():
            if full == name:
                name = short
                break

        # 添加高主频标识
        if item.get("is_high_freq"):
            name = f"高主频{name}"

        lines.append(f"🖥️ {name}")
        lines.append(f"   总数: {item['total']} | 空闲: {item['free']} | 使用中: {item['used']}")
        lines.append("")

    return "\n".join(lines)


def format_single_gpu_message(gpu_info: Dict, high_freq: bool = None) -> str:
    """格式化单个 GPU 类型的库存信息"""
    if not gpu_info:
        return "未找到该 GPU 类型的库存信息"

    name = gpu_info["name"]
    for short, full in GPU_TYPE_MAP.items():
        if full == name:
            name = short
            break

    # 添加高主频标识
    if high_freq is True or gpu_info.get("is_high_freq"):
        name = f"高主频{name}"

    return f"""🖥️ {name} 库存

总数: {gpu_info['total']} 卡
空闲: {gpu_info['free']} 卡
使用中: {gpu_info['used']} 卡
不可用: {gpu_info['unavailable']} 卡"""


def parse_user_question(text: str) -> Tuple[Optional[str], Optional[str], Optional[bool]]:
    """
    解析用户问题，提取 GPU 类型、地区和是否高主频
    返回: (gpu_type, region, high_freq)
    """
    text_upper = text.upper()
    text_lower = text.lower()

    # 识别 GPU 类型
    gpu_type = None
    for short_name in GPU_TYPE_MAP.keys():
        if short_name in text_upper:
            gpu_type = short_name
            break

    # 识别地区
    region = None
    if "国内" in text or "中国" in text:
        region = "国内"
    elif "海外" in text or "国外" in text:
        region = "海外"

    # 识别高主频
    high_freq = None
    if "高主频" in text or "bingte" in text_lower:
        high_freq = True
    elif "普通" in text or "非高主频" in text:
        high_freq = False

    return gpu_type, region, high_freq


async def get_gpu_availability(gpu_type: str, region: str = None, high_freq: bool = None) -> Optional[int]:
    """
    获取指定 GPU 类型的可用卡数
    用于飞书机器人问答
    """
    gpu_info = get_gpu_inventory_by_type(gpu_type, region=region, high_freq=high_freq)
    if gpu_info:
        return gpu_info["free"]
    return None


# 测试
if __name__ == "__main__":
    print("=== 测试 GPU 库存查询 ===\n")

    # 查询所有库存
    print("1. 所有 GPU 库存:")
    all_inventory = get_all_gpu_inventory()
    print(format_inventory_message(all_inventory))

    print("\n" + "="*50 + "\n")

    # 查询国内普通 4090
    print("2. 查询国内普通 4090 库存:")
    gpu_4090 = get_gpu_inventory_by_type("4090", region="国内", high_freq=False)
    print(format_single_gpu_message(gpu_4090))

    print("\n" + "="*50 + "\n")

    # 查询国内高主频 4090
    print("3. 查询国内高主频 4090 库存:")
    gpu_4090_high = get_gpu_inventory_by_type("4090", region="国内", high_freq=True)
    print(format_single_gpu_message(gpu_4090_high, high_freq=True))

    print("\n" + "="*50 + "\n")

    # 查询海外 4090
    print("4. 查询海外 4090 库存:")
    gpu_4090_overseas = get_gpu_inventory_by_type("4090", region="海外")
    print(format_single_gpu_message(gpu_4090_overseas))

    print("\n" + "="*50 + "\n")

    # 查询 5090 库存
    print("5. 查询 5090 库存:")
    gpu_5090 = get_gpu_inventory_by_type("5090")
    print(format_single_gpu_message(gpu_5090))

    print("\n" + "="*50 + "\n")

    # 测试解析用户问题
    print("6. 测试解析用户问题:")
    test_questions = [
        "4090有多少卡",
        "查一下5090库存",
        "H100还有多少",
        "国内A100库存",
        "高主频4090有多少",
        "国内高主频5090库存",
        "海外4090还有吗",
    ]
    for q in test_questions:
        gpu_type, region, high_freq = parse_user_question(q)
        print(f"  问题: {q} -> GPU: {gpu_type}, 地区: {region}, 高主频: {high_freq}")
