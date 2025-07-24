import requests
import json
import csv
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from quark_checker import is_quark_link_expired

# 配置常量
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Cookie': '_ga=GA1.1.1073942622.1746717690; cf_clearance=KoaokhNcEqD9XtvccYlxBwBSR5A.P8h8mBzwC9YGjuk-1753347718-1.2.1.1-.BOyza3v5zkOmx4UZKb3jVkEl56d5bNZYLvCTNHwtLuxOv8b1A_eCuFkva_HrOPyjuDc6WVa5UmzRAEGTyqPwfLSdGlrtii1uKQ_5JbTZFYO4yo1SwuGqL18_WF.9CCJ6PnFTbWNIfZws8ZHc_GH3k_7AgppriOe0mTaPaFrBBdKc9J1Ekm_YOI5zNmK57Q7UJUGLdIK3ftLjtFtbk62LBioxCY79Cwidk_qm4TAhP0; _ga_JSCFX80PZS=GS2.1.s1753347720$o4$g0$t1753347720$j60$l0$h0'
}
TARGET_DOMAIN = 'https://pan.quark.cn'
MAX_WORKERS = 5  # 并发检测线程数
RETRY_TIMES = 2  # 检测失败重试次数

def save_to_json(data, filename):
    """保存数据为JSON文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"数据已保存到 {filename}")

def save_to_csv(data, filename):
    """保存数据为CSV文件"""
    if not data:
        return
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
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

def check_link_status(url):
    """检测单个链接状态（带重试机制）"""
    for attempt in range(RETRY_TIMES):
        try:
            is_valid = not is_quark_link_expired(url)
            return "✅ 有效" if is_valid else "❌ 失效"
        except Exception as e:
            if attempt == RETRY_TIMES - 1:
                print(f"检测失败: {url[:60]}... | 错误: {e}")
                return "❓ 未知"
            time.sleep(1)

def batch_check_links(links):
    """并发检测链接有效性"""
    results = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_url = {
            executor.submit(check_link_status, link['href']): link['href']
            for link in links
        }
        
        for i, future in enumerate(as_completed(future_to_url), 1):
            url = future_to_url[future]
            try:
                results[url] = future.result()
                print(f"进度: {i}/{len(links)} | {url[:60]}... {results[url]}")
            except Exception as e:
                print(f"检测出错: {url[:60]}... | 错误: {e}")
                results[url] = "❓ 未知"
    return results

def main():
    SEARCH_KEYWORD = '喜剧之王单口季'
    TARGET_SITES = [
        {'name': '玩偶', 'url': 'https://www.wogg.one'},
        {'name': '至臻', 'url': 'https://xiaomi666.fun'},
        {'name': '二小', 'url': 'http://www.2xiaopan.fun'},
        {'name': '蜡笔', 'url': 'https://feimao666.fun'}
    ]

    # 1. 抓取数据
    print("="*50)
    print(f"开始搜索: {SEARCH_KEYWORD}")
    all_data = []
    
    for site in TARGET_SITES:
        try:
            search_url = (
                f"{site['url']}/vodsearch/-------------.html?wd={SEARCH_KEYWORD}"
                if site['name'] == '玩偶' else
                f"{site['url']}/index.php/vod/search.html?wd={SEARCH_KEYWORD}"
            )
            
            print(f"\n▌ 正在抓取 {site['name']}: {search_url}")
            response = requests.get(search_url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for link in extract_a_links(soup, site['url'])[:3]:  # 每个站点只处理前3个结果
                if page_data := fetch_page_data(link['link']):
                    for item in page_data:
                        print(item)
                        item['source'] = site['name']
                    all_data.extend(page_data)
                    print(f"发现 {len(page_data)} 个夸克链接")
        except Exception as e:
            print(f"抓取 {site['name']} 失败: {e}")

    # 2. 处理数据
    if not all_data:
        print("未找到任何夸克链接！")
        return

    merged_data = merge_duplicate_links(all_data)
    print(f"\n▌ 去重后得到 {len(merged_data)} 个唯一链接")

    # 3. 并发检测
    print(f"\n▌ 开始并发检测（同时{MAX_WORKERS}个线程）...")
    start_time = time.time()
    status_results = batch_check_links(merged_data)
    
    # 4. 合并结果
    final_data = []
    for item in merged_data:
        final_data.append({
            'title': item['title'],
            'href': item['href'],
            'source': item['source'],
            'status': status_results.get(item['href'], "❓ 未知")
        })

    # 5. 保存结果
    save_to_json(final_data, f'output.json')
    # save_to_csv(final_data, f'output.csv')

    # 6. 统计结果
    valid_count = sum(1 for x in final_data if x['status'] == "✅ 有效")
    print(f"\n{'='*50}")
    print(f"▶ 检测完成 | 耗时: {time.time()-start_time:.1f}秒")
    print(f"• 有效链接: {valid_count}")
    print(f"• 失效链接: {sum(1 for x in final_data if x['status'] == '❌ 失效')}")
    print(f"• 未知状态: {sum(1 for x in final_data if x['status'] == '❓ 未知')}")
    print(f"{'='*50}")

    # 按来源统计
    source_stats = defaultdict(lambda: {'valid': 0, 'total': 0})
    for item in final_data:
        for source in item['source'].split(' / '):
            source_stats[source]['total'] += 1
            if item['status'] == "✅ 有效":
                source_stats[source]['valid'] += 1
    
    print("\n按来源统计:")
    for source, stat in sorted(source_stats.items()):
        print(f"{source:<5} | 有效 {stat['valid']:>2}/{stat['total']:>2} | 成功率 {stat['valid']/stat['total']:.0%}")

if __name__ == '__main__':
    main()