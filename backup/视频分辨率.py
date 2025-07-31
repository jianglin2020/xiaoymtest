import cv2
import os
import glob
import time

def get_video_info(video_path):
    """获取单个视频文件的分辨率和帧率（带重试机制）"""
    retries = 0
    max_retries = 3
    
    while retries < max_retries:
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"  尝试 {retries+1}/{max_retries}: 无法打开文件")
                retries += 1
                time.sleep(1)  # 等待1秒后重试
                continue
            
            # 获取分辨率和帧率
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            cap.release()
            return width, height, fps
            
        except Exception as e:
            print(f"  处理出错: {str(e)}")
            retries += 1
            time.sleep(1)
    
    return None, None, None

def get_folder_video_info(folder_path):
    """逐个获取文件夹中视频文件的信息并实时输出"""
    # 支持的视频文件扩展名
    video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.flv', '*.wmv', '*.mpg', '*.mpeg']
    
    print(f"扫描文件夹: {os.path.abspath(folder_path)}")
    print("-" * 60)
    
    video_files = []
    for ext in video_extensions:
        video_files.extend(glob.glob(os.path.join(folder_path, ext)))
    
    if not video_files:
        print("未找到视频文件")
        return
    
    print(f"找到 {len(video_files)} 个视频文件\n")
    
    # 打印表头 - 增加帧率列
    print(f"{'序号':<6} {'视频文件':<20} {'分辨率':<15} {'帧率':<12} {'类型':<10} {'状态':<10}")
    print("-" * 95)
    
    results = []
    success_count = 0
    fail_count = 0
    
    for i, video_path in enumerate(video_files, 1):
        filename = os.path.basename(video_path)
        print(f"{i:<8} {filename:<25}", end="", flush=True)
        
        start_time = time.time()
        width, height, fps = get_video_info(video_path)
        elapsed = time.time() - start_time
        
        if width is not None and height is not None and fps is not None:
            # 计算宽高比
            ratio = f"{width}:{height}"
            
            # 确定分辨率类型
            if width >= 7680 or height >= 4320:
                res_type = "8K"
            elif width >= 3840 or height >= 2160:
                res_type = "4K"
            elif width >= 1920 or height >= 1080:
                res_type = "Full HD"
            elif width >= 1280 or height >= 720:
                res_type = "HD"
            elif width >= 854 or height >= 480:
                res_type = "SD"
            else:
                res_type = "低分辨率"
            
            # 格式化帧率显示
            if fps > 0:
                fps_str = f"{fps:.2f} fps"
            else:
                fps_str = "未知"
            
            print(f"{width}×{height:<13} {fps_str:<14} {res_type:<12} 成功 ({elapsed:.2f}s)")
            results.append((filename, width, height, fps))
            success_count += 1
        else:
            print(f"{'N/A':<18} {'N/A':<15} {'N/A':<14} 失败 ({elapsed:.2f}s)")
            fail_count += 1
    
    # 统计信息
    print("\n" + "=" * 60)
    print(f"扫描完成: 共处理 {len(video_files)} 个文件")
    print(f"成功: {success_count} | 失败: {fail_count}")
    
    if results:
        resolutions = set(f"{width}×{height}" for _, width, height, _ in results)
        print(f"发现的不同分辨率: {len(resolutions)}")
        
        # 显示分辨率分布
        print("\n分辨率分布:")
        res_counts = {}
        for _, width, height, _ in results:
            res_key = f"{width}×{height}"
            res_counts[res_key] = res_counts.get(res_key, 0) + 1
        
        # 按数量降序排序
        sorted_counts = sorted(res_counts.items(), key=lambda x: x[1], reverse=True)
        
        for res, count in sorted_counts:
            print(f"  {res}: {count} 个文件")
        
        # 帧率统计（可选）
        if any(fps > 0 for _, _, _, fps in results):
            print("\n帧率统计:")
            fps_counts = {}
            for _, _, _, fps in results:
                if fps > 0:
                    # 将帧率分组
                    rounded_fps = round(fps)
                    if rounded_fps < 20:
                        fps_key = "低帧率 (<20)"
                    elif rounded_fps == 24:
                        fps_key = "24 fps (电影)"
                    elif rounded_fps == 30:
                        fps_key = "30 fps (标准)"
                    elif rounded_fps == 60:
                        fps_key = "60 fps (流畅)"
                    else:
                        fps_key = f"{rounded_fps} fps"
                    
                    fps_counts[fps_key] = fps_counts.get(fps_key, 0) + 1
                else:
                    fps_key = "未知帧率"
                    fps_counts[fps_key] = fps_counts.get(fps_key, 0) + 1
            
            for fps_type, count in fps_counts.items():
                print(f"  {fps_type}: {count} 个文件")

if __name__ == "__main__":
    # 设置要扫描的文件夹路径
    folder_path = r"X:\天翼\nas\电视剧\凡人修仙传(2020)"  # 替换为你的实际路径
    
    # 检查路径是否存在
    if not os.path.exists(folder_path):
        print(f"错误: 路径 '{folder_path}' 不存在")
    elif not os.path.isdir(folder_path):
        print(f"错误: '{folder_path}' 不是文件夹")
    else:
        get_folder_video_info(folder_path)