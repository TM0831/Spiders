"""
Version: Python3.7
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/12/1 13:39
"""
import re
import time
import random
import logging
import pymongo
import requests
from lxml import etree
from multiprocessing import Pool
from pyecharts.charts import Bar
import pyecharts.options as opts


headers = {
    "Cookie": "pgv_pvi=9664493568; RK=V3YFZBzIaf; ptcz=dd1b29a0825c2b89b2a6c0be8de3c4703f0d3200ddf9187192521cc1ece"
              "fdd97; pgv_pvid=9380910985; eas_sid=h1x5Z6D3b9S4i4T2K8P5Y3T543; tvfe_boss_uuid=c9519be189685c52; _g"
              "a=amp-iCXI0A0Wl1HW9SvRHkHTgA; o_cookie=512880290; pac_uid=1_512880290; ied_qq=o0512880290; sensorsd"
              "ata2015jssdkcross=%7B%22distinct_id%22%3A%2216e0b29b9ad53f-0d01c45deb6f87-b363e65-1327104-16e0b29b9"
              "ae3b8%22%2C%22%24device_id%22%3A%2216e0b29b9ad53f-0d01c45deb6f87-b363e65-1327104-16e0b29b9ae3b8%22%"
              "2C%22props%22%3A%7B%22%24latest_referrer%22%3A%22https%3A%2F%2Fwww.baidu.com%2Flink%22%2C%22%24late"
              "st_referrer_host%22%3A%22www.baidu.com%22%2C%22%24latest_traffic_source_type%22%3A%22%E8%87%AA%E7%8"
              "4%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%9"
              "6%E5%88%B0%E5%80%BC%22%7D%7D; ptui_loginuin=1952963432; wr_localvid=; wr_name=; wr_avatar=; wr_gend"
              "er=; wr_gid=217986062",
    "Host": "weread.qq.com",
    "Referer": "https://weread.qq.com/",
    "UserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904"
                 ".108 Safari/537.36"
}

MONGO_HOST = "127.0.0.1"
MONGO_PORT = 27017
MONGO_DB = "Spiders"
MONGO_COL = "WeRead"


requests.packages.urllib3.disable_warnings()
logging.basicConfig(datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO, format="%(asctime)s - %(name)s: %(message)s")
