import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(dotenv_path='.env.local', verbose=True)

headers = {
  'Authorization': ''
}

url_host = 'http://192.168.1.120:8818'

# 登陆
def getCloudLogin():
  # 获取 环境变量值
  username = os.getenv('cloudSaverUsername')
  password = os.getenv('cloudSaverPassword')
        
  url = f'{url_host}/api/user/login'
  data = {
    'username': username,
    'password': password
  }

  response = requests.post(url, json=data)
  data = response.json().get('data', {})

  headers['Authorization'] = f"Bearer {data['token']}"
  
  print(headers)


# 豆瓣热门
def getDoubanHot(type):
    url = f'{url_host}/api/douban/hot'
    typeList = {
      1: 'tv',
      2: 'show',
    }
    params = {
        "type": typeList[type],
        "category": "show",
        "api": "tv",
        "limit": 10
    }
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()  # 检查请求是否成功
    
    data = response.json().get('data', [])
    
    for item in data[:5]:
      print(f"\n================{item['title']} {item['episodes_info']}======================")
      getCloudLinks(item['title'])

# 自定义查询名称
def getMyNames(data):
  for name in data:
    print(f"\n================{name}======================")
    getCloudLinks(name)

# 获取链接
def getCloudLinks(name):
  name = name.split(' ')[0] # 只要前面名称
  url = f'{url_host}/api/search?keyword={name}'
  response = requests.get(url, headers=headers)
  response.raise_for_status()  # 检查请求是否成功
  data = response.json().get('data', [])
  for item in data[:1]:
    if len(item['list']) > 0:
      print(f"{item['channelInfo']['name']}")
      for it in item['list'][:5]:
        # 解析为 datetime 对象
        dt = datetime.fromisoformat(it['pubDate'])  # Python 3.7+ 支持
        # 转换为可读格式（示例）
        pubDate = dt.strftime("%Y-%m-%d %H:%M:%S")  # 格式化为 "2025-07-13 14:57:21"
        for i in it['cloudLinks']:
          # 只显示天翼和夸克链接
          if i['cloudType'] == 'tianyi' or i['cloudType'] == 'quark':
            print(it['messageId'], i, pubDate)
        
# 主方法        
def main():
  getCloudLogin() # 登陆
  # getDoubanHot(1) # 电视剧
  # getDoubanHot(2) # 综艺
  getMyNames(['生万物', '锦月如歌', '花儿与少年'])

if __name__ == "__main__":
  main()
