import requests
import time
import yaml

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


class GoldCollector:
    def __init__(self, account):
        self.session = requests.Session()
        self.account = account
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63060012)'
        }
    
    def sleep_with_countdown(self, sleep_time):
        """带倒计时显示的sleep"""
        for remaining in range(sleep_time, 0, -1):
            print(f"\r剩余等待时间: {remaining}秒", end="", flush=True)
            time.sleep(1)
        print("\r等待完成！" + " " * 20)  # 清除行尾

    # 获取 domain_url
    def get_domain_url(self):
        url = "http://1747921943te.aaik2kk8693.cn/wtmpdomain2"
        data = {
            'unionid': self.account['unionid'],
        }

        try:
            response = self.session.post(
                url,
                headers=self.headers,
                data=data,
                cookies={'ejectCode': '1', 'ysmuid': self.account["ysmuid"]},
                timeout=20
            )
            response.raise_for_status()
            result = response.json()

            if result.get('errcode') == 0:
                data = result.get('data', {})
                print(f"🎉 domain地址：{data['domain']}")

                return result.get('data', {}).get('domain', '')
            else:
                print(f"获取失败: {result.get('msg', '未知错误')}")
                return None
                    
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {str(e)}")
            return None

    def get_sign_info(self):
        """获取初始页面并解析关键参数"""
        # url = f"http://1747926292te.519381.cn/yunonline/v1/sign_info"
        url = f"http://1747926292te.519381.cn/yunonline/v1/hasWechat"

        params = {
            'unionid': self.account['unionid']
            # 'time': int(time.time() * 1000)  # 生成13位时间戳
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

            if result.get('errcode') == 0:
                data = result.get('data', {})
                print(f"🎉 登陆数据：{data}")
            else:
                print(f"登陆失败: {result.get('msg', '未知错误')}")
                return None
                    
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {str(e)}")
            return None 


    def get_initial_page(self, domain_url):
        """获取初始页面并解析关键参数"""
        url = f"{domain_url}"
        response = self.session.get(url, headers=self.headers)

        # 保存到当前目录的 response.txt
        with open("response.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        
        print("内容已保存到 response.html")
        return response.text


    def get_gold_balance(self):
        """获取金币余额"""
        url = f"http://1747913911te.cgwgov.cn/yunonline/v1/gold"
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

            if result.get('errcode') == 0:
                data = result.get('data', {})
                print(f"🎉 今日阅读：{data['day_read']}")
                print(f"🎉 金币剩余：{data['last_gold']}")
                print(f"🎉 今日奖励：{data['day_gold']}")
                return result.get('data', {}).get('gold', 0)
            else:
                print(f"获取余额失败: {result.get('msg', '未知错误')}")
                return None
                    
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {str(e)}")
            return None


    def request_article(self, domain_url):
        """请求文章链接"""
        # 先处理时间戳（13位毫秒级）
        timestamp = str(int(time.time() * 1000))
        new_url = (domain_url
                .replace("/xsysy.html?", "/xdaeryy?")
                .replace("&dt=", "&time=") 
                + "000&psgn=168&vs=120")



        print(new_url)
        response = self.session.get(new_url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None
    
    def simulate_reading(self, article_url, read_seconds=10):
        """模拟阅读行为"""
        print(f"正在模拟阅读 {read_seconds} 秒...")
        time.sleep(read_seconds)
        return int(time.time())
    
    def claim_reward(self, gt_param, read_time):
        """领取金币奖励"""
        timestamp = int(time.time() * 1000)
        api_url = f"{self.base_url}/jinbicp?gt={gt_param}&time={read_time}&timestamp={timestamp}"
        
        response = self.session.get(api_url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None

    def send_message(self):    
        print(f"{self.account['name']}_发现目标疑似检测文章！！！")
        url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=' + qwbotkey
        link = 'https://www.baidu.com'
        messages = [
            f"{self.account['name']}_出现检测文章！！！\n{link}\n请在60s内点击链接完成阅读",
        ]

        for message in messages:
            data = {
                "msgtype": "text",
                "text": {
                    "content": message
                }
            }
            # headers = {'Content-Type': 'application/json'}
            # response = requests.post(url, headers=headers, data=json.dumps(data))
            print("以将该文章推送至微信请在60s内点击链接完成阅读--60s后继续运行")
            # 使用示例
            self.sleep_with_countdown(60)

    
    def run(self):
        """执行完整流程"""
        # 登陆
        self.get_sign_info()

        # 查询金币
        self.get_gold_balance()

        # 获取domain_url
        domain_url = self.get_domain_url()

        # 获取初始页面
        self.get_initial_page(domain_url)
        
        # 请求文章
        article_data = self.request_article(domain_url)
        if not article_data or article_data.get('errcode') != 0:
            print("获取文章失败:", article_data.get('msg', '未知错误'))
            return
        
        # 发送消息
        self.send_message()

        # 模拟阅读
        # article_url = article_data['data']['link']
        # start_time = int(time.time())
        # end_time = self.simulate_reading(article_url)
        # read_duration = end_time - start_time
        
        # 领取奖励
        # reward_data = self.claim_reward(gt_param, read_duration)
        # if reward_data and reward_data.get('errcode') == 0:
        #     gold = reward_data['data']['gold']
        #     print(f"🎉 成功获得 {gold} 金币!")
        # else:
        #     print("领取奖励失败:", reward_data.get('msg', '未知错误'))

if __name__ == "__main__":
    # 遍历所有账号
    for account in xyy_config['xyyck']:
        # 输出当前正在执行的账号
        print(f"\n=======开始执行{account['name']}=======")
        print(account['name'], account['ysmuid'])
        # current_time = str(int(time.time()))
        collector = GoldCollector(account)
        collector.run()