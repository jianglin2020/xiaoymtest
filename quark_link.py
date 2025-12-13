import requests
import json
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
    for item in soup.find_all(class_='module-search-item'):
        if a_tag := item.find('a', class_='video-serial'):
            links.append({
                'title': a_tag.get("title", "无标题"),
                'link': urljoin(base_url, a_tag.get('href'))
            })
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

def quark_link(name):
    SEARCH_KEYWORD = name
    TARGET_SITES = [
        {'name': '玩偶', 'url': 'https://wogg.xxooo.cf'},
        {'name': '至臻', 'url': 'https://xiaomi666.fun'},
        {'name': '蜡笔', 'url': 'https://feimao666.fun'},
        # {'name': '虎斑', 'url': 'http://103.45.162.207:20720'},
        # {'name': '二小', 'url': 'http://erxiaofn.click'}
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
            
            for link in extract_a_links(soup, site['url'])[:3]:  # 每个站点只处理前3个结果  
                # print(link['link'])
                if page_data := fetch_page_data(link['link']):
                    for item in page_data:
                        # print(item)
                        item['source'] = site['name']
                    all_data.extend(page_data)
                    # print(f"发现 {len(page_data)} 个夸克链接")
        except Exception as e:
            print(f"抓取 {site['name']} 失败: {e}")

    # 2. 处理数据
    if not all_data:
        print("未找到任何夸克链接！")
        return

    merged_data = merge_duplicate_links(all_data)
    # print(f"\n▌ 去重后得到 {len(merged_data)} 个唯一链接")
    
    # 4. 合并结果
    final_data = []
    for item in merged_data:
        final_data.append({
            'title': item['title'],
            'href': item['href'],
            'source': item['source']
        })

    return final_data

if __name__ == '__main__':
    quark_link('你好星期六')