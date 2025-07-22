import os
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(dotenv_path='.env.local', verbose=True)

# 登陆
def getLogin():
  # 获取 环境变量值
  username = os.getenv('leijingUsername')
  password = os.getenv('leijingPassword')

  url = f'https://leijing1.com/login?timestamp={int(time.time() * 1000)}'
  data = {
    'token': '5a069f4401844b8fab41132678ae59d611',
    'type': 10,
    'account': username,
    'password': password
  }
  headers = {
    'x-requested-with': 'XMLHttpRequest',
    'cookie': 'cms_token=5a069f4401844b8fab41132678ae59d611'
  }

  response = requests.post(url, data=data, headers=headers)

  print(response.json())

  cookies = response.cookies.get_dict()

  # 转换为字符串格式
  cookies_str = '; '.join([f'{k}={v}' for k, v in cookies.items()])

  print(cookies_str)      


if __name__ == "__main__":
  getLogin()
