"""
Version: Python3.5
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/2/9 16:46
"""
import re
import json
import time
import requests
from fake_useragent import UserAgent


ua = UserAgent()
city_dict = dict()


# 获取城市-编码字典
def get_city_dict():
    url = "http://map.weather.com.cn/static_data/101.js"
    headers = {
        "User-Agent": ua.random
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
                city_dict[i[0] + "-" + j['data-name']] = j['data-id']
            else:
                city_dict[i[0] + "-" + j['data-name']] = j['data-id'] + "01"
    # print(.city_dict)


# 获取城市对应的编码
def get_city_id(city_name):
    result = [(k, city_dict[k]) for k in city_dict.keys() if city_name in k]
    city_id = ""
    if len(result) == 0:  # 如果字典中没有相关数据就报错
        print("Error!")
        exit()
    elif len(result) == 1:
        city_id = result[0][1]
    else:
        for i in range(len(result)):  # 说明地名有相同的
            print(i, result[i])
        city_id = result[int(input("请确定您的城市的序号："))][1]
    return city_id


# 爬取天气信息
def get_weather(city_name):
    get_city_dict()
    city_id = get_city_id(city_name)
    url = "http://d1.weather.com.cn/sk_2d/{}.html?_=1544842784069".format(city_id)
    # 如果User-Agent被识别出来了，就再重新随机一个UA
    while 1:
        headers = {
            "Referer": "http://www.weather.com.cn/weather1d/{}.shtml".format(city_id),
            "User-Agent": ua.random
        }
        res = requests.get(url, headers=headers)
        if not re.search('FlashVars', res.text):
            break
    res.encoding = "utf-8"
    js = json.loads(res.text.lstrip('var dataSK = '))
    weather_info = {
        "日期": js['date'],
        "天气": js['weather'],
        "温度": js['temp'] + '℃',
        "PM2.5": js['aqi_pm25'],
        "相对湿度": js['SD'],
    }
    return weather_info
