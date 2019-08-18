"""
Version: Python3.7
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/8/16 14:03
"""
import re
import time
import random
import requests
from lxml import etree
from redis import Redis
from fake_useragent import UserAgent

ua = UserAgent(verify_ssl=False)
headers = {
    "Connection": "keep-alive",
    "Cookie": "Hm_lvt_73f7fa8431ee92c8d44d7fe9b72394af=1565961296,1565961531,1565963461,1566014119; Hm_lpvt_73f7fa8431ee92c8d44d7fe9b72394af=1566024386",
    "Host": "www.shu800.com",
    "Referer": "http://www.shu800.com/",
    "User-Agent": ua.random
}
r = Redis(host="192.168.229.130", port=6379, db=1)
x = 1


def get_urls():
    """
    监听Redis中是否有URL，如果没有就一直运行，如果有就提取出来进行爬取
    :return:
    """
    if b"href" in r.keys():
        while True:
            try:
                url = r.spop("href")
                url = url.decode("utf-8")  # unicode转str
                print("Crawling URL: ", url)
                get_image(url)
                get_img_page(url)
            except:
                if b"href" not in r.keys():  # 爬取结束，退出程序
                    break
                else:
                    continue
    else:
        time.sleep(5)
        get_urls()


def get_img_page(url):
    """
    根据传入的图集URL，获取该图集的总页数及每一页的URL
    :param url: 图集URL
    :return:
    """
    try:
        time.sleep(random.random())
        res = requests.get(url, headers=headers)
        res.encoding = "utf-8"
        end_href = re.findall('下一页</a><a href="(/.*?.html)">尾页</a>', res.text)[0]  # 获取最后一页的url
        end_list = end_href.rstrip(".html").split('_')
        end_num = int(end_list[1])  # 获取最大页数
        for i in range(2, end_num + 1):
            page_url = "http://www.shu800.com" + end_list[0] + "_" + str(i) + ".html"
            get_image(page_url)
    except requests.exceptions:
        headers["User-Agent"] = ua.random
        get_img_page(url)


def get_image(url):
    """
    爬取图片展示页面，获取图片名称和链接进行下载
    :param url: 图片展示页URL
    :return:
    """
    global x
    if x < 10:
        x += 1
    else:
        x = 1
        time.sleep(random.randint(2, 5))

    res = requests.get(url, headers=headers)
    res.encoding = "utf-8"
    et = etree.HTML(res.text)
    try:
        img_name = et.xpath('/html/body/div[5]/div[1]/div[1]/div[2]/div[4]/span/p/img/@alt')  # 图片名称
        img_url = et.xpath('/html/body/div[5]/div[1]/div[1]/div[2]/div[4]/span/p/img/@src')  # 图片链接
        if img_url:
            img_name, img_url = img_name[0], img_url[0]
            if "_" not in url:
                img_name += "-1"
            else:
                num = url.rstrip(".html").split("_")[1]
                img_name = img_name + "-" + num
            # print(img_name)
            with open("Images/" + img_name + ".jpg", "wb") as f:  # 下载图片
                f.write(requests.get(img_url).content)
        else:
            pass
    except:
        pass


if __name__ == '__main__':
    get_urls()
