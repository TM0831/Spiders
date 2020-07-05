"""
Version: Python3.7
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2020/7/5 14:19
"""
import execjs
import requests


class MTimeSpider:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def encrypted(self):
        """
        use JavaScript to encrypt the password
        :return:
        """
        with open("encrypt.js", "r", encoding="utf-8") as f:
            ctx = execjs.compile(f.read())
            self.password = ctx.call("encrypt", self.password)

    def request(self):
        """
        send request and get the response
        :return:
        """
        self.encrypted()
        login_api = "https://m.mtime.cn/Service/callback-comm.mi/user/login.api"
        data = {
            "t": "20207515574379774",
            "name": self.username,
            "password": self.password,
            "code": "",
            "codeId": ""
        }
        res = requests.post(url=login_api, data=data)
        status, msg = res.json()["data"]["status"], res.json()["data"]["msg"]
        # print(status, msg)
        if status == 1:
            name = res.json()["data"]["user"]["nickname"]
            print("用户： {} 登录成功！".format(name))
        else:
            print("登录失败！{}".format(msg))


if __name__ == '__main__':
    print("请输入账号：")
    usr = input()
    print("请输入密码：")
    pwd = input()
    spider = MTimeSpider(usr, pwd)
    spider.request()
