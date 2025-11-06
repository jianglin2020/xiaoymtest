import os
import requests
import re
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from quark_link import quark_link

# 加载环境变量
load_dotenv(dotenv_path='.env.local', verbose=True)

headers = {
  'Authorization': ''
}

url_host = 'http://192.168.1.120:8818'
url_host2 = 'http://192.168.1.120:8877'

# 处理标题
def deal_title(title):
  # 用括号拆分取第一部分
  parts = re.split(r'[()（）]', title.replace('\u200e', ''))
  if parts and parts[0].strip():
    return parts[0].strip()
  else:
    return title

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
      getCloudSaverLinks(item['title'])
      # getPanSouLinks(item['title'])

# 自定义查询名称
def getMyNames(data):
  for item in data:
    print(f"\n================{item['name']}======================")
    if item['type'] == 1: # 电视剧
      getCloudSaverLinks(item['name'])
    else: # 综艺
      getQuarkLinks(item['name'])
      # getPanSouLinks(item['name'])

# 获取CloudSaver链接
def getCloudSaverLinks(name):
  print('CloudSaver')
  name = name.split(' ')[0] # 只要前面名称
  url = f'{url_host}/api/search?keyword={name}'
  response = requests.get(url, headers=headers)
  response.raise_for_status()  # 检查请求是否成功
  data = response.json().get('data', [])
  for item in data[:1]:
    if len(item['list']) > 0:
      for it in item['list'][:5]:
        for i in it['cloudLinks']:
          i['title'] = it['title']
          # 只显示天翼和夸克链接
          if i['cloudType'] == 'tianyi' or i['cloudType'] == 'quark':
            print({
              'title': deal_title(it['title']),
              'href': i['link'],
              'source': item['channelInfo']['name']
            })

# 获取Quark链接
def getQuarkLinks(name):
  print('Quark')
  name = name.split(' ')[0] # 只要前面名称
  data = quark_link(name)

  for it in data:
    print(it)

# 获取盘搜链接
def getPanSouLinks(name):
  print('PanSou')
  name = name.split(' ')[0] # 只要前面名称
  url = f'{url_host2}/api/search?kw={name}&res=merge&src=all&channels=tianyirigeng&plugins=labi,wanou,zhizhen,leijing&cloud_types=quark,tianyi&refresh=true'
  response = requests.get(url, headers=headers)
  response.raise_for_status()  # 检查请求是否成功
  data = response.json().get('data', [])

  # 定义处理顺序
  preferred_order = ['quark']

  # 按指定顺序处理
  for key in preferred_order:
      if key in data['merged_by_type']:
          item = data['merged_by_type'][key]
          for index, it in enumerate(item[:6], start=1000):

            # print(it['source'])
            # 1. 解析为 datetime 对象（直接支持带时区的格式）
            datetime_str = it['datetime'].replace('Z', '+00:00')
            dt = datetime.fromisoformat(datetime_str)
            # 2. 转换为东八区时间
            east_8_tz = timezone(timedelta(hours=8))  # 创建东八区时区
            beijing_time = dt.astimezone(east_8_tz)   # 转换时区
            # 3. 格式化为字符串
            pubDate = beijing_time.strftime("%Y-%m-%d %H:%M:%S") # 输出: 2025-08-14 20:22:17

            # 只显示天翼和夸克链接
            if key == 'tianyi' or key == 'quark':
              print(index, {'link': it['url'], 'cloudType': key}, pubDate, it['source'],)

def select_item(data):
    print("请选择一条数据：")
    for i, item in enumerate(data, 1):
        print(f"{i}. {item['name']}")
    
    while True:
        try:
            choice = int(input("请输入序号: ")) - 1
            if 0 <= choice < len(data):
                return data[choice]
            else:
                print("序号无效，请重新输入")
        except ValueError:
            print("请输入有效数字")

# 主方法        
def main():
  getCloudLogin() # 登陆
  # getDoubanHot(1) # 电视剧
  # getDoubanHot(2) # 综艺

  # 运行选择
  selected_item = select_item([
    {'name': '天地剑心', 'type': 1},
    {'name': '暗河传', 'type': 1},
    {'name': '森林进化论', 'type': 2},
    {'name': '现在就出发', 'type': 2},
    {'name': '花儿与少年', 'type': 2},
    {'name': '向往的生活', 'type': 2},
    {'name': '你好星期六', 'type': 2}
  ])

  print("你选择了:", selected_item)
  getMyNames([selected_item])
     
if __name__ == "__main__":
  main()
