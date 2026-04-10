import requests
import re
import yaml
import json
from bs4 import BeautifulSoup

def load_config(config_path='config.yaml'):
    """加载配置文件"""
    global config
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
    except FileNotFoundError:
        raise Exception(f"配置文件 {config_path} 不存在")
    except yaml.YAMLError as e:
        raise Exception(f"配置文件解析错误: {str(e)}")

# 加载配置
load_config() 

qwbotkey = config['qwbotkey']
PDDAccessToken = config['PDDAccessToken']

url = "https://mobile.pinduoduo.com/psnl_goods_help.html?_t_module_name=assistant_search&refer_scene=no_pickup_package_box"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Cookie": f"PDDAccessToken={PDDAccessToken}"
}

def clean_text(text):
    """去除多余空白和换行"""
    return re.sub(r'\s+', ' ', text).strip()


def send_message(idx, message):    
    print(f"开始发送消息{idx}")
    url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=' + qwbotkey
    messages = [
        f"多多驿站\n{message}",
    ]
    
    for message in messages:
        data = {
            "msgtype": "text",
            "text": {
                "content": message
            }
        }
        headers = {'Content-Type': 'application/json'}
        requests.post(url, headers=headers, data=json.dumps(data))
        
try:
    resp = requests.get(url, headers=headers, timeout=10)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'html.parser')

    # 1. 提取驿站/超市信息
    # 驿站名称：.company-name-text 中的文本（去除“支持退换货”标签）
    company_div = soup.select_one('.company-name-text')
    if company_div:
        # 获取所有文本，但去掉子标签 .suport-tag 的内容
        for tag in company_div.select('.suport-tag'):
            tag.decompose()
        station_name = clean_text(company_div.get_text())
    else:
        station_name = "未知驿站"

    # 驿站地址
    address_div = soup.select_one('.station-address')
    station_address = clean_text(address_div.get_text()) if address_div else "未知地址"

    # 待取件总数
    num_span = soup.select_one('.tip .num')
    total_packages = int(num_span.get_text()) if num_span else 0

    print(f"驿站名称：{station_name}")
    print(f"驿站地址：{station_address}")
    print(f"今日待取快递数：{total_packages}\n")

    # 2. 提取每个包裹的信息
    package_items = soup.select('.express-package-item')
    if not package_items:
        print("未找到包裹列表，请检查页面结构或 Cookie 是否有效。")
    else:
        print(f"共找到 {len(package_items)} 个包裹：\n")
        packages = []
        for idx, item in enumerate(package_items, 1):
            # 取件码
            pick_code_div = item.select_one('.pick-code')
            if pick_code_div:
                pick_text = pick_code_div.get_text(strip=True)
                match = re.search(r'(\d+-\d+-\d+)', pick_text)
                pick_code = match.group(1) if match else pick_text
            else:
                pick_code = "未找到"

            # 快递公司
            shipping_span = item.select_one('.shipping-name')
            shipping_company = shipping_span.get_text(strip=True) if shipping_span else "未知快递"

            # 运单号
            shipping_detail = item.select_one('.shipping-detail')
            if shipping_detail:
                full_text = shipping_detail.get_text(strip=True)
                # 运单号通常在快递公司名称之后
                tracking_no = full_text.replace(shipping_company, "").strip()
            else:
                tracking_no = "未找到"

            packages.append({
                "快递公司": shipping_company,
                "运单号": tracking_no,
                "取件码": pick_code
            })

            # 发送消息
            send_message(idx, f"包裹 {idx}\n快递公司: {shipping_company}\n运单号: {tracking_no}\n取件码: {pick_code}")

            print(f"包裹 {idx}:")
            print(f"  快递公司: {shipping_company}")
            print(f"  运单号:   {tracking_no}")
            print(f"  取件码:   {pick_code}")
            print("-" * 30)

        # 可选：输出结构化 JSON
        # import json
        # result = {
        #     "station_name": station_name,
        #     "station_address": station_address,
        #     "total_packages": total_packages,
        #     "packages": packages
        # }
        # print(json.dumps(result, ensure_ascii=False, indent=2))

except Exception as e:
    print(f"请求失败：{e}")