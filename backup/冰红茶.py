import random
import string
import qrcode
import os
# from PIL import Image

def generate_random_code(length=12):
    """生成12位随机码（大写字母 + 数字）"""
    characters = string.ascii_uppercase + string.digits
    # 可选：排除易混淆字符（如 O/0）
    exclude_chars = {'O', '0', '1', 'I', 'L'}
    characters = [c for c in characters if c not in exclude_chars]
    return ''.join(random.choice(characters) for _ in range(length))

def generate_url(base_url="HTTPS://25.KSF.CN"):
    """生成完整URL"""
    random_code = generate_random_code()
    return f"{base_url}?{random_code}"
    # return f"{base_url}?0HC44IDXR4QQKC"
    # HTTPS://25.KSF.CN/RN9VYHRO2U0KBG
    # HTTPS://25.KSF.CN?0HC44IDXR4QQKC
    # HTTPS://YYC.1U1M.CN/08H4YH9D3O4TLKV38C31


def generate_qrcode(url, save_path):
    """生成二维码并保存"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(save_path)

def main():
    # 创建保存二维码的文件夹
    os.makedirs("qrcodes", exist_ok=True)
    
    print("生成的URL及二维码：")
    for i in range(1, 10):  # 生成10个
        url = generate_url()
        print(f"{i}. {url}")
        
        # 保存二维码，文件名用随机码命名
        code = url.split("?")[1].split("#")[0]  # 提取随机码（如RN9VYHRO2U0KBG）
        save_path = f"qrcodes/{code}.png"
        generate_qrcode(url, save_path)
    
    print(f"\n所有二维码已保存至文件夹: {os.path.abspath('qrcodes')}")

if __name__ == "__main__":
    main()