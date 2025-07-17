import os

# 视频格式的文件头签名（16进制）和对应后缀
VIDEO_SIGNATURES = {
    'MP4': {
        'sigs': ['66747970'],  # 'ftyp'
        'exts': ['.mp4', '.m4v']
    },
    'AVI': {
        'sigs': ['52494646'],  # 'RIFF'
        'exts': ['.avi']
    },
    'MKV': {
        'sigs': ['1A45DFA3'],  # MKV
        'exts': ['.mkv']
    },
    'MOV': {
        'sigs': ['66747970', '6D6F6F76'],  # 'ftyp' + 'moov'
        'exts': ['.mov']
    },
    'FLV': {
        'sigs': ['464C5601'],  # 'FLV.'
        'exts': ['.flv']
    },
    '3GP': {
        'sigs': ['667479703367'],  # 'ftyp3gp'
        'exts': ['.3gp']
    },
}

def get_file_signature(file_path, num_bytes=32):
    """读取文件前32字节的16进制签名"""
    with open(file_path, 'rb') as f:
        return f.read(num_bytes).hex().upper()

def detect_video_format(file_path):
    """检测视频真实格式"""
    signature = get_file_signature(file_path)
    for fmt, data in VIDEO_SIGNATURES.items():
        for sig in data['sigs']:
            if sig in signature[:20]:  # 放宽匹配范围
                return fmt
    return "Unknown"

def scan_mismatched_files(folder_path):
    """扫描并标记后缀名与真实格式不一致的文件"""
    mismatched_files = []
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            print(file_path)
            try:
                file_ext = os.path.splitext(file)[1].lower()
                real_format = detect_video_format(file_path)
                
                # 检查后缀是否匹配真实格式
                if real_format != "Unknown":
                    expected_exts = VIDEO_SIGNATURES[real_format]['exts']
                    if file_ext not in expected_exts:
                        mismatched_files.append({
                            'file': file,
                            'path': file_path,
                            'ext': file_ext,
                            'real_format': real_format,
                            'expected_exts': expected_exts
                        })
            except Exception as e:
                print(f"检测失败: {file} - {e}")
    # 输出结果
    if mismatched_files:
        print("=== 以下文件后缀名与真实格式不一致 ===")
        for item in mismatched_files:
            print(f"文件: {item['file']}")
            print(f"路径: {item['path']}")
            print(f"当前后缀: {item['ext']}")
            print(f"真实格式: {item['real_format']}")
            print(f"建议后缀: {', '.join(item['expected_exts'])}")
            print("-" * 50)
    else:
        print("所有文件的后缀名均与真实格式匹配。")

# 使用示例
folder_path = r"Z:\download\电视剧\锦绣芳华"
scan_mismatched_files(folder_path)