import requests
from datetime import datetime

headers = {
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIxNDM0ODdjYy0xYzU5LTQ4YWItYTM2MS1iNjBhN2EzYTRmYmYiLCJyb2xlIjoxLCJpYXQiOjE3NTI4MDU1MDMsImV4cCI6MTc1MjgyNzEwM30.L5sOE9OfEKxnTP17OPERFRViRd863XrynE9Wi7NR0QE'
}

url_host = 'http://192.168.1.120:8818'

# 豆瓣热门
def getDoubanHot():  
    url = f'{url_host}/api/douban/hot'
    params = {
        "type": 'tv',
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


# 获取链接
def getCloudLinks(name):
  url = f'{url_host}/api/search?keyword={name}'
  response = requests.get(url, headers=headers)
  response.raise_for_status()  # 检查请求是否成功
  data = response.json().get('data', [])
  for item in data[:1]:
    if len(item['list']) > 0:
      print(f"{item['channelInfo']['name']}")
      for it in item['list'][:2]:
        # 解析为 datetime 对象
        dt = datetime.fromisoformat(it['pubDate'])  # Python 3.7+ 支持
        # 转换为可读格式（示例）
        pubDate = dt.strftime("%Y-%m-%d %H:%M:%S")  # 格式化为 "2025-07-13 14:57:21"
        print(it['messageId'], it['cloudLinks'], pubDate)

if __name__ == "__main__":
  getDoubanHot()
