# quark_checker.py
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse
import time

def is_quark_link_expired(url):
    """
    使用 Selenium 3.x 检测夸克网盘链接是否失效
    
    参数:
        url (str): 夸克网盘分享链接
        
    返回:
        bool: True（链接失效） | False（链接有效）
    """
    try:
        # 验证URL格式
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return True
            
        if 'quark.cn' not in parsed.netloc:
            return True  # 非夸克链接

        # 设置 Chrome 无头模式
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')  # 禁用 GPU 加速
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--log-level=3')  # 只显示致命错误
        options.add_argument('--disable-logging')  # 禁用日志
        options.add_argument('--silent')  # 静默模式
        options.add_experimental_option('excludeSwitches', ['enable-logging'])  # 隐藏 DevTools 监听日志
        
        # Selenium 3.x 写法
        driver = webdriver.Chrome(
            executable_path=ChromeDriverManager().install(),
            options=options
        )
        
        driver.get(url)
        time.sleep(3)  # 等待页面加载

        expired_keywords = [
            "该分享已被取消，无法访问",
            "文件涉及违规内容已失效",
            "分享地址已失效"
        ]
        
        page_content = driver.page_source
        driver.quit()

        for keyword in expired_keywords:
            if keyword in page_content:
                return True
                
        return False
        
    except Exception as e:
        print(f"检测出错: {e}")
        return True

# 测试代码（可选）
if __name__ == "__main__":
    test_url = "https://pan.quark.cn/s/f06e211473c7"
    print("🔴 链接已失效" if is_quark_link_expired(test_url) else "🟢 链接有效")