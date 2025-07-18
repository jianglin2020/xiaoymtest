import os
import rsa
import requests
from urllib.parse import parse_qs
from dotenv import load_dotenv, set_key

# 加载环境变量
load_dotenv(dotenv_path='.env.local', verbose=True)

class TianyiCloudLogin:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json;charset=UTF-8'
        })
        
        # 天翼云URL
        self.AUTH_URL = "https://open.e.189.cn"

    # 保存cookie
    def save_cookie(self, cookie):
        set_key('.env.local', "TIANYI_COOKIE", cookie)
        print(f"Cookie已保存到 .env.local")

    def _check_error(self, response):
        try:
            data = response.json()
            if 'errorCode' in data:
                raise Exception(f"天翼云错误: {data.get('errorMsg', '未知错误')} (代码: {data['errorCode']})")
        except ValueError:
            pass
    
    def get_encrypt_config(self):
        """获取加密配置"""
        url = f"{self.AUTH_URL}/api/logbox/config/encryptConf.do"
        response = self.session.post(url)
        self._check_error(response)
        return response.json()
    
    def get_login_params(self):
        """获取登录页面参数"""    
        response = self.session.get("https://cloud.189.cn/api/portal/loginUrl.action")

        # 从url中提取关键参数 url.query
        query_params = parse_qs(response.url)  # 返回字典，值为列表（因为参数可重复）

        url = f"{self.AUTH_URL}/api/logbox/oauth2/appConf.do"

        self.session.headers.update({
            'Referer': self.AUTH_URL,
            'lt': query_params['lt'][0],
            'reqId': query_params['reqId'][0],
        })

        data = {
            'appKey': 'cloud',
            'version': '2.0',
        }

        response = self.session.post(url, data=data)
        print(response.json())

        return response.json().get('data', {})
   
            
    def login_by_password(self):
        """使用用户名密码登录"""
        print("登录天翼云...")
        # 获取 环境变量值
        username = os.getenv('tianyiUsername')
        password = os.getenv('tianyiPassword')
        
        # 1. 获取加密配置和登录参数
        encrypt_config = self.get_encrypt_config()['data']
        login_params = self.get_login_params()

        # 构造RSA公钥
        pub_key = rsa.PublicKey.load_pkcs1_openssl_pem(
            f"-----BEGIN PUBLIC KEY-----\n{encrypt_config['pubKey']}\n-----END PUBLIC KEY-----".encode()
        )

        # RSA加密用户名和密码
        username_encrypted = rsa.encrypt(username.encode(), pub_key).hex()
        password_encrypted = rsa.encrypt(password.encode(), pub_key).hex()
        
        # 2. 构建登录表单数据
        data = {
            'version': 'v2.0',
            'appKey': 'cloud',
            'pageKey': 'normal',
            'accountType': login_params['accountType'],
            'userName': f"{encrypt_config['pre']}{username_encrypted}",
            'epd': f"{encrypt_config['pre']}{password_encrypted}",
            'validateCode': '',
            'captchaToken': '',
            'dynamicCheck': 'FALSE',
            'clientType': '1',
            'cb_SaveName': '3',
            'isOauth2': 'false',
            'returnUrl': login_params['returnUrl'],
            'paramId': login_params['paramId']
        }

        # 3. 提交登录请求
        login_url = f"{self.AUTH_URL}/api/logbox/oauth2/loginSubmit.do"
        
        response = self.session.post(login_url, data=data)

        print(response.json())
        self._check_error(response)
        login_result = response.json()
        
        # 4. 获取session
        return self._get_session_for_web(login_result['toUrl'])
    
    def _get_session_for_web(self, redirect_url):

        print(redirect_url)
        """获取web端session"""
        response = self.session.get(redirect_url)

        # 检查重定向历史
        cookie = response.history[0].cookies.get_dict()     

        # 转换为字符串格式
        cookies_str = '; '.join([f'{k}={v}' for k, v in cookie.items()])
        
        #保存cookie
        self.save_cookie(cookies_str)
        return cookies_str

# 使用示例
if __name__ == "__main__":
    # 创建登录实例
    cloud_login = TianyiCloudLogin()

    try:
        # 执行登录
        login_result = cloud_login.login_by_password()

        print("登录成功!")
        print("cookie信息:", login_result)
        
    except Exception as e:
        print("登录失败:", str(e))