import os

def rename_files():
  # 设置要处理的目录路径
  path = r'Z:\download\下载'
  for dirpath, dirnames, filenames in os.walk(path):
      for filename in filenames:
        #设置新文件名
        if "S01E" in filename:  # 确保是我们要处理的文件
          # 查找E01的位置
          e_index = filename.find("E")
          
          # 提取集数部分 (E后面的两位数字)
          episode_num = filename[e_index+1:e_index+3]
          
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
