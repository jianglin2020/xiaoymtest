import os
import re

def rename_files():
  # 设置要处理的目录路径
  path = r'Z:\download\下载'
  for dirpath, dirnames, filenames in os.walk(path):
      for filename in filenames:
          # 使用正则表达式匹配集数部分
          match = re.search(r"S01E(\d{2,3})", filename)
          # match = re.search(r"2021.E(\d{2,3})", filename)
          
          if match:
              # 提取匹配到的集数
              episode_num = match.group(1)
              
              # 获取文件扩展名
              ext = os.path.splitext(filename)[1]
              # 构建新文件名
              new_filename = episode_num + ext
              
              # 重命名文件
              old_path = os.path.join(dirpath, filename)
              new_path = os.path.join(dirpath, new_filename)

              os.rename(old_path, new_path)
              print(f"Renamed: {filename} -> {new_filename}")


if __name__ == "__main__":
    rename_files()
