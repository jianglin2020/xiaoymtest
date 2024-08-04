import os
import requests

from dotenv import load_dotenv
# 加载环境变量
load_dotenv(dotenv_path='.env.local', verbose=True)

# 从环境变量中获取CODE
list = os.getenv('ddztx')

url = "http://78383495092.sx.shuxiangby.cn/index/mob/fa_tx.html"

accounts = list.split('&')
# print(accounts, 'accounts')
for account in accounts:
  pairs = account.split(';')
  # 创建一个字典来存储键值对
  print(pairs)
  item = {}
  # 遍历每个键值对，并将其添加到字典中
  for pair in pairs:
      # print(pair)
      key, value = pair.split('=')
      item[key] = value

  headers = {
      "Host": "78383495092.sx.shuxiangby.cn",
      "Accept": "*/*",
      "Origin": "http://78383495092.sx.shuxiangby.cn",
      "X-Requested-With": "XMLHttpRequest",
      "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63060012)",
      "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
      "Cookie": "PHPSESSID="+item["ck"],
      "Referer": f"http://78383495092.sx.shuxiangby.cn/index/mob/tixian.html?code={item['code']}&state={item['id']}",
      "Accept-Encoding": "gzip, deflate",
      "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
  }

  data = {
      "code": item["code"],
      "money": 0.5,
      "kou_credit": 5000,
      "tx_type": "2",
      "ali_name": "关壮壮",
      "ali_account": 15311216972
  }

  response = requests.post(url, headers=headers, data=data)

  print(f"Status for {item['name']}: {response.status_code}")
  print(response.text)


#   POST /index/mob/fa_tx.html HTTP/1.1
# Host: 49727133196.sx.shuxiangby.cn
# Content-Length: 135
# Accept: */*
# Origin: http://49727133196.sx.shuxiangby.cn
# X-Requested-With: XMLHttpRequest
# User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63060012)
# Content-Type: application/x-www-form-urlencoded; charset=UTF-8
# Cookie: PHPSESSID=7775267869661693eb0e6e1302f18f57
# Referer: http://49727133196.sx.shuxiangby.cn/index/mob/tixian.html?code=081hoinl2z90Fd4UZYkl2add5k4hoin2&state=92351
# Accept-Encoding: gzip, deflate
# Accept-Language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7

# code=081hoinl2z90Fd4UZYkl2add5k4hoin2&money=1.5&kou_credit=15000&tx_type=2&ali_name=%E5%85%B3%E5%A3%AE%E5%A3%AE&ali_account=15311216972


# POST /index/mob/fa_tx.html HTTP/1.1
# Host: 87441840615.sx.shuxiangby.cn
# Content-Length: 134
# Accept: */*
# Origin: http://87441840615.sx.shuxiangby.cn
# X-Requested-With: XMLHttpRequest
# User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63060012)
# Content-Type: application/x-www-form-urlencoded; charset=UTF-8
# Cookie: PHPSESSID=a01c4540312344449ee56ad9f1f9962c
# Referer: http://87441840615.sx.shuxiangby.cn/index/mob/tixian.html?code=011gwCll2ubvHd4Xl2nl23JY3f3gwClo&state=92351
# Accept-Encoding: gzip, deflate
# Accept-Language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7

# code=011gwCll2ubvHd4Xl2nl23JY3f3gwClo&money=0.7&kou_credit=7000&tx_type=2&ali_name=%E5%85%B3%E5%A3%AE%E5%A3%AE&ali_account=15311216972


# http://87441840615.sx.shuxiangby.cn/index/mob/tixian.html?code=081hoinl2z90Fd4UZYkl2add5k4hoin2&state=71970

