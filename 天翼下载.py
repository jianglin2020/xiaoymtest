import requests
import os
import time
import json
from urllib.parse import urlparse, parse_qs

class TianyiDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'accept': 'application/json;charset=UTF-8',
            'cookie': 'Hm_lvt_9c25be731676bc425f242983796b341c=1742357985; userId=201%7C2022072000368771793; zhizhendata2015jssdkcross=%7B%22distinct_id%22%3A%22MjAyMjA3MjAwMDM2ODc3MTc5Mw%3D%3D%22%2C%22first_id%22%3A%22195ac9df37d798-0cff8224617bd2-26021051-1821369-195ac9df37e1619%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22login_type%22%3A%22%22%2C%22utms%22%3A%7B%7D%2C%22%24device_id%22%3A%22195ac9df37d798-0cff8224617bd2-26021051-1821369-195ac9df37e1619%22%7D; apm_key=3D79FAD30746356E8A33A5D0F38CE4F2; apm_uid=504A44F36D169C530EAC8A72C667AD62; apm_ct=20250622101758000; apm_ua=B9CBD8DC13F19F9E7EB854F472BFA274; JSESSIONID=CD945E48D0156C14E8C9D68E97242D2F; COOKIE_LOGIN_USER=32FDAF63FE3ED5D04B607C53E5BD9D5D06B9BAB25A864B2B4E647CDC89C0F911116218FB08FA4578DA2715CB3A79B695E0DA1B309F038142'
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
            print(f'{file_name} 不在历史记录中')
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
        print("\n下载顺序：")
        for i, item in enumerate(sorted_file_list, 1):
            print(f"{i}. {item['name']}")

        return sorted_file_list
    
    def verify_share(self, share_url):
        """解析分享链接获取shareId和accessCode"""
        parsed = urlparse(share_url)
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

        if response.status_code == 400:
            raise ConnectionError("文件正在加紧审核中")
        # elif response.status_code != 200:
        #     raise ConnectionError("验证分享链接失败")
            
        data = response.json()
        print(f'\n{data}')
        if data['res_code'] != 0:
            raise ValueError(f"验证失败: {data.get('res_message', '未知错误')}")
            
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

        if response.status_code != 200:
            raise ConnectionError("获取下载链接失败")
            
        data = response.json()

        print(data)
        if data['res_code'] != 0:
            raise ValueError(f"获取下载链接失败: {data.get('res_message', '未知错误')}")
            
        return data['normal']['url']
    
    def download_file(self, download_url, save_path):
      # 获取目录路径
      dir_path = os.path.dirname(save_path)
        
      # 如果目录不存在则创建（递归创建多层目录）
      os.makedirs(dir_path, exist_ok=True)

      """下载文件（带进度条+实时速度）"""
      start_time = time.time()
      last_update = start_time
      downloaded = 0
      speed = 0
      
      response = self.session.get(download_url, stream=True)
      if response.status_code != 200:
          raise ConnectionError(f"下载失败，状态码：{response.status_code}")
      
      total_size = int(response.headers.get('content-length', 0))
      
      with open(save_path, 'wb') as f:
          for chunk in response.iter_content(chunk_size=1024*1024):  # 1MB chunks
              if chunk:
                  f.write(chunk)
                  downloaded += len(chunk)
                  
                  # 每0.5秒更新一次速度（避免闪烁）
                  now = time.time()
                  if now - last_update > 0.5:
                      speed = downloaded / (now - start_time) / 1024 / 1024  # MB/s
                      last_update = now
                  
                  # 打印进度+速度
                  self._print_progress(downloaded, total_size, speed)
      
      print(f"\n下载完成！平均速度：{speed:.2f} MB/s")
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
    
    def download_share_file(self, share_url, save_dir):
        """下载天翼云盘分享文件主函数"""
        # 创建保存目录
        # os.makedirs(save_dir, exist_ok=True)
  
        # 验证分享链接
        share_info = self.verify_share(share_url)
        
        # 第一层数据
        fileListAO = self.fileList_share(share_info)

        fileList = []
        # 判断是否有文件夹
        if (len(fileListAO['folderList']) != 0):
          # 第二层数据
          for item in fileListAO['folderList']:
            fileListAOTwo = self.fileList_share({
              **share_info,
              'fileId': item['id']
            })
            fileList.extend(fileListAOTwo['fileList'])
        
        # 排序后下载
        for fileListItem in self.sort_file_list(fileList):
            print(f"\n{'='*30} {fileListItem['name']} {'='*30}")
            if self._is_downloaded(fileListItem['id'], fileListItem['name']):
                print(f"✓ 历史文件已下载过，跳过: {fileListItem['name']}")
                continue
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
      {'name': '以法之名', 'url': 'https://cloud.189.cn/web/share?code=77nuYf3AjYJ3' },
      {'name': '锦绣芳华', 'url': 'https://cloud.189.cn/web/share?code=3YVJveiIzQne' },
      {'name': '书卷一梦', 'url': 'https://cloud.189.cn/web/share?code=BFzEzaaeaUB3' },
      {'name': '奔跑吧兄弟', 'url': 'https://cloud.189.cn/web/share?code=MVRBnqRRF3M3' }
    ]
        
    downloader = TianyiDownloader()
    try:
        for share_item in share_list:
          # 指定保存目录（默认为当前目录下的downloads文件夹）
          save_dir = f"Z:\download\下载\{share_item['name']}"
          downloader.download_share_file(share_item['url'], save_dir)
    except Exception as e:
        print(f"下载失败: {str(e)}")