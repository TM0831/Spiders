"""
Version: Python3.7
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/8/16 13:50
"""
import re
import time
import random
import requests
from lxml import etree
from redis import Redis
from multiprocessing import Pool
from fake_useragent import UserAgent

ua = UserAgent(verify_ssl=False)
headers = {
    "Connection": "keep-alive",
    "Cookie": "Hm_lvt_73f7fa8431ee92c8d44d7fe9b72394af=1565961296,1565961531,1565963461,1566014119; Hm_lpvt_73f7fa8431ee92c8d44d7fe9b72394af=1566024386",
    "Host": "www.shu800.com",
    "Referer": "http://www.shu800.com/",
    "User-Agent": ua.random
}
page_urls = []  # 各类别页面URL


def get_homepage(url):
    """
    爬取shu800网站首页下的各分类URL
    :param url: 首页URL
    :return:
    """
    try:
        res = requests.get(url, headers=headers)
        res.encoding = "utf-8"
        et = etree.HTML(res.text)
        href_list = et.xpath('/html/body/div/div[1]/a/@href')
        for href in href_list:
            get_url("http://www.shu800.com" + href)
    except requests.exceptions:
        headers["User-Agent"] = ua.random
        get_homepage(url)


def get_url(url):
    """
    根据传入的分类URL，获取该类别的总页数及每一页的URL
    :param url: 分类URL
    :return:
    """
    try:
        page_urls.append(url)
        res = requests.get(url, headers=headers)
        res.encoding = "utf-8"
        end_href = re.findall('下一页</a><a href="(/.*?.html)">尾页</a>', res.text)[0]  # 获取最后一页的url
        end_list = end_href.rstrip(".html").split('_')
        end_num = int(end_list[1])  # 获取最大页数
        for i in range(2, end_num + 1):
            page_url = "http://www.shu800.com" + end_list[0] + "_" + str(i) + ".html"
            page_urls.append(page_url)
    except requests.exceptions:
        headers["User-Agent"] = ua.random
        get_url(url)


def get_page(url):
    """
    爬取每个页面下的美女图集的URL
    :param url: 页面URL
    :return:
    """
    try:
        r = Redis(host="localhost", port=6379, db=1)  # 连接Redis
        time.sleep(random.random())
        res = requests.get(url, headers=headers)
        res.encoding = "utf-8"
        et = etree.HTML(res.text)
        href_list = et.xpath('/html/body/div[5]/div[1]/div[1]/div[2]/ul/li/a/@href')
        for href in href_list:
            href = "http://www.shu800.com" + href
            r.sadd("href", href)  # 保存到数据库中
    except requests.exceptions:
        headers["User-Agent"] = ua.random
        get_page(url)


if __name__ == '__main__':
    print("Start crawling url...")
    get_homepage("http://www.shu800.com/")
    print("Url count", len(page_urls))
    print("Start crawling page...")
    pool = Pool()
    pool.map(get_page, page_urls)
    print("End crawling...")
    db = Redis(host="localhost", port=6379, db=1)  # 连接Redis
    count = len(list(db.smembers("href")))  # 计算URL总条数
    print("Href count: ", count)
