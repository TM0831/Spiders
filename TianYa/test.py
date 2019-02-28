"""
Version: Python3.5
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/2/27 14:23
"""
import re
import time
import requests
from fake_useragent import UserAgent

ua = UserAgent()
headers = {
    "Referer": "http://pp.tianya.cn/",
    "Cookie": "__auc=90d515c116922f9f856bd84dd81; Hm_lvt_80579b57bf1b16bdf88364b13221a8bd=1551070001,1551157745; user=w=EW2QER&id=138991748&f=1; right=web4=n&portal=n; td_cookie=1580546065; __cid=CN; Hm_lvt_bc5755e0609123f78d0e816bf7dee255=1551070006,1551157767,1551162198,1551322367; time=ct=1551322445.235; __asc=9f30fb65169320604c71e2febf6; Hm_lpvt_bc5755e0609123f78d0e816bf7dee255=1551322450; __u_a=v2.2.4; sso=r=349690738&sid=&wsid=71E671BF1DF0B635E4F3E3E41B56BE69; temp=k=674669694&s=&t=1551323217&b=b1eaa77438e37f7f08cbeffc109df957&ct=1551323217&et=1553915217; temp4=rm=ef4c48449946624e9d7d473bc99fc5af; u_tip=138991748=0",
    "UserAgent": ua.random
}


def crawl(url):
    res = requests.get(url, headers=headers)
    res.encoding = "utf-8"
    if res.status_code == 200:
        result = re.findall('<img.+src="(.*?)" alt="(.*?)".+>', res.text)
        for i in result:
            download(i[0], i[1])
    else:
        print("Error Request!")


def download(href, name):
    try:
        res = requests.get(href, headers=headers)
        with open('Images/{}.jpg'.format(name), 'wb') as f:
            f.write(res.content)
            print('[INFO]{}.jpg已下载！'.format(name))
    except:
        print("Error Download!")


if __name__ == '__main__':
    for num in range(1, 16):  # 最大页数15页
        time.sleep(1)
        t = int(time.time() * 1000)  # 获取13位时间戳
        page_url = "http://pp.tianya.cn/qt/list_{}.shtml?_={}".format(num, t)  # 构造链接
        crawl(page_url)
