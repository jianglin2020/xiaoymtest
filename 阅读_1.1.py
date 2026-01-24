import random
import requests
import time
import yaml
import json
import re
import sys
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

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
xyy_config = config['xyy_config']

# 判断是否系统维护
def is_maintenance():
    url = f"http://t510514s.weifangqr.cn/jxybyy/6d288b175355d987746598c6c11c0227?mid=815"

    response = requests.get(url,headers={'User-Agent': random.choice(config['ua_list'])},timeout=20)

    """用bool()转换"""
    return bool(re.search(r'系统维护中，近期价格低', response.text))

class GoldCollector:
    def __init__(self, account):
        self.session = requests.Session()
        self.account = account
        # self.base_url = 'http://5cd20cc.window-repair-200.site'
        self.base_url = 'http://375cbec.t3h1w6.cn'

        self.headers = {'User-Agent': random.choice(config['ua_list'])}
        self.cookies = {'ejectCode': '1', 'ysmuid': account["ysmuid"]}

    def sleep_with_countdown(self, sleep_time):
        """带倒计时显示的sleep"""
        for remaining in range(sleep_time, 0, -1):
            print(f"\r{self.account['name']}_剩余等待时间: {remaining}秒", end="", flush=True)
            time.sleep(1)
        print(f"\r{self.account['name']}等待完成！" + " " * 20)  # 清除行尾

    def extract_params_from_html(self, html_content):
        """从HTML中提取关键参数"""
        # 提取domain
        domain_match = re.search(r'var domain\s*=\s*["\'](.*?)["\']', html_content)
        if domain_match:
            self.domain = domain_match.group(1)
        
        # 提取unionid
        unionid_match = re.search(r'var unionid\s*=\s*[\'"](.*?)[\'"]', html_content)
        if unionid_match:
            self.unionid = unionid_match.group(1)
        
        # 提取request_id
        request_id_match = re.search(r'var request_id\s*=\s*["\'](.*?)["\']', html_content)
        if request_id_match:
            self.request_id = request_id_match.group(1)

    # 获取 domain_url
    def get_domain_url(self):
        # url = f"{self.base_url}/xyysofttmplik"
        url = f"{self.base_url}/xiaoxinxin/duliks"

        data = {
            'unionid': self.account['unionid'],
        }

        try:
            response = self.session.post(
                url,
                headers=self.headers,
                data=data,
                cookies=self.cookies,
                timeout=20
            )
            response.raise_for_status()
            result = response.json()

            if result.get('errcode') == 0:
                data = result.get('data', {})
                query_value = re.search(r'query=([^&]+)', data['domain']).group(1)

                print(f"🚗 domain地址：{query_value}")

                return query_value
            else:
                print(f"获取失败: {result.get('msg', '未知错误')}")
                return None
                    
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {str(e)}")
            return None

    def get_sign_info(self):
        """获取初始页面并解析关键参数"""
        url = f"{self.base_url}/xiaoxinxin/home.html"
        params = {
          #'inviteid': 0
          'ysi': 0
        }

        try:
            response = self.session.get(
                url,
                headers=self.headers,
                params=params,
                cookies={'ysmuid': self.account["ysmuid"]},  # 直接使用值，不要外加 {}
                timeout=20
            )
            response.raise_for_status()
            if response.status_code == 200: 
                text = response.text
                print(f"🎉 登陆成功") 
                pattern = r"(exchange\?.+?)['\"]"
                match = re.search(pattern, text)

                if match:
                    full_exchange_part = match.group(1)
                    self.full_exchange_part = full_exchange_part

        except requests.exceptions.RequestException as e:
            print(f"请求异常: {str(e)}")
            return None 

    # 提现初始
    def get_initial_page(self):
        """获取初始页面并解析关键参数"""
        # url = f"{self.base_url}/yunonline/v1/{self.full_exchange_part}"
        url = f"{self.base_url}/xiaoxinxin/{self.full_exchange_part}"

        response = self.session.get(url, headers=self.headers, cookies=self.cookies)

        # 保存到当前目录的 response.txt
        # with open("response.html", "w", encoding="utf-8") as f:
        #     f.write(response.text)
        # 获取提现参数
        self.extract_params_from_html(response.text)

        goid = self.get_gold_balance()

        if int(goid) >= 5000:
            # 提现
            print(f"🎉 开始提现到微信！")
            self.get_user_gold()
            self.withdraw_to_wechat()
        else:
            print('🎉 金币不足5000!')
        print("内容已保存到 response.html")
        return response.text

    # 金币转余额
    def get_user_gold(self):
        """金币转余额"""
        # url = urljoin(self.domain, "withdraw")
        url = f"{self.base_url}/xiaoxinxin/user_gold"

        data = f"unionid={self.unionid}&request_id={self.request_id}&gold=5000"

        headers = {
            'User-Agent': random.choice(config['ua_list']),
            'Accept': "application/json, text/javascript, */*; q=0.01",
            'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8"
        }

        response = self.session.post(
            url, 
            data=data,
            headers=headers,
            cookies={'ysmuid': self.account["ysmuid"]},  # 直接使用值，不要外加 {}
            timeout=15)

        print(response.json())    
       

    # 提现到微信
    def withdraw_to_wechat(self):
        """提现到微信钱包"""
        # url = urljoin(self.domain, "withdraw")
        url = f"{self.base_url}/xiaoxinxin/withdraw"

        data = f"unionid={self.unionid}&signid={self.request_id}&ua=0&ptype=0&paccount=&pname="

        headers = {
            'User-Agent': random.choice(config['ua_list']),
            'Accept': "application/json, text/javascript, */*; q=0.01",
            'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8"
        }

        try:
            response = self.session.post(
                url, 
                data=data,
                headers=headers,
                cookies={'ysmuid': self.account["ysmuid"]},  # 直接使用值，不要外加 {}
                timeout=15)

            print(response.json())    
            if response.json().get("errcode") == 0:
                print("微信提现成功！请返回微信查看")
                return True
            else:
                print(f"微信提现失败: {response.json().get('msg', '未知错误')}")
                return False
        except Exception as e:
            print(f"微信提现请求失败: {str(e)}")
            return False

    def get_gold_balance(self):
        """获取金币余额"""
        url = f"{self.base_url}/xiaoxinxin/gold"

        params = {
            'unionid': self.account['unionid'],
            'time': int(time.time() * 1000)  # 生成13位时间戳
        }

        try:
            response = self.session.get(
                url,
                headers=self.headers,
                params=params,
                cookies={'ysmuid': self.account["ysmuid"]},  # 直接使用值，不要外加 {}
                timeout=20
            )
            response.raise_for_status()
            result = response.json()

            print(result)
            if result.get('errcode') == 0:
                data = result.get('data', {})
                print(f"🎉 今日阅读：{data['day_read']}")
                print(f"🎉 金币剩余：{data['last_gold']}")
                print(f"🎉 今日奖励：{data['day_gold']}")
                return result.get('data', {}).get('last_gold', 0)
            else:
                print(f"获取余额失败: {result.get('msg', '未知错误')}")
                return None
                    
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {str(e)}")
            return None

    def request_article(self, domain_url):
        """请求文章链接"""
        # http://sr1206.3b3d0b936.okapdf089.asia/siyxaygty?xsyfew=026513654eead334c509b0632cb651ba&time=1765338846000&psgn=168&vs=1002
        # http://f0104a35.kztbla.cn/xiaoxinxin/dudu?rid=3040d86e7b2f&time=1769147362000&psgn=168&vs=1002

        # 1. 提取 rid 的值
        self.rid = domain_url.split("rid=")[1].split("#")[0]

        timestamp = int(time.time() * 1000)

        # 2. 构建新的 URL
        new_url = (
            domain_url.split("?")[0] 
            .replace("/x/r", "/xiaoxinxin/dudu")
            + f"?rid={self.rid}&time={timestamp}&psgn=168&vs=1002"                
        )

        print(new_url)
        response = self.session.get(new_url, headers=self.headers)
        print(response.json())
        if response.status_code == 200: 
            with open('output.json', 'a', encoding='utf-8') as f:
                json.dump(response.json(), f, ensure_ascii=False, indent=4)
                f.write('\n')  # 每次追加后换行分隔
        return response.json()
    
    def simulate_reading(self, article_data):
        """模拟阅读行为"""
        read_seconds = random.randint(7, 9)

        if article_data.get('a') != 1:
            self.send_message(article_data.get('link'))
        else:
            print(f"正在模拟阅读 {read_seconds} 秒...")
            time.sleep(read_seconds)
        return int(time.time())
    
    def claim_reward(self, read_time):
        """领取金币奖励"""
        timestamp = int(time.time() * 1000)
        api_url = f"{self.base_url}/xiaoxinxin/jinright?rid={self.rid}&time={read_time}&timestamp={timestamp}"

        response = self.session.get(api_url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None

    def send_message(self, link):    
        print(f"{self.account['name']}_发现目标疑似检测文章！！！")
        url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=' + qwbotkey
        messages = [
            f"{self.account['name']}_出现检测文章！！！\n{link}\n请在20s内点击链接完成阅读",
        ]

        for message in messages:
            data = {
                "msgtype": "text",
                "text": {
                    "content": message
                }
            }
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, headers=headers, data=json.dumps(data))
            print("以将该文章推送至微信请在20s内点击链接完成阅读--20s后继续运行")
            # 使用示例
            self.sleep_with_countdown(20)

    
    def run(self):
        """执行完整流程"""
        # 登陆
        self.get_sign_info()

        # 查询金币
        self.get_gold_balance()

        # 获取domain_url
        domain_url = self.get_domain_url()

        # 执行任务
        for i in range(30):
            print(f"------{self.account['name']}_正在第{i+1}次阅读------")
            # 请求文章
            article_data = self.request_article(domain_url)
            if not article_data or article_data.get('errcode') != 0:
                print("获取文章失败:", article_data.get('msg', '未知错误'))
                break

            # 模拟阅读
            article_data = article_data['data']
            start_time = int(time.time())
            end_time = self.simulate_reading(article_data)
            read_duration = end_time - start_time
            
            # 领取奖励
            reward_data = self.claim_reward(read_duration)
            if reward_data and reward_data.get('errcode') == 0:
                gold = reward_data['data']['gold']
                print(reward_data)
                print(f"🎉 成功获得 {gold} 金币!")
            else:
                print("领取奖励失败:", reward_data.get('msg', '未知错误'))
  
        # 提现
        self.get_initial_page()

if __name__ == "__main__":
    if is_maintenance() == True:
        print('系统维护中!!!')
        sys.exit(1)  # 中断程序

    def process_account(account):
        print(f"\n=======开始执行{account['name']}=======")
        print(account['name'], account['unionid'])
        collector = GoldCollector(account)
        collector.run()

    # 创建线程池
    with ThreadPoolExecutor(max_workers=4) as executor:
        for account in xyy_config['xyyck']:
            executor.submit(process_account, account)
            time.sleep(40)  # 线程间隔40秒
    
    # 遍历所有账号
    # for account in xyy_config['xyyck']:
    #     # 输出当前正在执行的账号
    #     print(f"\n=======开始执行{account['name']}=======")
    #     print(account['name'], account['unionid'])
    #     collector = GoldCollector(account)
    #     collector.run()