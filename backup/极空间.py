import requests
from tqdm import tqdm
import os

def download_video(url, cookie_str, output_path):
    """
    携带 Cookie 下载视频（支持进度条）
    
    :param url:      视频文件的直链地址
    :param cookie_str: Cookie 字符串，格式如 'name1=value1; name2=value2'
    :param output_path: 保存的视频文件路径（例如 'video.mp4'）
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": cookie_str
    }
    
    # 发送请求，流式获取
    resp = requests.get(url, headers=headers, stream=True, timeout=30)
    resp.raise_for_status()
    
    total_size = int(resp.headers.get('content-length', 0))
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # 进度条写入文件
    with open(output_path, 'wb') as f, tqdm(
        desc=output_path,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                bar.update(len(chunk))
    
    print(f"\n✅ 下载完成：{output_path}")

# ========== 使用示例 ==========
if __name__ == "__main__":
    # 你要下载的视频 URL
    video_url = "https://www.zconnect.cn/splay/ZE.oJJaioW0HlRvUyNZWiM7m2OXdQ5m2O5cs8ODYUDsJUDZxj5OkMneRm37KcgH9gusnjMy6SEUSQL0wjpb8m289uwfanP6rkxc31gfYkcXy7UEOhAm4/01.mp4"

    # 从浏览器复制的 Cookie（字符串形式）
    my_cookie = "isAllFlash=0; webagent=v2; qcname=; nickname=admin; isLocal=0; deviceMode=z2s; _l=zh_cn; device_id=3682491ba55ac98fc7a4b7786b8a933e; nas_id=Z02101B3D5A33; zenithtoken=108MSQlMTc3NTkyMjg5OCQlMTY2NzEyOTY1OCQlMzY4MjQ5MWJhNTVhYzk4Zm1M3YTRiNzc4Nm1I4YTkzM2UkJTE3NjEwODM1ODgwJCVybwm4m4WB8E0xqb6nOoRY9GkrCGihsK944RGOxm3ZdotDFzHjOKm2hlqoJuah5t5f2lUr7l4m2cm1ryZeGHwroO7VDm1k5rFJVQ3DEsiXTpfWiv7wqFL04pkzEfoZQsa83CReYlnw0rWsXP2tat9v1ARdCJm3rjCWs0rnrGRIlhCUGum374m22tDscccQtM9WEm2l345Ktsjm23K6GnTcQbcTkMnJg2LCFLaPlhHojBhxSSwdS4m3GegW7RUm2NeBcwKs7VNai94Fjm27x2VUKKdNM1m1faHvF5Ynbbz0hdem25jjW0GltlpE7RlFM3Ag86HiwpAxWGSX9z1cWElVMMLm1C6uewiGATEim3Zm3Dm3m3AAm4m4; username=176xxxx5880; userid=1; isMaster=1; nasIp=192.168.1.140:5055; deviceColor=pl_deep_gray_metallic_paint; devicePdt=z2; plat=web; app=file; cloudPubKey=-----BEGIN%20PUBLIC%20KEY-----%0AMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDEeoIJVvpk0NDObnyn66lVH5n+%0A8E4SwM7RJhdFBbubSelWQdmPyAVSAi1Qlxb8Q0gsd8C2QwNfhCBKoncmhLnA6+tf%0AIxxZM5VjA/GHy7NwZ5zSUCoNTdsSl5oFu/XUu/+Tr+usAiIUSXiRADxMnSEos8r+%0AtmmXGcn7zpxB7jLEzwIDAQAB%0A-----END%20PUBLIC%20KEY-----; cloudPubKeyId=v1; nas_name=Z2S-5A33; sign=061WjAyMTAxQjNENUEzM18xNzc1OTIyOTA0XzYwNTczMzI2NjU2MDQ3NzkyMDYm4Q9pkFPm1q4hxWGA7L2wRm1VcZM1m1Uc4w2QGWDuoq3m37zM7QWStqfPm14KQXAB7m24EE9y12Tm2AEQT4m3qL7yUE4hVDN356JWuB6NTRtLm3Ym38CJNMiqi1tZMGgGLon8eA2NHL32Pl0im1SvtuMbHtrucXinxm3deOYWgU3Wpl31TnZCEgF9eIPm1m36pHdUcACwMCzfs1dUOVsJJWoL731GgMjxGklDqQsEzDORUm1pACZ692w1w9NQDFzTuLGxW5Q8Wnlm3qm1Oc5TgUhkWRqtPrT1X81K1PNnm3P3hfzgyntMuwFScgXCm2jBZIp7C6G9WQOiNQwzvVem3DBpNMrm3YIRppJJOkfAcCPwm4m4; nasPubKey=-----BEGIN%20PUBLIC%20KEY-----%0AMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvsoxRKckrH7mFRR2kjbF%0ARkmQgy1/oy/+dRYafU4cY6oPYyUu7cIigTGFaJsQa5k+uYGXOzvC6m0ISHLjNwlz%0AdwCti+awBMPlSWjTxAN2MlDZDv69CLPgZCFT8MFKD6kiBAaqjFAzR1d+N4ln637B%0Ahbt8z9hDGZ0468H54HOFzoOUvHfGWuFfHpdd2SBHeqgTMg/UkE7hllZaA0hFONDc%0AUfnbGwQ222BtDm+6BXfCKoC8LvEe9yEmHgu7Y/dc827dhNMicSLXQ+iLyaR9bgWu%0AmtD0F+zZjzjGnCxtW9vBa7epw3G29oGqxHwSxFMlUUICKxenAObPI9+DYhRb+Cr7%0AkwIDAQAB%0A-----END%20PUBLIC%20KEY-----; publicSwitch=false; version=2.3.2025122901; device=PC%20(Chrome/109.0.0.0)"
    
    # 保存路径
    save_as = "./downloaded_video.mp4"
    
    download_video(video_url, my_cookie, save_as)