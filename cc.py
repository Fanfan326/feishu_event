import sys
import re
import requests
import os
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from feishu_webhook import FeishuWebhook
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 飞书 Webhook URL（从环境变量读取）
WEBHOOK_URL = os.getenv("FEISHU_WEBHOOK_URL")

# Grafana 配置（从环境变量读取）
GRAFANA_URL = os.getenv("GRAFANA_URL")
GRAFANA_API_KEY = os.getenv("GRAFANA_API_KEY")
# Grafana 面板查询 API 端点
GRAFANA_PANEL_QUERY_URL = os.getenv("GRAFANA_DASHBOARD_URL", "") + "&from=now-5m&to=now"


def input_multiline_text():
    """
    支持多行文本输入
    支持两种输入方式：
    1. 单行输入多个内容，用空格分隔，自动换行
    2. 多行输入，每行输入后按 Enter
    """
    print("=" * 60)
    print("多行文本输入")
    print("=" * 60)
    print("提示：")
    print("  - 方式1: 单行输入多个内容，用空格分隔（如：文本1 文本2 文本3）")
    print("  - 方式2: 每行输入后按 Enter 继续下一行")
    print("  - 输入 'END' 结束输入并发送")
    print("  - 输入空行作为段落分隔（保留空行）")
    print("  - 输入 'CANCEL' 取消发送")
    print("=" * 60)
    
    lines = []
    line_number = 1
    
    while True:
        # 提示输入（不 strip，保留原始输入）
        prompt = f"请输入要发送的文本行 {line_number} (Enter 继续，输入 END 结束): "
        user_input = input(prompt)
        
        # 检查取消命令
        if user_input.strip().upper() == 'CANCEL':
            print("❌ 已取消发送")
            return None
        
        # 检查结束命令
        if user_input.strip().upper() == 'END':
            if line_number == 1:
                print("⚠️  至少需要输入一行内容")
                continue
            break
        
        # 处理空行
        if not user_input.strip():
            lines.append('')
            print(f"✅ 已添加第 {line_number} 行: (空行 - 段落分隔)")
            line_number += 1
            continue
        
        # 检查是否包含空格（可能是多个内容用空格分隔）
        if ' ' in user_input.strip():
            # 按空格分割，但保留连续空格的处理
            parts = user_input.split()
            if len(parts) > 1:
                # 多个内容，分别添加为多行
                for part in parts:
                    if part.strip():  # 忽略空字符串
                        lines.append(part.strip())
                        print(f"✅ 已添加第 {line_number} 行: {part.strip()}")
                        line_number += 1
                continue
        
        # 单行内容，直接添加
        lines.append(user_input.rstrip('\r\n'))
        print(f"✅ 已添加第 {line_number} 行: {user_input}")
        line_number += 1
    
    # 检查是否有非空内容
    has_content = any(line.strip() for line in lines)
    if not has_content:
        print("❌ 没有输入任何内容")
        return None
    
    # 将多行合并，使用 \n 连接
    result = '\n'.join(lines)
    
    print("\n" + "=" * 60)
    print("预览要发送的内容:")
    print("=" * 60)
    for i, line in enumerate(lines, 1):
        if line:
            print(f"行 {i}: {line}")
        else:
            print(f"行 {i}: (空行)")
    print("=" * 60)
    
    return result


def parse_grafana_url(url: str) -> dict:
    """
    解析 Grafana URL，提取 dashboard UID 和 panel ID
    
    Args:
        url: Grafana URL
        
    Returns:
        dict: 包含 dashboard_uid, panel_id, org_id, from_time, to_time
    """
    try:
        parsed = urlparse(url)
        path_parts = parsed.path.split('/')
        
        # 提取 dashboard UID（通常在 /d/ 后面）
        dashboard_uid = None
        if '/d/' in parsed.path:
            idx = path_parts.index('d')
            if idx + 1 < len(path_parts):
                dashboard_uid = path_parts[idx + 1]
        
        # 从查询参数中提取信息
        params = parse_qs(parsed.query)
        panel_id = params.get('viewPanel', [None])[0]
        org_id = params.get('orgId', ['1'])[0]
        from_time = params.get('from', ['now-2y'])[0]
        to_time = params.get('to', ['now'])[0]
        
        return {
            'dashboard_uid': dashboard_uid,
            'panel_id': panel_id,
            'org_id': org_id,
            'from': from_time,
            'to': to_time,
            'base_url': f"{parsed.scheme}://{parsed.netloc}"
        }
    except Exception as e:
        print(f"❌ 解析 Grafana URL 失败: {str(e)}")
        return None


def fetch_grafana_panel_data(grafana_url: str, api_key: str = None) -> str:
    """
    从 Grafana 获取面板数据并格式化为 Markdown
    
    Args:
        grafana_url: Grafana 面板 URL
        api_key: Grafana API Key（可选）
        
    Returns:
        str: 格式化的 Markdown 数据
    """
    try:
        # 解析 URL
        url_info = parse_grafana_url(grafana_url)
        if not url_info:
            return None
        
        dashboard_uid = url_info['dashboard_uid']
        panel_id = url_info['panel_id']
        base_url = url_info['base_url']
        org_id = url_info['org_id']
        
        # 设置请求头
        headers = {
            'Content-Type': 'application/json'
        }
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        # 获取 dashboard 信息
        dashboard_api_url = f"{base_url}/api/dashboards/uid/{dashboard_uid}"
        response = requests.get(dashboard_api_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"⚠️  无法获取 Grafana 数据 (状态码: {response.status_code})")
            print(f"   提示: 可能需要配置 Grafana API Key")
            return f"**Grafana 面板数据**\n\n面板 ID: {panel_id}\n仪表盘 UID: {dashboard_uid}\n\n⚠️  无法获取详细数据，请检查 API 权限或配置 API Key"
        
        dashboard_data = response.json()
        dashboard_info = dashboard_data.get('dashboard', {})
        panels = dashboard_info.get('panels', [])
        
        # 查找指定的面板
        panel_data = None
        for panel in panels:
            if str(panel.get('id')) == str(panel_id):
                panel_data = panel
                break
        
        if not panel_data:
            return f"**Grafana 面板数据**\n\n⚠️  未找到面板 ID: {panel_id}"
        
        panel_title = panel_data.get('title', '未命名面板')
        
        # 尝试获取面板的实际查询数据
        try:
            # 方法1: 使用 Grafana 面板查询 API
            panel_query_url = f"{base_url}/api/dashboards/uid/{dashboard_uid}/panels/{panel_id}/query"
            # 添加 orgId 到 URL 参数
            if org_id:
                panel_query_url += f"?orgId={org_id}"
            
            query_params = {
                'from': url_info['from'],
                'to': url_info['to']
            }
            
            print(f"   查询 URL: {panel_query_url}")
            print(f"   查询参数: from={url_info['from']}, to={url_info['to']}")
            
            query_response = requests.post(
                panel_query_url,
                headers=headers,
                json=query_params,
                timeout=15
            )
            
            if query_response.status_code == 200:
                query_data = query_response.json()
                # 添加调试信息
                print(f"✅ 成功获取查询数据")
                print(f"   数据格式: {type(query_data)}")
                if isinstance(query_data, dict):
                    print(f"   数据键: {list(query_data.keys())}")
                return format_query_results_as_markdown(panel_title, query_data, url_info)
            else:
                print(f"⚠️  面板查询 API 返回状态码: {query_response.status_code}")
                try:
                    error_info = query_response.json()
                    print(f"   错误信息: {error_info}")
                except:
                    print(f"   响应内容: {query_response.text[:200]}")
            
            # 方法2: 如果面板查询 API 失败，尝试使用数据源查询 API
            print(f"⚠️  尝试使用数据源查询 API...")
            
            targets = panel_data.get('targets', [])
            if targets:
                # 获取数据源信息
                datasource = targets[0].get('datasource', {})
                if isinstance(datasource, dict):
                    datasource_uid = datasource.get('uid', '')
                else:
                    datasource_uid = datasource
                
                if datasource_uid:
                    # 使用数据源查询 API
                    ds_query_url = f"{base_url}/api/datasources/proxy/uid/{datasource_uid}/query"
                    
                    queries = []
                    for target in targets:
                        query_item = {
                            'expr': target.get('expr', target.get('query', '')),
                            'refId': target.get('refId', 'A')
                        }
                        queries.append(query_item)
                    
                    query_payload = {
                        'queries': queries,
                        'from': url_info['from'],
                        'to': url_info['to']
                    }
                    
                    ds_response = requests.post(
                        ds_query_url,
                        headers=headers,
                        json=query_payload,
                        timeout=15
                    )
                    
                    if ds_response.status_code == 200:
                        ds_data = ds_response.json()
                        return format_query_results_as_markdown(panel_title, ds_data, url_info)
            
            # 如果都失败，返回面板配置信息
            return format_panel_info_as_markdown(panel_data, url_info)
            
        except Exception as query_error:
            print(f"⚠️  查询数据时出错: {str(query_error)}")
            # 如果查询失败，返回面板配置信息
            return format_panel_info_as_markdown(panel_data, url_info)
        
    except requests.exceptions.RequestException as e:
        return f"**Grafana 数据获取失败**\n\n错误: {str(e)}\n\n提示: 请检查网络连接或 Grafana API 配置"
    except Exception as e:
        return f"**Grafana 数据获取失败**\n\n错误: {str(e)}"


def fetch_grafana_panel_data_direct(query_url: str, api_key: str = None) -> str:
    """
    直接从 Grafana 查询 API 获取面板数据
    
    Args:
        query_url: Grafana 面板查询 API URL
        api_key: Grafana API Key
        
    Returns:
        str: 格式化的 Markdown 数据
    """
    try:
        # 设置请求头
        headers = {
            'Content-Type': 'application/json'
        }
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        # 解析 URL 获取参数
        parsed = urlparse(query_url)
        params = parse_qs(parsed.query)
        org_id = params.get('orgId', ['1'])[0]
        
        # 构建查询参数
        query_params = {
            'from': 'now-5m',
            'to': 'now'
        }
        
        print(f"   查询 URL: {query_url}")
        print(f"   查询参数: from={query_params['from']}, to={query_params['to']}")
        
        # 发送查询请求
        query_response = requests.post(
            query_url,
            headers=headers,
            json=query_params,
            timeout=15
        )
        
        if query_response.status_code != 200:
            print(f"⚠️  查询 API 返回状态码: {query_response.status_code}")
            try:
                error_info = query_response.json()
                print(f"   错误信息: {error_info}")
            except:
                print(f"   响应内容: {query_response.text[:200]}")
            return f"**Grafana 数据获取失败**\n\n状态码: {query_response.status_code}\n\n请检查 API 权限或网络连接。"
        
        query_data = query_response.json()
        print(f"✅ 成功获取查询数据")
        
        # 格式化数据
        url_info = {
            'from': query_params['from'],
            'to': query_params['to']
        }
        
        return format_query_results_as_markdown("Instance实时库存情况", query_data, url_info)
        
    except requests.exceptions.RequestException as e:
        return f"**Grafana 数据获取失败**\n\n错误: {str(e)}\n\n提示: 请检查网络连接或 Grafana API 配置"
    except Exception as e:
        return f"**Grafana 数据获取失败**\n\n错误: {str(e)}"


def format_query_results_as_markdown(panel_title: str, query_data: dict, url_info: dict) -> str:
    """
    将 Grafana 查询结果格式化为 Markdown 表格，每一行数据都清晰展示
    
    Args:
        panel_title: 面板标题
        query_data: Grafana 查询返回的数据
        url_info: URL 信息
        
    Returns:
        str: Markdown 格式的数据
    """
    markdown_content = f"**{panel_title}**\n\n"
    
    # 添加调试信息
    print(f"   处理查询数据，数据类型: {type(query_data)}")
    if isinstance(query_data, dict):
        print(f"   数据键: {list(query_data.keys())}")
    
    # 处理查询结果 - 支持多种数据格式
    results = query_data.get('results', {})
    frames = query_data.get('frames', [])
    
    print(f"   results: {len(results) if results else 0} 个结果")
    print(f"   frames: {len(frames) if frames else 0} 个帧")
    
    # 如果没有 results，尝试直接处理 frames
    if not results and frames:
        all_rows = []
        headers_set = set()
        
        for frame in frames:
            schema = frame.get('schema', {})
            fields = schema.get('fields', [])
            
            if not fields:
                continue
            
            # 获取字段名和类型
            field_info = []
            for field in fields:
                field_name = field.get('name', '')
                field_type = field.get('type', '')
                field_info.append({'name': field_name, 'type': field_type})
                if field_name:
                    headers_set.add(field_name)
            
            # 获取数据值
            data_values = frame.get('data', {}).get('values', [])
            
            if not data_values:
                continue
            
            # 转置数据：从列格式转为行格式
            num_rows = len(data_values[0]) if data_values else 0
            for row_idx in range(num_rows):
                row_data = {}
                for col_idx, field in enumerate(field_info):
                    field_name = field['name'] or f'Column{col_idx+1}'
                    if col_idx < len(data_values) and row_idx < len(data_values[col_idx]):
                        value = data_values[col_idx][row_idx]
                        # 格式化数值
                        if isinstance(value, (int, float)):
                            row_data[field_name] = value
                        else:
                            row_data[field_name] = str(value) if value is not None else ''
                    else:
                        row_data[field_name] = ''
                all_rows.append(row_data)
        
        if all_rows:
            print(f"   从 frames 中提取到 {len(all_rows)} 行数据")
            return format_rows_as_markdown_table(markdown_content, all_rows, headers_set, url_info)
        else:
            print(f"   ⚠️  frames 中没有有效数据")
    
    # 处理 results 格式
    if results:
        print(f"   处理 results 格式，包含 {len(results)} 个结果")
        all_rows = []
        headers_set = set()
        
        for ref_id, result in results.items():
            result_frames = result.get('frames', [])
            for frame in result_frames:
                schema = frame.get('schema', {})
                fields = schema.get('fields', [])
                
                if not fields:
                    continue
                
                # 获取字段名
                field_names = []
                for i, field in enumerate(fields):
                    field_name = field.get('name', f'Field{i+1}')
                    field_names.append(field_name)
                    headers_set.add(field_name)
                
                # 获取数据值
                data_values = frame.get('data', {}).get('values', [])
                
                if not data_values:
                    continue
                
                # 转置数据：从列格式转为行格式
                num_rows = len(data_values[0]) if data_values else 0
                for row_idx in range(num_rows):
                    row_data = {}
                    for col_idx, field_name in enumerate(field_names):
                        if col_idx < len(data_values) and row_idx < len(data_values[col_idx]):
                            value = data_values[col_idx][row_idx]
                            # 格式化数值
                            if isinstance(value, (int, float)):
                                row_data[field_name] = value
                            else:
                                row_data[field_name] = str(value) if value is not None else ''
                        else:
                            row_data[field_name] = ''
                    all_rows.append(row_data)
        
        if all_rows:
            print(f"   从 results 中提取到 {len(all_rows)} 行数据")
            return format_rows_as_markdown_table(markdown_content, all_rows, headers_set, url_info)
        else:
            print(f"   ⚠️  results 中没有有效数据")
    
    # 如果没有 results，尝试其他格式
    if 'data' in query_data:
        print(f"   尝试处理 'data' 字段")
        return format_data_as_markdown_table(panel_title, query_data['data'], url_info)
    
    # 如果没有数据，显示调试信息
    print(f"⚠️  未找到数据，显示调试信息")
    print(f"   query_data 类型: {type(query_data)}")
    if isinstance(query_data, dict):
        print(f"   query_data 内容: {str(query_data)[:500]}")
    
    markdown_content += "⚠️  查询结果为空\n\n"
    markdown_content += f"**调试信息:**\n"
    markdown_content += f"- 数据时间范围: {url_info['from']} 到 {url_info['to']}\n"
    markdown_content += f"- 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    if isinstance(query_data, dict):
        markdown_content += f"- 数据键: {', '.join(query_data.keys())}\n"
    markdown_content += f"\n请检查 Grafana 面板是否有数据，或检查 API 权限。"
    return markdown_content


def format_rows_as_markdown_table(markdown_content: str, all_rows: list, headers_set: set, url_info: dict) -> str:
    """
    将数据行格式化为 Markdown，每一行数据都清晰展示
    
    Args:
        markdown_content: 已有的 Markdown 内容
        all_rows: 数据行列表
        headers_set: 表头集合
        url_info: URL 信息
        
    Returns:
        str: 完整的 Markdown 格式数据
    """
    if not all_rows:
        markdown_content += "暂无数据\n\n"
        markdown_content += f"数据时间范围: {url_info['from']} 到 {url_info['to']}\n"
        markdown_content += f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return markdown_content
    
    # 确定表头顺序（保持原始顺序，如果可能）
    # 使用第一行的键顺序作为表头顺序
    if all_rows:
        first_row_keys = list(all_rows[0].keys())
        headers = [h for h in first_row_keys if h in headers_set]
        # 添加其他可能遗漏的头部
        for h in headers_set:
            if h not in headers:
                headers.append(h)
    else:
        headers = sorted(list(headers_set))
    
    # 添加标题行（字段名之间用多个空格分隔）
    header_values = []
    for header in headers:
        header_values.append(str(header))
    markdown_content += f"**标题行：**\n\n"
    markdown_content += f"{'   '.join(header_values)}\n\n"
    
    # 添加数据行，每一行都清晰展示
    for row_idx, row in enumerate(all_rows, 1):
        row_values = []
        for header in headers:
            value = row.get(header, '')
            # 格式化值
            if isinstance(value, float):
                # 保留适当的小数位数
                if value.is_integer():
                    row_values.append(str(int(value)))
                else:
                    row_values.append(f"{value:.2f}")
            elif value is None:
                row_values.append('')
            else:
                row_values.append(str(value))
        # 使用"行X: 字段1  字段2  字段3..."的格式
        markdown_content += f"**行{row_idx}:**\n\n"
        markdown_content += f"{'   '.join(row_values)}\n\n"
    
    markdown_content += f"数据时间范围: {url_info['from']} 到 {url_info['to']}\n"
    markdown_content += f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return markdown_content


def format_data_as_markdown_table(panel_title: str, data: list, url_info: dict) -> str:
    """
    将数据列表格式化为 Markdown 表格
    
    Args:
        panel_title: 面板标题
        data: 数据列表
        url_info: URL 信息
        
    Returns:
        str: Markdown 格式的数据
    """
    markdown_content = f"**{panel_title}**\n\n"
    
    if not data:
        markdown_content += "暂无数据\n\n"
        markdown_content += f"数据时间范围: {url_info['from']} 到 {url_info['to']}"
        return markdown_content
    
    # 如果是字典列表
    if isinstance(data[0], dict):
        headers = list(data[0].keys())
        markdown_content += "| " + " | ".join(headers) + " |\n"
        markdown_content += "| " + " | ".join(["---"] * len(headers)) + " |\n"
        
        for row in data:
            values = [str(row.get(header, '')) for header in headers]
            markdown_content += "| " + " | ".join(values) + " |\n"
    else:
        # 如果是简单列表，每行一个
        for item in data:
            markdown_content += f"- {item}\n"
    
    markdown_content += f"\n数据时间范围: {url_info['from']} 到 {url_info['to']}\n"
    markdown_content += f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return markdown_content


def format_panel_info_as_markdown(panel_data: dict, url_info: dict) -> str:
    """
    将面板配置信息格式化为 Markdown（备用方案）
    
    Args:
        panel_data: 面板配置数据
        url_info: URL 信息
        
    Returns:
        str: Markdown 格式的数据
    """
    panel_title = panel_data.get('title', '未命名面板')
    panel_type = panel_data.get('type', 'unknown')
    
    markdown_content = f"**{panel_title}**\n\n"
    markdown_content += f"面板类型: {panel_type}\n\n"
    
    # 显示查询信息
    targets = panel_data.get('targets', [])
    if targets:
        markdown_content += "**查询信息:**\n\n"
        for i, target in enumerate(targets, 1):
            expr = target.get('expr', target.get('query', ''))
            if expr:
                markdown_content += f"{i}. `{expr}`\n"
        markdown_content += "\n"
    
    markdown_content += f"数据时间范围: {url_info['from']} 到 {url_info['to']}\n"
    markdown_content += f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return markdown_content


def validate_webhook_url(url: str) -> bool:
    """
    验证 Webhook URL 格式
    
    Args:
        url: Webhook URL
        
    Returns:
        bool: URL 是否有效
    """
    if not url:
        return False
    
    # 检查基本格式
    if not url.startswith('https://'):
        print("❌ Webhook URL 必须以 https:// 开头")
        return False
    
    # 检查是否是飞书 URL
    if 'open.feishu.cn' not in url and 'larkoffice.com' not in url:
        print("⚠️  警告: 这可能不是飞书的 Webhook URL")
        print("   飞书 Webhook URL 通常包含: open.feishu.cn 或 larkoffice.com")
    
    # 检查是否包含 hook
    if '/hook/' not in url:
        print("⚠️  警告: Webhook URL 格式可能不正确")
        print("   正确的格式应该是: https://open.feishu.cn/open-apis/bot/v2/hook/...")
    
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("飞书 Webhook 消息发送工具")
    print("=" * 60)
    print("\n获取 Webhook URL 的方法:")
    print("  1. 在飞书群聊中，点击右上角设置")
    print("  2. 选择「群机器人」→「添加机器人」→「自定义机器人」")
    print("  3. 创建后复制 Webhook URL")
    print("=" * 60)
    
    # 使用代码中配置的 Webhook URL，或允许用户输入新的
    if "your-webhook-url-here" in WEBHOOK_URL:
        print("\n⚠️  检测到未配置的 Webhook URL")
        print("请在代码中配置 WEBHOOK_URL，或手动输入")
        webhook_url = input("\n请输入 Webhook URL: ").strip()
        if not webhook_url:
            print("❌ Webhook URL 不能为空")
            sys.exit(1)
    else:
        print(f"\n✅ 使用代码中配置的 Webhook URL")
        use_custom = input("是否使用其他 Webhook URL? (y/n，默认n): ").strip().lower()
        if use_custom == 'y':
            webhook_url = input("请输入 Webhook URL: ").strip()
            if not webhook_url:
                print("❌ Webhook URL 不能为空")
                sys.exit(1)
        else:
            webhook_url = WEBHOOK_URL
    
    # 验证 URL 格式
    if not validate_webhook_url(webhook_url):
        print("\n❌ Webhook URL 格式验证失败")
        retry = input("是否继续使用此 URL? (y/n): ").strip().lower()
        if retry != 'y':
            sys.exit(1)
    
    # 创建 webhook 客户端
    try:
        webhook = FeishuWebhook(webhook_url)
    except ValueError as e:
        print(f"❌ {str(e)}")
        sys.exit(1)
    
    # 选择消息类型
    print("\n选择消息类型:")
    print("1. 纯文本消息（多行）")
    print("2. Markdown 消息（多行）")
    print("3. 从 Grafana 获取数据并发送 Markdown 消息")
    print("0. 退出")
    
    choice = input("\n请选择 (0-3): ").strip()
    
    if choice == "0":
        print("退出")
        sys.exit(0)
    
    # 如果选择从 Grafana 获取数据
    if choice == "3":
        print("\n正在从 Grafana 获取数据...")
        content = fetch_grafana_panel_data_direct(GRAFANA_PANEL_QUERY_URL, GRAFANA_API_KEY)
        if not content:
            print("❌ 无法获取 Grafana 数据")
            sys.exit(1)
        print("\n✅ 成功获取 Grafana 数据")
        print("\n" + "=" * 60)
        print("预览要发送的内容:")
        print("=" * 60)
        print(content)
        print("=" * 60)
    else:
        # 获取多行输入
        content = input_multiline_text()
        
        if content is None:
            sys.exit(0)
    
    # 确认发送
    confirm = input("\n确认发送? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ 已取消发送")
        sys.exit(0)
    
    # 发送消息
    print("\n正在发送...")
    
    if choice == "1":
        # 发送纯文本消息
        success = webhook.send_text(content)
    elif choice == "2" or choice == "3":
        # 发送 Markdown 消息
        # 自动生成标题：日期 + "Instance实时库存情况"
        current_date = datetime.now().strftime("%Y%m%d")
        title = f"{current_date}Instance实时库存情况"
        print(f"\n自动生成的标题: {title}")
        success = webhook.send_markdown(title, content)
    else:
        print("❌ 无效的选择")
        sys.exit(1)
    
    if success:
        print("\n✅ 消息已成功发送到飞书！")
    else:
        print("\n❌ 消息发送失败")


if __name__ == "__main__":
    main()
