import requests
import json
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import defaultdict

# 配置常量
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    # 'Cookie': '_ga=GA1.1.1073942622.1746717690; cf_clearance=H_XhTOVzhLrdAgV4dACUelE_PbPWOC6HmRv2gmssO6s-1755143919-1.2.1.1-K5dvOjVjS8ME2ZL7UGCBFhCa.Y9TEO19BL_ypOFzlnlBWRfhrVMK_wi4FkHoV2Lw4yvAPkTbyS_ot3RZxo3H3DDoOcVEwwlEi44SS8GYDeT..iOBkJMippBce3If8Ro5ZWMvEiePONPqLwOu2pEWqNi6RAWKwQW5gGgmkjBBcG5nbmDN8osASAlhkRWCSBaCIJHcs7KOY1FysdqtTyGdYLQA92CcDebs38TBjuZvw7w; _ga_JSCFX80PZS=GS2.1.s1755143919$o4$g0$t1755143919$j60$l0$h0'
}
TARGET_DOMAIN = 'https://pan.quark.cn'

def save_to_json(data, filename):
    """保存数据为JSON文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"数据已保存到 {filename}")

def extract_a_links(soup, base_url):
    """提取搜索结果的链接和标题"""
    links = []
    for item in soup.find_all(class_='module-item-pic'):
        if a_tag := item.find('img'):
            links.append({
                'title': a_tag.get("alt", "无标题"),
                'images': a_tag.get('data-src')
            })
    print(links)
    return links

def fetch_page_data(url):
    """获取详情页中的夸克链接"""
    try:
        soup = BeautifulSoup(requests.get(url, headers=HEADERS, timeout=10).text, 'html.parser')
        return [
            {
                'href': a.get('data-clipboard-text'),
                'title': a.find('h4').text.strip() if a.find('h4') else '无标题'
            }
            for row in soup.find_all(class_='module-row-info')
            if (a := row.find('a', class_='module-row-text')) 
            and a.get('data-clipboard-text', '').startswith(TARGET_DOMAIN)
        ]
    except Exception as e:
        print(f"获取页面数据失败: {url} | 错误: {e}")
        return []

def merge_duplicate_links(data):
    """合并重复链接，标题保留第一个遇到的"""
    merged = defaultdict(lambda: {
        'href': '',
        'title': '',  # 只保留第一个标题
        'sources': set()
    })
    
    for item in data:
        href = item['href']
        if not merged[href]['title']:  # 如果是第一次遇到这个链接
            merged[href]['title'] = item['title']
        merged[href]['href'] = href
        merged[href]['sources'].add(item['source'])
    
    return [{
        'href': item['href'],
        'title': item['title'],  # 直接使用第一个标题
        'source': ' / '.join(sorted(item['sources']))
    } for item in merged.values()]

def save_img(item, title):
    if not os.path.exists('./images'):
        os.makedirs('./images')
    try:
        print(f"{item['images']}")
        res = requests.get(url=item['images'], headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'})

        with open(f"./images/{title}.jpg", 'wb') as f:
            f.write(res.content)
    except Exception as e:
        print(e, "图片下载失败")

def quark_link(name):
    SEARCH_KEYWORD = name
    TARGET_SITES = [
        # {'name': '玩偶', 'url': 'https://wogg.xxooo.cf'},
        # {'name': '至臻', 'url': 'https://xiaomi666.fun'},
        {'name': '蜡笔', 'url': 'https://feimao666.fun'},
        # {'name': '虎斑', 'url': 'http://103.45.162.207:20720'},
        # {'name': '二小', 'url': 'http://www.2xiaopan.fun'}
    ]

    # 1. 抓取数据
    # print("="*50)
    # print(f"开始搜索: {SEARCH_KEYWORD}")
    all_data = []
    
    for site in TARGET_SITES:
        try:
            search_url = (
                f"{site['url']}/vodsearch/-------------.html?wd={SEARCH_KEYWORD}"
                if site['name'] == '玩偶' else
                f"{site['url']}/index.php/vod/search.html?wd={SEARCH_KEYWORD}"
            )
            
            print(f"正在抓取 {site['name']}: {search_url}")
            response = requests.get(search_url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for link in extract_a_links(soup, site['url'])[:1]:  # 每个站点只处理前3个结果  
                save_img(link, SEARCH_KEYWORD)
        except Exception as e:
            print(f"抓取 {site['name']} 失败: {e}")


if __name__ == '__main__':
    list = ['浪浪山小妖怪', '捕风追影', '南京照相馆', '罗小黑战记2', '毕正明的证明', '聊斋：兰若寺', '长安的荔枝', '戏台', '哆啦A梦：大雄的绘画奇遇记', 'F1：狂飙飞车', '坏蛋联盟2', '坏蛋联盟2', '碟中谍8：最终清算', '侏罗纪世界：重生', '封神第二部：战火西 岐', '美国队长4', '哪吒之魔童闹海', '雄狮少年2', '唐探1900', '熊出没·重启未来', '误杀3', '美国队长4', '好东西', '志愿军： 存亡之战', '飞驰人生2', '龙马精神', '雷神3：诸神黄昏', '雷霆沙赞！众神之怒', '雷神2：黑暗世界', '雷神4：爱与雷霆', '雷神1', '长津湖之水门桥', '雄狮少年', '长津湖', '银河护卫队3', '逆行人生', '长安三万里', '荒野机器人', '铁道英雄', '速度与激情9', '超级马力欧兄弟大电影', '速度与激情10', '走走停停', '误杀', '西游记之大圣归来', '蚁人与黄蜂女：量子狂潮', '让子弹飞', '西虹市首富', '西线无战事', '第二十条', '神偷奶爸4', '荒野机器人', '芬奇', '茶啊二中', '疾速追杀4', '白蛇：浮生', '碟中谍7 ：致命清算（上）', '猩球崛起：新世界', '疯狂的麦克斯：狂暴女神', '疯狂原始人2：新纪元', '疯狂原始人', '独行月球', '狙击手', '猩球崛起：新世界', '爱情神话', '热辣滚烫', '熊出没·逆转时空', '熊出没·伴我“熊芯”', '深海', '消失的她', '满江红', '流浪地球2', '末路狂花钱', '沙丘2', '抓娃娃', '新神榜：杨戬', '巨齿鲨2：深渊', '我爱你', '年会不能停', '', '我和我的家乡', '我们一起摇太阳', '哥斯拉大战金刚2：帝国崛起', '惊天营救2', '巨齿鲨', '封神第一部：朝歌风云', '小黄人大眼萌：神偷奶爸前传', '姥姥的外孙', '宇宙探索编辑部', '头脑特工队2', '孤注一掷', '周处除三害', '天书奇谭', '哪吒之魔童降世', '哥斯拉大战金刚', '哥斯拉大战金刚2：帝国崛起', '哆啦A梦：大雄与天空的理想乡', '千与千寻', '变型金刚：超能勇土崛起', '变形金刚：起源', '功夫熊猫4', '八角笼中', '保你平安', '加勒比海盗3：世界的尽头', '你好，李焕英', '人生大事', '人生路不熟', '三大队 电影版', '中国乒乓之绝地反击']

    for item in list:
        quark_link(item)