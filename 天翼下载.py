import requests
import os
import time
import json
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
from tianyiLogin import TianyiCloudLogin
from tianyiRename import rename_files

# 加载环境变量
load_dotenv(dotenv_path='.env.local', verbose=True)

class TianyiDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'accept': 'application/json;charset=UTF-8',
            'cookie': tianyiCookie
        })
        self.base_url = "https://cloud.189.cn"
        self.download_history = {}  # 下载历史记录
        self.history_file = "./history.json"  # 历史记录文件

        # 加载历史记录
        self._load_history()

    def _load_history(self):
        """加载下载历史记录"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.download_history = json.load(f)
            except Exception as e:
                print(f"无法加载下载记录: {str(e)}")
                self.download_history = {}

    def _save_history(self):
        """保存下载历史记录"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.download_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"无法保存下载记录: {str(e)}")
    
    def _add_to_history(self, file_id, file_name, file_size, save_path, download_url):
        """添加到下载历史"""
        self.download_history[file_id] = {
            'name': file_name,
            'size': file_size,
            'path': save_path,
            'url': download_url,
            'time': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        print('添加到下载历史', file_name)
        self._save_history()
    
    def _is_downloaded(self, file_id, file_name):
        """检查文件是否已下载"""
        # 先检查ID是否在历史记录中
        if str(file_id) not in self.download_history:
            # print(f'{file_name} 不在历史记录中')
            return False

        return True
        
    
    def sort_file_list(self, fileList):
        try:
            # 方法1：简单字母排序（适合英文文件名）
            sorted_file_list = sorted(fileList, key=lambda x: x['name'])
            
            # 方法2：中文拼音排序（需要安装pypinyin）
            # from pypinyin import lazy_pinyin
            # sorted_file_list = sorted(fileList, key=lambda x: ''.join(lazy_pinyin(x['name'])))
        except Exception as e:
            print(f"排序失败，将按原始顺序下载: {str(e)}")
            sorted_file_list = fileList

        # 显示排序结果
        # print("\n下载顺序：")
        # for i, item in enumerate(sorted_file_list, 1):
        #     print(f"{i}. {item['name']}")

        return sorted_file_list
    
    def verify_share(self, share_item):
        """解析分享链接获取shareId和accessCode"""
        parsed = urlparse(share_item['url'])
        query = parse_qs(parsed.query)
        
        if 'code' not in query:
            raise ValueError("无效的分享链接，请确保包含shareId和accessCode参数")
        access_code = query['code'][0]  

        """验证分享链接并获取文件信息"""
        url = f"{self.base_url}/api/open/share/getShareInfoByCodeV2.action"

        params = {
            'shareCode': access_code,
            'noCache': int(time.time() * 1000)
        }

        response = self.session.get(url, params=params)

        # if response.status_code == 400:
        #     raise ConnectionError(f"{share_item['name']} 正在审核中")
        # elif response.status_code != 200:
        #     raise ConnectionError("验证分享链接失败")
     
        data = response.json()
        # print(f"\n{data}")

        if data['res_code'] != 0:
            error_msg = data.get('res_message', '未知错误')

            # 定义常见错误的中文翻译
            error_translations = {
                "share audit not pass": "文件审核不通过",
                "share audit waiting": "文件审核中",
                "share not found or invalid": "访问页面不存在"
            }
    
            # 如果错误消息在字典里，替换成中文，否则保留原错误
            chinese_error = error_msg  # 默认保留原错误
            for key in error_translations:
                if key in error_msg:
                    chinese_error = error_translations[key]
                    break  # 找到第一个匹配项就退出
            
            raise ValueError(f"{share_item['name']} {chinese_error}")
            
        return data

    def fileList_share(self, share_info):
        """验证分享链接并获取文件信息"""
        url = f"{self.base_url}/api/open/share/listShareDir.action"

        params = {
            'noCache': int(time.time() * 1000),
            'pageNum': 1,
            'pageSize': 60,
            'fileId': share_info['fileId'],
            'shareDirFileId': share_info['fileId'],
            'isFolder': share_info['isFolder'],
            'shareId': share_info['shareId'],
            'shareMode': share_info['shareMode'],
            'iconOption': 5,
            'orderBy': 'lastOpTime',
            'descending': 'true'
        }

        response = self.session.get(url, params=params)
        if response.status_code != 200:
            raise ConnectionError("验证分享链接失败")
            
        data = response.json()
        if data['res_code'] != 0:
            raise ValueError(f"验证失败: {data.get('res_message', '未知错误')}")
        return data['fileListAO']


    def get_download_url(self, file_info):
        """获取文件下载链接"""
        url = f"{self.base_url}/api/portal/getNewVlcVideoPlayUrl.action"
        params = {
            'noCache': int(time.time() * 1000),
            'shareId': file_info['shareId'],
            'dt': 1,
            'fileId': file_info['fileId'],
            'type': 4
        }

        response = self.session.get(url, params=params)

        if response.status_code == 400:
            print(response.json())
            raise ConnectionError("cookie失效")
        # elif response.status_code != 200:
        #   raise ConnectionError("验证分享链接失败")
            
        data = response.json()

        print(data)
        if data['res_code'] != 0:
            raise ValueError(f"获取下载链接失败: {data.get('res_message', '未知错误')}")
            
        return data['normal']['url']
    
    def download_file(self, download_url, save_path, max_retries=3, retry_delay=5):
        """
        下载文件（带进度条+实时速度+断点续传+重试机制）
        
        Args:
            download_url: 下载URL
            save_path: 保存路径
            max_retries: 最大重试次数
            retry_delay: 重试延迟时间（秒）
        """
        # 获取目录路径
        dir_path = os.path.dirname(save_path)
        
        # 如果目录不存在则创建（递归创建多层目录）
        os.makedirs(dir_path, exist_ok=True)

        start_time = time.time()
        last_update = start_time
        downloaded = 0
        speed = 0
        
        # 检查文件是否已部分下载
        file_size = 0
        if os.path.exists(save_path):
            file_size = os.path.getsize(save_path)
            downloaded = file_size
        
        # 重试机制
        for attempt in range(max_retries + 1):
            try:
                # 设置断点续传请求头
                headers = {}
                if file_size > 0:
                    headers['Range'] = f'bytes={file_size}-'
                    print(f"检测到已下载 {file_size} 字节，开始断点续传...")
                
                # 设置超时和重试
                response = self.session.get(
                    download_url, 
                    headers=headers, 
                    stream=True,
                    timeout=30  # 添加超时设置
                )

                # 处理服务器响应
                if response.status_code == 416:  # 请求范围不满足
                    print("文件已完整下载")
                    return save_path
                elif response.status_code not in [200, 206]:  # 206表示部分内容
                    raise ConnectionError(f"下载失败，状态码：{response.status_code}")
                
                # 获取文件总大小
                total_size = int(response.headers.get('content-length', 0))
                if 'content-range' in response.headers:
                    # 从Content-Range头中获取总大小，格式如：bytes 0-1000/1001
                    total_size = int(response.headers['content-range'].split('/')[-1])
                elif total_size == 0:
                    # 如果无法获取总大小，使用已下载大小作为基准
                    total_size = file_size
                
                # 计算实际需要下载的总大小
                actual_total_size = total_size
                
                # 打开文件，如果已存在则追加，否则创建新文件
                mode = 'ab' if file_size > 0 else 'wb'
                with open(save_path, mode) as f:
                    for chunk in response.iter_content(chunk_size=1024*1024):  # 1MB chunks
                        if chunk:
                            f.write(chunk)
                            f.flush()  # 确保数据写入磁盘
                            downloaded += len(chunk)
                            
                            # 每0.5秒更新一次速度（避免闪烁）
                            now = time.time()
                            if now - last_update > 0.5:
                                elapsed = now - start_time
                                speed = downloaded / elapsed / 1024 / 1024  # MB/s
                                last_update = now
                            
                            # 打印进度+速度
                            self._print_progress(downloaded, actual_total_size, speed)
                
                # 如果执行到这里，说明下载成功
                break
                
            except (ConnectionError, TimeoutError, requests.exceptions.RequestException) as e:
                print(f"\n下载出错: {str(e)}")
                
                if attempt < max_retries:
                    print(f"{retry_delay}秒后开始第 {attempt + 1} 次重试...")
                    time.sleep(retry_delay)
                    
                    # 重新获取当前文件大小，因为可能已经下载了一部分
                    if os.path.exists(save_path):
                        file_size = os.path.getsize(save_path)
                        downloaded = file_size
                    else:
                        file_size = 0
                        downloaded = 0
                else:
                    print(f"\n下载失败，已达到最大重试次数 {max_retries} 次")
                    raise
        
        # 验证文件完整性
        final_size = os.path.getsize(save_path)
        if actual_total_size > 0 and final_size != actual_total_size:
            print(f"\n警告：文件大小不匹配！期望: {actual_total_size} 字节，实际: {final_size} 字节")
        else:
            print(f"\n下载完成！文件大小: {final_size} 字节，平均速度：{speed:.2f} MB/s")
        
        return save_path

    def _print_progress(self, downloaded, total, speed):
        """带速度显示的进度条"""
        percent = downloaded / total * 100 if total > 0 else 0
        bar_length = 30
        filled = int(bar_length * percent / 100)
        bar = '█' * filled + ' ' * (bar_length - filled)
        
        # 自动选择单位（B/KB/MB/GB）
        size_str = self._format_size(downloaded)
        total_str = self._format_size(total)
        
        print(
            f"\r{bar} {percent:.1f}% | {size_str}/{total_str} "
            f"| 速度: {speed:.2f} MB/s",
            end='', flush=True
        )

    def _format_size(self, size_bytes):
        """智能转换文件大小单位"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f}TB"
    
    # 获取文件
    def get_fileList(self, data, share_info):
        # 判断是否有文件夹
        if (len(data['folderList']) != 0):
            # 第二层数据
            for item in data['folderList']:
                fileListAOTwo = self.fileList_share({
                **share_info,
                'fileId': item['id']
                })
                # self.get_fileList(fileListAOTwo, share_info)
                self.fileList.extend(fileListAOTwo['fileList'])
        else: # 处理没有第二层
            self.fileList.extend(data['fileList'])
    
    def download_share_file(self, share_item, save_dir):
        """下载天翼云盘分享文件主函数"""
        # 创建保存目录
        # os.makedirs(save_dir, exist_ok=True)
  
        # 验证分享链接
        share_info = self.verify_share(share_item)
        
        # 第一层数据
        fileListAO = self.fileList_share(share_info)

        # 初始化文件列表
        self.fileList = []

        # 获取文件列表
        self.get_fileList(fileListAO, share_info)
    
        # 排序后下载
        for fileListItem in self.sort_file_list(self.fileList):
            if self._is_downloaded(fileListItem['id'], fileListItem['name']):
                # print(f"✓ 历史文件已下载过，跳过: {fileListItem['name']}")
                continue
            print(f"\n{'='*30} {fileListItem['name']} {'='*30}")
            # 获取下载链接
            download_url = self.get_download_url({
                'shareId': share_info['shareId'],
                'fileId': fileListItem['id']
            })

            # 构建保存路径
            save_path = os.path.join(save_dir, fileListItem['name'])

            # 检查文件是否存在且大小匹配
            if os.path.exists(save_path):
                local_size = os.path.getsize(save_path)
                if local_size == fileListItem['size']:
                    print(f"✓ 文件已存在且大小匹配，跳过下载: {fileListItem['name']}")
                    print(fileListItem)
                else:
                    print(f"⚠️ 文件已存在但大小不匹配 本地: {self._format_size(local_size)} vs 云端: {self._format_size(fileListItem['size'])}")
                    print(f"↓ 开始重新下载: {fileListItem['name']}")
                    self.download_file(download_url, save_path)
                    print(f"✓ 文件已保存到: {save_path}")
            else:
                # 添加历史记录
                print(f"↓ 开始下载: {fileListItem['name']} (大小: {self._format_size(fileListItem['size'])})")
                self.download_file(download_url, save_path)
                print(f"✓ 文件已保存到: {save_path}")

            # 添加历史记录
            self._add_to_history(fileListItem['id'], fileListItem['name'], fileListItem['size'], save_path, download_url)


if __name__ == "__main__":
    # 在这里直接输入分享链接
    share_list = [
      # {'name': '凡人修仙传(2020)', 'url': 'https://cloud.189.cn/web/share?code=fMraqaqiEJji'},
      {'name': '许我耀眼', 'url': 'https://cloud.189.cn/web/share?code=bYVzUvFrMzYv'},
      {'name': '欢乐家长群 第二季', 'url': 'https://cloud.189.cn/web/share?code=6RRV7rRnAree'}
    ]

    tianyiCookie = os.getenv('TIANYI_COOKIE')

    downloader = TianyiDownloader()

    try:
        for share_item in share_list:
            print(share_item)
            # 指定保存目录（默认为当前目录下的downloads文件夹）
            save_dir = f"Z:\download\下载\{share_item['name']}"
            downloader.download_share_file(share_item, save_dir)
        print('下载完成！')
        rename_files() # 重命名

    except Exception as e:
        if str(e) == 'cookie失效':
            # 用户登陆
            cloud_login = TianyiCloudLogin()
            tianyiCookie = cloud_login.login_by_password()
            print(f'{tianyiCookie}\n')
        else:
            print(f"下载失败: {str(e)}")