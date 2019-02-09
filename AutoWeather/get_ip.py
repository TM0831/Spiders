"""
Version: Python3.5
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/2/9 16:46
"""
import re
import requests


# 获取本机IP和地理位置
def get_ip():
    res = requests.get("http://www.ip.cn")
    result = re.findall("<p>您现在的 IP：<code>(.*?)</code></p><p>所在地理位置：<code>(.*?)</code>", res.text)
    ip, address = "", ""
    if len(result):
        ip = result[0][0]  # IP地址
        address = result[0][1].split(' ')[0]  # 地理位置
    else:
        print("Error!")
        exit()
    return ip, address
