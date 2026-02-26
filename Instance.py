#!/usr/bin/env python3
import asyncio
import httpx
import logging
import datetime
import os
import tempfile
import schedule
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

try:
    from report_excel import logger
except ImportError:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("./feishu_sla_report.log"),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger()

# 从环境变量读取配置
WEBHOOK_URL = os.getenv("FEISHU_WEBHOOK_URL")
HEADERS = {"Content-Type": "application/json"}
TITLE_NAME = "GPU库存监控"
APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
GRAFANA_URL = os.getenv("GRAFANA_URL")
GRAFANA_DASHBOARD_URL = os.getenv("GRAFANA_DASHBOARD_URL")
GRAFANA_API_KEY = os.getenv("GRAFANA_API_KEY")
SCREENSHOT_WIDTH = 1920
SCREENSHOT_HEIGHT = 1200
SCREENSHOT_WAIT_TIME = 2000  
TIME_RANGE_MINUTES = 5
def get_time_range_params():
    now = datetime.datetime.now()
    end_time = now
    start_time = now - datetime.timedelta(minutes=TIME_RANGE_MINUTES)
    from_ts = int(start_time.timestamp() * 1000)
    to_ts = int(end_time.timestamp() * 1000)
    return from_ts, to_ts, start_time, end_time
def get_grafana_url_with_time():
    from_ts, to_ts, _, _ = get_time_range_params()
    base_url = GRAFANA_DASHBOARD_URL.split('?')[0]
    params = GRAFANA_DASHBOARD_URL.split('?')[1] if '?' in GRAFANA_DASHBOARD_URL else ''
    param_list = []
    if params:
        for param in params.split('&'):
            if not param.startswith(('from=', 'to=', 'time=')):
                param_list.append(param)
    param_list.append(f"from={from_ts}")
    param_list.append(f"to={to_ts}")
    return f"{base_url}?{'&'.join(param_list)}"
def build_card_data(screenshot_key=None):
    _, _, start_time, end_time = get_time_range_params()
    dashboard_url = get_grafana_url_with_time()
    sla_data = {
        "MONITOR_DASHBOARD_LINK": dashboard_url,
        "MONITORTYPE": "GPU库存监控",
        "MONITORNAME": "GPU库存监控",
        "INCIDENT_TIME_ISO": f"{start_time.strftime('%Y-%m-%d %H:%M:%S')} 至 {end_time.strftime('%Y-%m-%d %H:%M:%S')}",
    }
    FIELD_MAPPING = [
        ("MONITOR_DASHBOARD_LINK", "监控仪表盘链接"),
        ("MONITORTYPE", "监控类型"),
        ("MONITORNAME", "监控名称"),
    ]
    fields = []
    for key, display_name in FIELD_MAPPING:
        value = sla_data.get(key, "N/A")
        if key == "MONITOR_DASHBOARD_LINK" and value != "N/A":
            value = f"[点击查看]({value})"
        fields.append({
            "is_short": False,
            "text": {
                "tag": "lark_md",
                "content": f"{display_name}:  {value}\n"
            }
        })
    fields.append({
        "is_short": False,
        "text": {
            "tag": "lark_md",
            "content": f"时间范围:  {sla_data.get('INCIDENT_TIME_ISO', 'N/A')}\n"
        }
    })
    elements = [
        {"tag": "hr"},
        {"tag": "div", "fields": fields}
    ]
    if screenshot_key:
        elements.append({
            "tag": "img",
            "img_key": screenshot_key,
            "alt": {"tag": "plain_text", "content": "Grafana监控截图"}
        })
    card_template = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": f"[{TITLE_NAME}]"},
                "template": "red"
            },
            "elements": elements
        }
    }
    return card_template
async def capture_grafana_screenshot():
    if not GRAFANA_API_KEY:
        logger.warning("未配置Grafana API Token，跳过截图")
        return None
    try:
        from playwright.async_api import async_playwright
        temp_dir = tempfile.gettempdir()
        screenshot_path = os.path.join(temp_dir, "grafana_screenshot.png")
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            context = await browser.new_context(
                viewport={"width": SCREENSHOT_WIDTH, "height": SCREENSHOT_HEIGHT}
            )
            page = await context.new_page()
            await page.set_extra_http_headers({
                "Authorization": f"Bearer {GRAFANA_API_KEY}"
            })
            grafana_url = get_grafana_url_with_time()
            kiosk_url = grafana_url + "&kiosk"
            logger.info(f"访问Grafana URL: {kiosk_url}")
            await page.goto(kiosk_url, wait_until="networkidle")
            logger.info(f"等待 {SCREENSHOT_WAIT_TIME/1000} 秒让图表渲染")
            await page.wait_for_timeout(SCREENSHOT_WAIT_TIME)
            await page.evaluate("""() => {
                const elementsToHide = [
                    '.navbar', '.sidemenu', '.grafana-app-header',
                    '.page-toolbar', '.page-header', '.panel-header'
                ];
                elementsToHide.forEach(selector => {
                    document.querySelectorAll(selector).forEach(el => {
                        el.style.display = 'none';
                    });
                });
            }""")
            await page.wait_for_timeout(500)
            await page.screenshot(path=screenshot_path, full_page=True)
            logger.info(f"截图已保存: {screenshot_path}")
            await browser.close()
        image_key = await upload_image_to_feishu(screenshot_path)
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)
        return image_key
    except Exception as e:
        logger.error(f"获取Grafana截图失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None
async def get_tenant_access_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code", 0) == 0:
            return data["tenant_access_token"]
        else:
            logger.error(f"获取tenant_access_token失败: {data}")
            return None
async def upload_image_to_feishu(file_path):
    tenant_access_token = await get_tenant_access_token()
    if not tenant_access_token:
        logger.error("无法获取tenant_access_token，图片上传中止")
        return None
    url = "https://open.feishu.cn/open-apis/im/v1/images"
    headers = {"Authorization": f"Bearer {tenant_access_token}"}
    try:
        with open(file_path, "rb") as f:
            files = {"image": (os.path.basename(file_path), f, "image/png")}
            form_data = {"image_type": "message"}
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, headers=headers, data=form_data, files=files)
                resp.raise_for_status()
                data = resp.json()
                if data.get("code", 0) == 0:
                    image_key = data["data"]["image_key"]
                    logger.info(f"图片上传成功，image_key: {image_key}")
                    return image_key
                else:
                    logger.error(f"图片上传失败: {data}")
                    return None
    except Exception as e:
        logger.error(f"上传图片到飞书失败: {str(e)}")
        return None
async def send_feishu_message():
    screenshot_key = await capture_grafana_screenshot()
    card_data = build_card_data(screenshot_key)
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                WEBHOOK_URL,
                json=card_data,
                headers=HEADERS
            )
            response.raise_for_status()
            result = response.json()
            if result.get("code", 0) == 0:
                logger.info("发送飞书消息成功")
                return True
            else:
                logger.error(f"发送飞书消息失败: {result}")
                return False
    except httpx.TimeoutException:
        logger.error("发送请求超时")
        return False
    except httpx.HTTPError as e:
        logger.error(f"HTTP错误: {e}")
        return False
    except Exception as e:
        logger.error(f"未知错误: {e}")
        return False
def send_message_job():
    """定时任务：发送消息"""
    logger.info("=" * 60)
    logger.info("定时任务触发：开始发送GPU库存监控到飞书")
    logger.info(f"查询时间范围: 过去{TIME_RANGE_MINUTES}分钟")
    success = asyncio.run(send_feishu_message())
    if success:
        logger.info("GPU库存监控发送完成")
    else:
        logger.warning("GPU库存监控发送失败")
    logger.info("=" * 60)

def main():
    """主函数"""
    import sys
    
    # 检查是否有命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # 立即发送一次
        logger.info("立即发送模式：开始发送GPU库存监控到飞书")
        logger.info(f"查询时间范围: 过去{TIME_RANGE_MINUTES}分钟")
        success = asyncio.run(send_feishu_message())
        if success:
            logger.info("GPU库存监控发送完成")
        else:
            logger.warning("GPU库存监控发送失败")
        return
    
    # 定时任务已取消
    logger.info("=" * 60)
    logger.info("GPU库存监控")
    logger.info("=" * 60)
    logger.info("⚠️  定时任务已取消")
    logger.info("💡 使用 --once 参数可立即发送一次")
    logger.info("💡 或在飞书群里@机器人自动同步")
    logger.info("=" * 60)
    
    # 定时任务代码已注释
    # schedule.every().hour.at(":10").do(send_message_job)
    # 
    # next_run = schedule.next_run()
    # if next_run:
    #     logger.info(f"下次执行时间: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    # 
    # try:
    #     while True:
    #         schedule.run_pending()
    #         time.sleep(60)
    # except KeyboardInterrupt:
    #     logger.info("\n程序已停止")

if __name__ == "__main__":
    main()