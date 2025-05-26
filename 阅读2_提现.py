import random
import requests
import time
import yaml
import json
import re
from datetime import datetime, timedelta


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
duoduo_config = config['duoduo_config']
check_whitelist = config['check_whitelist']

class GoldCollector:
    def __init__(self, account={}):
        # 初始化会话和基本参数
        self.session = requests.Session()  # 使用session保持连接
        self.account = account 
        self.main_url = 'http://oapi.liyishabiubiu.cn/api/client/read/has_next?val=xlxixexkxkxhxiycxmxgxjxfxmxfxlxhxlxe'
        self.aid = ''
        self.headers = {'User-Agent': random.choice(config['ua_list'])}  # 随机选择User-Agent

    def sleep_with_countdown(self, sleep_time):
        """带倒计时显示的休眠函数"""
        for remaining in range(sleep_time, 0, -1):
            print(f"\r剩余等待时间: {remaining}秒", end="", flush=True)
            time.sleep(1)
        print(f"\r等待完成！" + " " * 20)  # 清除行尾

    def is_10_days_before(self, target_str="1990-01-01 16:01"):
        """检查目标日期是否是当前日期的前10天"""
        try:
            target = datetime.strptime(target_str, "%Y-%m-%d %H:%M")
            return target < datetime.now() - timedelta(days=7)
        except ValueError:
            raise ValueError("日期格式必须为 YYYY-MM-DD HH:MM")
    
    def extract_params_from_html(self, html_content):
        """从HTML中提取关键参数"""
        # 提取时间
        create_time_match = re.search(r"var createTime\s*=\s*['\"](.*?)['\"]", html_content)

        if create_time_match:
            self.create_time = create_time_match.group(1)
            print(self.create_time)  # 输出: 2025-04-19 18:08

        # 匹配 class 包含 `wx_tap_link js_wx_tap_highlight weui-wa-hotarea` 的 `<a>` 标签文本
        author_match = re.search(r'<a[^>]*class="[^"]*\bwx_tap_link\b[^"]*\bjs_wx_tap_highlight\b[^"]*\bweui-wa-hotarea\b[^"]*"[^>]*>([^<]+)</a>', html_content)

        if author_match:
            self.author_match = author_match.group(1).strip()
            print(author_match.group(1).strip())  # 输出: 蜜蜂岛学习
        else:
            print("未找到作者")

        match = re.search(r'<h1[^>]*id="activity-name"[^>]*>([\s\S]*?)<\/h1>', html_content)
        if match:
            self.title = match.group(1).strip()
            print(self.title)    
    
    def get_wx_page(self, wx_url):
        """获取初始页面并解析关键参数"""
        url = f"{wx_url}"   

        response = self.session.get(url, headers=self.headers, timeout=20)

        # 保存到当前目录的 response.txt
        with open("response.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        # 获取参数
        self.extract_params_from_html(response.text)
        read_seconds = random.randint(7, 10)
        if self.is_10_days_before(self.create_time) or self.author_match in check_whitelist :
            #10天以前的文章
            self.send_message(url)
        else:
            print(f"正在模拟阅读 {read_seconds} 秒...")
            time.sleep(read_seconds)
    
    def send_message(self, link):    
        print(f"发现目标疑似检测文章！！！")
        url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=' + qwbotkey
        messages = [
            f"出现检测文章！！！\n{link}\n请在60s内点击链接完成阅读",
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
            print("以将该文章推送至微信请在30s内点击链接完成阅读--30s后继续运行")
            # 使用示例
            self.sleep_with_countdown(30)
    # 查询金币
    def get_balance(self):
        url = f'https://oapi.liyishabiubiu.cn/api/client/user/profile'
        headers = {
            'User-Agent': random.choice(config['ua_list']),
            'access-token': self.account['token']
        } 

        response = self.session.get(url, headers=headers)

        response.raise_for_status()
        result = response.json()

        print(result)
        if result.get('code') == 0:
            data = result.get('data', {})
            print(f"🎉 用户昵称：{data['nickname']}")
            print(f"🎉 金币剩余：{data['balance']}")
            return result.get('data', {}).get('balance', 0)
        else:
            print(f"获取余额失败: {result.get('msg', '未知错误')}")
            return None
    
    def withdraw_to_wechat(self):
        balance = self.get_balance()
        # 大于3000 执行提现
        if balance >= 3000:
            url = f'https://oapi.liyishabiubiu.cn/api/client/user/balance/withdraw?amount={balance}&pay_method=wx'
            headers = {
                'User-Agent': random.choice(config['ua_list']),
                'access-token': self.account['token']
            } 

            response = self.session.get(url, headers=headers)
            print(f"响应状态码: {response.status_code}")

            # 解析JSON响应内容
            result = response.json()
            
            print(result)

    def send_requests(self):
        """发送30次请求的核心函数"""
        for i in range(1, 31):
            print(f"\n--- 第 {i} 次请求 ---")
            # 构造请求URL，添加时间戳参数
            url = f'{self.main_url}&aid={self.aid}&st={int(time.time() * 1000)}' 
            print("请求URL:", url)  
            
            # 发送GET请求
            response = self.session.get(url, headers=self.headers)
            print(f"响应状态码: {response.status_code}")

            # 解析JSON响应内容
            result = response.json()
            
            print(result)
            # 写入JSON文件（追加模式）
            with open('output.json', 'a', encoding='utf-8') as f:
                # 将JSON数据写入文件，禁用ASCII转码，使用4空格缩进
                f.write(f"\n===== 第{i}次 运行时间: {time.strftime('%Y-%m-%d %H:%M:%S')} =====\n")
                json.dump(result, f, ensure_ascii=False, indent=4)
                f.write('\n')  # 每次追加后换行分隔不同记录
            
            # 检查业务逻辑是否失败（假设result是业务结果对象）
            if result.get('code') != 0:
                print('阅读失败！！！')
                break  # 失败时退出循环
            # 更新aid参数（安全获取嵌套字段，失败时保持原值）
            data = result.get('data', {})
            self.aid = data.get('aid', self.aid) 
            print(f"新的aid: {self.aid}")
            # 检测消息
            self.get_wx_page(data.get('url', ''))

    def test_weixin_url(self):
        weixin_urls = []
        pattern = r'"url":\s*"(https?://mp\.weixin\.qq\.com[^"]+)"'

        with open('output.json', 'r', encoding='utf-8') as f:
            for line in f:
                match = re.search(pattern, line)
                if match:
                    weixin_urls.append(match.group(1))

        for item in weixin_urls:
            print("=========================================")
            print(item)
            self.get_wx_page(item)
       

    def run(self):
        """主运行方法"""
        # self.send_requests()
        # 提现
        self.withdraw_to_wechat()
        # self.test_weixin_url()

if __name__ == "__main__":
    # collector = GoldCollector()
    # collector.run()

    #遍历所有账号
    for account in duoduo_config['duoduock']:
        # 输出当前正在执行的账号
        print(f"\n=======开始执行{account['name']}=======")
        collector = GoldCollector(account)
        collector.run()