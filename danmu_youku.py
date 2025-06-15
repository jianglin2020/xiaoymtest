import requests
import re
import os
from urllib.parse import urlparse, parse_qs

def ensure_directory_exists(dir_path):
    """确保目录存在，如果不存在则创建"""
    os.makedirs(dir_path, exist_ok=True)
    print(f"确保目录存在: {os.path.abspath(dir_path)}")

def extract_youku_vid(url):
    """从优酷URL提取vid"""
    # 尝试从查询参数获取
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    if 'vid' in params:
        return params['vid'][0]
    
    # 尝试从路径获取（新格式）
    match = re.search(r'/id_([^\.]+)\.html', url)
    if match:
        return match.group(1)
    
    return None

def generate_dmku_url(vid):
    """生成DMKU弹幕链接"""
    return f"https://dmku.thefilehosting.com/?ac=dm&url=https://v.youku.com/v_show/id_{vid}.html"

def fetch_danmaku_data(dmku_url):
    """从DMKU获取弹幕数据"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"正在访问: {dmku_url}")
        response = requests.get(dmku_url, headers=headers, timeout=10)
        response.raise_for_status()  # 检查请求是否成功
        
        # 解析JSON数据
        danmaku_data = response.json()
        return danmaku_data
        
    except Exception as e:
        print(f"获取弹幕失败: {str(e)}")
        return None

def json_to_bilibili_ass(
    danmaku_data, 
    output_ass_path,
    max_lines=6,            # 上部1/3区域约6行
    scroll_speed=1.0,       # 滚动速度
    fixed_duration=4.0,     # 固定弹幕持续时间
    scroll_duration=8.0,    # 滚动弹幕基准时间
    play_res_x=560,         # 画面宽度
    play_res_y=420          # 画面高度
):
    """将JSON弹幕数据直接转换为ASS文件(非粗体白色弹幕，上部1/3区域，18px字体)
    
    Args:
        danmaku_data: 弹幕JSON数据
        output_ass_path: 输出ASS文件路径
        max_lines: 上部区域最大行数
        scroll_speed: 滚动速度 (1.0=正常)
        fixed_duration: 固定弹幕显示时间(秒)
        scroll_duration: 滚动弹幕基准时间(秒)
        play_res_x: 画面水平分辨率
        play_res_y: 画面垂直分辨率
    """
    # 固定设置
    font_size = 18
    font_name = "Microsoft YaHei UI"
    top_region_height = play_res_y // 3  # 上部1/3区域高度
    danmaku_color = "&H00FFFFFF"  # 白色（ASS颜色格式BBGGRR）
    outline_color = "&H00000000"  # 黑色描边
    
    # 创建ASS文件头部（非粗体样式）
    ass_header = f"""[Script Info]
Title: 非粗体白色弹幕 (上部1/3区域)
Original Script: 根据弹幕数据生成
ScriptType: v4.00+
Collisions: Normal
PlayResX: {play_res_x}
PlayResY: {play_res_y}
Timer: 10.0000

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Fix,{font_name},{font_size},{danmaku_color},{danmaku_color},{outline_color},{outline_color},0,0,0,0,100,100,0,0,1,2,0,8,20,20,2,0
Style: R2L,{font_name},{font_size},{danmaku_color},{danmaku_color},{outline_color},{outline_color},0,0,0,0,100,100,0,0,1,2,0,7,20,20,2,0

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    
    # 准备弹幕事件
    events = []
    
    # 计算行高和Y坐标位置（仅在上部1/3区域）
    line_height = top_region_height // max_lines
    r2l_y_positions = [int(line_height * (i + 0.5)) for i in range(max_lines)]
    r2l_index = 0
    
    for danmaku in danmaku_data['danmuku']:
        try:
            # 解析时间
            start_seconds = float(danmaku[0])
            hours = int(start_seconds // 3600)
            minutes = int((start_seconds % 3600) // 60)
            seconds = int(start_seconds % 60)
            centiseconds = int((start_seconds - int(start_seconds)) * 100)
            start_time = f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"
            
            # 弹幕文本
            text = danmaku[4]
            
            # 强制使用白色，忽略原始颜色数据
            color_override = "\\c" + danmaku_color.replace("&H00", "&H")
            
            # 根据弹幕类型处理
            if danmaku[1] == 'top':
                # 顶部固定弹幕（居中显示）
                end_seconds = start_seconds + fixed_duration
                end_time = f"{hours}:{minutes:02d}:{(seconds + int(fixed_duration)):02d}.{centiseconds:02d}"
                event = f"Dialogue: 0,{start_time},{end_time},Fix,,20,20,2,,{{\\fs{font_size}{color_override}\\pos({play_res_x//2},{line_height//2})}}{text}"
            elif danmaku[1] == 'right':
                # 从右向左滚动弹幕（仅在上部区域）
                y_pos = r2l_y_positions[r2l_index % max_lines]
                r2l_index += 1
                
                # 调整持续时间
                adjusted_duration = scroll_duration / scroll_speed
                end_seconds = start_seconds + adjusted_duration
                end_time = f"{hours}:{minutes:02d}:{(seconds + int(adjusted_duration)):02d}.{centiseconds:02d}"
                
                # 计算移动路径（18px字体专用系数）
                text_length = len(text)
                start_x = play_res_x + text_length * 8
                end_x = -text_length * 12
                
                event = f"Dialogue: 0,{start_time},{end_time},R2L,,20,20,2,,{{\\fs{font_size}{color_override}\\move({start_x},{y_pos},{end_x},{y_pos})}}{text}"
            else:
                continue
            
            events.append(event)
        except Exception as e:
            print(f"处理弹幕时出错: {danmaku}，错误: {str(e)}")
            continue
    
    # 写入ASS文件
    with open(output_ass_path, 'w', encoding='utf-8-sig') as f:
        f.write(ass_header)
        f.write("\n".join(events))

if __name__ == "__main__":
    # 定义基础输出目录
    output_dir = './output/藏海传'
    ensure_directory_exists(output_dir)

    # 优酷视频列表
    video_list = [
        {'name': '33', 'url': 'https://v.youku.com/video?vid=XNjQ4MDEzODgyNA==&s=06efbfbd08efbfbdefbf&scm=20140719.apircmd.298496.video_XNjQ4MDEzODgyNA==&spm=a2hkt.13141534.1_6.d_1_33'},
        {'name': '34', 'url': 'https://v.youku.com/video?vid=XNjQ3MjQzMDYyNA==&s=06efbfbd08efbfbdefbf&scm=20140719.apircmd.298496.video_XNjQ3MjQzMDYyNA==&spm=a2hkt.13141534.1_6.d_1_34'},
        {'name': '35', 'url': 'https://v.youku.com/video?vid=XNjQ4MDE0MDYyNA==&s=06efbfbd08efbfbdefbf&scm=20140719.apircmd.298496.video_XNjQ4MDE0MDYyNA==&spm=a2hkt.13141534.1_6.d_1_35'},
        {'name': '36', 'url': 'https://v.youku.com/video?vid=XNjQ3MjQyNzc2MA==&s=06efbfbd08efbfbdefbf&scm=20140719.apircmd.298496.video_XNjQ3MjQyNzc2MA==&spm=a2hkt.13141534.1_6.d_1_36'}
    ]
    
    for video in video_list:
        print(f"\n处理视频: {video['name']}")
        vid = extract_youku_vid(video['url'])
        if not vid:
            print(f"无法从URL中提取vid: {video['url']}")
            continue
        
        # 生成DMKU链接
        dmku_url = generate_dmku_url(vid)
        print(f"生成的DMKU链接: {dmku_url}")
        
        # 获取弹幕数据
        danmaku_data = fetch_danmaku_data(dmku_url)
        if not danmaku_data:
            continue

        # 生成输出文件路径（修正部分）
        output_ass_path = os.path.join(output_dir, f"{video['name']}.ass")
        
        # 直接转换为ASS文件
        json_to_bilibili_ass(
            danmaku_data=danmaku_data,
            output_ass_path=output_ass_path,
            max_lines=6,
            scroll_speed=0.8,
            fixed_duration=4.0,
            scroll_duration=7.0
        )
        print(f"ASS文件已生成: {os.path.abspath(output_ass_path)}")