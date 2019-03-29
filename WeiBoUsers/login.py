"""
Version: Python3.7
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/3/27 16:40
"""
import requests
import time
import json
import base64
import rsa
import binascii


class WeiBoLogin:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.session()
        self.cookie_file = "Cookie.json"
        self.nonce, self.pubkey, self.rsakv = "", "", ""
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}

    def save_cookie(self, cookie):
        """
        保存Cookie
        :param cookie: Cookie值
        :return:
        """
        with open(self.cookie_file, 'w') as f:
            json.dump(requests.utils.dict_from_cookiejar(cookie), f)

    def load_cookie(self):
        """
        导出Cookie
        :return: Cookie
        """
        with open(self.cookie_file, 'r') as f:
            cookie = requests.utils.cookiejar_from_dict(json.load(f))
            return cookie

    def pre_login(self):
        """
        预登录，获取nonce, pubkey, rsakv字段的值
        :return:
        """
        url = 'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&su=&rsakt=mod&client=ssologin.js(v1.4.19)&_={}'.format(int(time.time() * 1000))
        res = requests.get(url)
        js = json.loads(res.text.replace("sinaSSOController.preloginCallBack(", "").rstrip(")"))
        self.nonce, self.pubkey, self.rsakv = js["nonce"], js['pubkey'], js["rsakv"]

    def sso_login(self, sp, su):
        """
        发送加密后的用户名和密码
        :param sp: 加密后的用户名
        :param su: 加密后的密码
        :return:
        """
        data = {
            'encoding': 'UTF-8',
            'entry': 'weibo',
            'from': '',
            'gateway': '1',
            'nonce': self.nonce,
            'pagerefer': 'https://login.sina.com.cn/crossdomain2.php?action=logout&r=https%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D%252F',
            'prelt': '22',
            'pwencode': 'rsa2',
            'qrcode_flag': 'false',
            'returntype': 'META',
            'rsakv': self.rsakv,
            'savestate': '7',
            'servertime': int(time.time()),
            'service': 'miniblog',
            'sp': sp,
            'sr': '1920*1080',
            'su': su,
            'url': 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'useticket': '1',
            'vsnf': '1'}
        url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)&_={}'.format(int(time.time() * 1000))
        self.session.post(url, headers=self.headers, data=data)

    def login(self):
        """
        模拟登录主函数
        :return:
        """

        # Base64加密用户名
        def encode_username(usr):
            return base64.b64encode(usr.encode('utf-8'))[:-1]

        # RSA加密密码
        def encode_password(code_str):
            pub_key = rsa.PublicKey(int(self.pubkey, 16), 65537)
            crypto = rsa.encrypt(code_str.encode('utf8'), pub_key)
            return binascii.b2a_hex(crypto)  # 转换成16进制

        # 获取nonce, pubkey, rsakv
        self.pre_login()

        # 加密用户名
        su = encode_username(self.username)
        # 加密密码
        text = str(int(time.time())) + '\t' + str(self.nonce) + '\n' + str(self.password)
        sp = encode_password(text)

        # 发送参数，保存cookie
        self.sso_login(sp, su)
        self.save_cookie(self.session.cookies)
        self.session.close()

    def cookie_test(self):
        """
        测试Cookie是否有效，这里url要替换成个人主页的url
        :return:
        """
        session = requests.session()
        session.cookies = self.load_cookie()
        url = ''
        res = session.get(url, headers=self.headers)
        print(res.text)


if __name__ == '__main__':
    user_name = ''
    pass_word = ''
    wb = WeiBoLogin(user_name, pass_word)
    wb.login()
    wb.cookie_test()
