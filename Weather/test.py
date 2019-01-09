"""
Version: Python3.5
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2018/12/15 12:19
"""
import re
import json
import time
import smtplib
import requests
from lxml import etree
from pprint import pprint
from email.header import Header
from email.mime.text import MIMEText


def get_agent():
    import random
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]
    return random.choice(user_agent_list)


class Weather:
    def __init__(self):
        self.city_name = ""
        self.city_id = ""
        self.city_dict = {}
        self.weather_info = {}
        self.sender = "xxx@163.com"  # 发件人
        self.password = "xxx"  # 授权码
        self.receiver = "xxx@163.com"  # 收件人

    # 获取城市-编码字典
    def get_city_dict(self):
        url = "http://map.weather.com.cn/static_data/101.js"
        headers = {
            "User-Agent": get_agent()
        }
        res = requests.get(url, headers=headers)
        js = json.loads(res.text.lstrip('var map_config_101='))
        province_list = []
        for i in js['text']['inner']:
            province_list.append((i['data-name'], i['data-id']))
        for i in province_list:
            time.sleep(1)
            href = "http://map.weather.com.cn/static_data/{}.js".format(i[1])
            res = requests.get(href, headers=headers)
            js = json.loads(res.text.lstrip('var map_config_{}='.format(i[1])))
            for j in js['text']['inner']:
                if i[0] in ['北京', '上海', '天津', '重庆']:
                    self.city_dict[i[0] + "-" + j['data-name']] = j['data-id']
                else:
                    self.city_dict[i[0] + "-" + j['data-name']] = j['data-id'] + "01"
        # print(self.city_dict)

    # 获取城市对应的编码
    def get_city_id(self):
        self.city_name = input("请输入城市名：")
        result = [(k, self.city_dict[k]) for k in self.city_dict.keys() if self.city_name in k]
        if len(result) == 0:  # 如果字典中没有相关数据就报错
            print("Error!")
        elif len(result) == 1:
            self.city_id = result[0][1]
        else:
            for i in range(len(result)):  # 说明地名有相同的
                print(i, result[i])
            self.city_id = result[int(input("请确定您的城市的序号："))][1]
        # print(self.city_id)

    # 爬取天气信息
    def get_weather(self):
        url1 = "http://d1.weather.com.cn/sk_2d/{}.html?_=1544842784069".format(self.city_id)
        # 如果User-Agent被识别出来了，就再重新随机一个UA
        while 1:
            headers = {
                "Referer": "http://www.weather.com.cn/weather1d/{}.shtml".format(self.city_id),
                "User-Agent": get_agent()
            }
            res1 = requests.get(url1, headers=headers)
            if not re.search('FlashVars', res1.text):
                break
        res1.encoding = "utf-8"
        js = json.loads(res1.text.lstrip('var dataSK = '))
        url2 = "http://www.weather.com.cn/weather1d/{}.shtml".format(self.city_id)
        # 如果User-Agent被识别出来了，就再重新随机一个UA
        while 1:
            headers = {
                "Referer": "http://www.weather.com.cn/weather1d/{}.shtml".format(self.city_id),
                "User-Agent": get_agent()
            }
            res2 = requests.get(url2, headers=headers)
            if not re.search('FlashVars', res2.text):
                break
        res2.encoding = "utf-8"
        s = etree.HTML(res2.text)
        info1 = s.xpath('//*[@class="li1 hot"]/p/text()')[0]  # 紫外线指数
        info2 = s.xpath('//*[@id="chuanyi"]/a/p/text()')[0]  # 穿衣指数
        info3 = s.xpath('//*[@class="li4 hot"]/p/text()')[0]  # 洗车指数
        self.weather_info = {
            "城市": js['cityname'],
            "日期": js['date'],
            "天气": js['weather'],
            "温度": js['temp'] + '℃',
            "风向": js['WD'],
            "风力等级": js['WS'],
            "相对湿度": js['SD'],
            "PM2.5": js['aqi_pm25'],
            "紫外线指数": info1,
            "穿衣指数": info2,
            "洗车指数": info3
        }
        pprint(self.weather_info)  # 更好的打印Json格式数据

    # 发送邮件
    def send_email(self):
        try:
            mail = MIMEText(str(self.weather_info), 'plain', 'utf-8')  # 邮件内容
            mail['Subject'] = Header('今日天气预报', 'utf-8')  # 邮件主题
            mail['From'] = self.sender  # 发件人
            mail['To'] = self.receiver  # 收件人
            smtp = smtplib.SMTP()
            smtp.connect('smtp.163.com', 25)  # 连接邮箱服务器
            smtp.login(self.sender, self.password)  # 登录邮箱
            smtp.sendmail(self.sender, self.receiver, mail.as_string())  # 第三个是把邮件内容变成字符串
            smtp.quit()  # 发送完毕，退出
            print('邮件已成功发送！')
        except Exception as e:
            print(e)


if __name__ == '__main__':
    w = Weather()
    w.get_city_dict()
    w.get_city_id()
    w.get_weather()
    w.send_email()