"""
Version: Python3.7
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2020/6/28 14:45
"""
import time
import execjs
import requests
from lxml import etree
from XiaoNiu.CJYDemo import use_cjy


class XNSpider:
    def __init__(self, username, password):
        self.url = "https://www.xiaoniu88.com/user/login"
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": "_ga=GA1.2.1575428040.1593311456; _gid=GA1.2.390668910.1593311456; Hm_lvt_7226b8c48cd07619c7a9ebd471d9d589=1593311456; SESSIONID=486a67f0-85e9-4c92-8bbf-35f5fe7438f9; sr=331271.43.11.3.101.54.204.169.0.33.20.15.07; Hm_lpvt_7226b8c48cd07619c7a9ebd471d9d589=1593329691",
            "Host": "www.xiaoniu88.com",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
        }
        self.username = username
        self.password = password

    def get_token(self):
        """
        获取token
        :return:
        """
        res = requests.get(self.url, headers=self.headers)
        if res.status_code == 200:
            et = etree.HTML(res.text)
            token_name = et.xpath('//*[@id="ooh.token.name"]/@value')[0]
            token_value = et.xpath('//*[@id="ooh.token.value"]/@value')[0]
            return token_name, token_value
        print("状态码：{}，请求页面出错，终止程序！".format(res.status_code))
        exit()

    def encrypt(self):
        """
        调用JS代码进行加密
        :return:
        """
        with open("encrypt.js", "r", encoding="utf-8") as f:
            ctx = execjs.compile(f.read())
        self.password = ctx.call("encrypt", self.password)

    @staticmethod
    def get_captcha():
        url = "https://www.xiaoniu88.com/user/captcha"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;"
                      "q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9","Cache-Control": "max-age=0","Connection": "keep-alive",
            "Cookie": "_ga=GA1.2.1575428040.1593311456; _gid=GA1.2.390668910.1593311456; Hm_lvt_7226b8c4"
                      "8cd07619c7a9ebd471d9d589=1593311456; SESSIONID=486a67f0-85e9-4c92-8bbf-35f5fe7438f9; sr=33127"
                      "1.43.11.3.101.54.204.169.0.33.20.15.07; Hm_lpvt_7226b8c48cd07619c7a9ebd471d9d589=1593329691",
            "Host": "www.xiaoniu88.com",
            "Referer": "https://www.xiaoniu88.com/user/login",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/83.0.4103.116 Safari/537.36"
        }
        res = requests.get(url, headers=headers, stream=True)
        if res.status_code == 200:
            with open("captcha.jpg", "wb") as f:
                f.write(res.content)
        else:
            print("状态码：{}，请求验证码出错，终止程序！".format(res.status_code))
            exit()

    def login(self):
        """
        登录方法
        :return:
        """
        url = self.url + "?" + str(int(time.time()) * 1000)
        token = self.get_token()
        self.get_captcha()
        captcha = use_cjy("captcha.jpg")
        if captcha["err_no"]:
            print("验证码识别出错，终止程序！")
            exit()
        data = {
            "ooh.token.name": token[0],
            "ooh.token.value": token[1],
            "username": self.username,
            "password": self.encrypt(),
            "code": captcha["pic_str"]
        }
        res = requests.post(url, headers=self.headers, data=data)
        print(res.json())
        try:
            if res.json()["resultCode"] == 0:
                print("登录成功！")
            else:
                print("登录失败！")
        except Exception as e:
            print(e)


if __name__ == "__main__":
    spider = XNSpider("", "")
    spider.login()
