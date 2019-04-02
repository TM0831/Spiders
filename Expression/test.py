"""
Version: Python3.7
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/4/2 12:06
"""
import time
import queue
import random
import requests
import threading
from lxml import etree
from fake_useragent import UserAgent

ua = UserAgent(verify_ssl=False)


class Producer(threading.Thread):
    def __init__(self, url_queue, img_queue):
        super(Producer, self).__init__()
        self.url_queue = url_queue
        self.img_queue = img_queue
        self.headers = {
            "Cookie": "td_cookie=306675591; __cfduid=ddc4d1a30bd24c96efdb74f90bd5cb0561554179214; _ga=GA1.2.2043100814.1554179212; _gid=GA1.2.586137198.1554179212; UM_distinctid=169dc4cc15e35f-0b77fc0e27baf-7a1437-144000-169dc4cc15f5b9; yjs_id=f565d35ce79377fe81c6f3b7912a0aae; ctrl_time=1; CNZZDATA1256911977=350124520-1554175596-http%253A%252F%252Fwww.doutula.com%252F%7C1554176880; XSRF-TOKEN=eyJpdiI6InMwVXhYeTQxNGNqUjd2bHZ5cFFZR1E9PSIsInZhbHVlIjoiME9aXC9oanJCOEU0NzZtdmlhcXVDNk11a0JKVWUrRE9CRkJcL1lna2p6eVp6RVwvSnA0Q05HaHM5cjBwcmszcmJXdiIsIm1hYyI6IjBhMGMwNmI3ODM3YjViM2RlZGZlZTcwNGIxZTMyYzI5NmFmMzFlZmFhZWY1MTg4ODQyNzY1NmZlZTY2ZWM1MzcifQ%3D%3D; doutula_session=eyJpdiI6IndBUnl4bTJua1R0emFcL2orcTF0RG9nPT0iLCJ2YWx1ZSI6Ild2T24xSXkzVk1LMnh4bDkyRUlXNDhxZVZWMXRhWXZZVU9zeklZWjhzSDFtMTNYNnMyVmpZZHhscUhkZDFjelwvIiwibWFjIjoiY2I3YzNlYWMwYTNiZmYzYWFiYWM5MDI4YzkyNWQzYmM1NGFhNmQ4MWY5MDk3ZDk4ZGMwNWE4ZTg2YjFhOWM0ZCJ9",
            "Referer": "http://www.doutula.com/",
            "User-Agent": ua.random
        }

    def run(self):
        """
        若队列不为空则获取url，若两个队列都为空则退出程序
        :return:
        """
        while True:
            if not self.url_queue.empty():
                url = self.url_queue.get()
                self.crawl(url)
            elif self.img_queue.empty():
                print("下载完成！正在退出程序...")
                time.sleep(5)
                exit()

    def crawl(self, url):
        """
        爬取和解析网页
        :param url: 网页url
        :return:
        """
        res1 = requests.get(url, headers=self.headers)
        et1 = etree.HTML(res1.text)
        href_list = et1.xpath('//*[@id="home"]/div/div[3]/a/@href')
        # print(href_list)
        for href in href_list:
            print("[INFO]Crawling ", href)
            res2 = requests.get(href, headers=self.headers)
            et2 = etree.HTML(res2.text)
            src_list = et2.xpath('//*[@class="artile_des"]/table/tbody/tr/td/a/img/@src')
            for n in range(len(src_list)):
                if src_list[n] == "":
                    src = et2.xpath('//*[@class="artile_des"][{}]/table/tbody/tr/td/a/img/@onerror'.format(n + 1))[0]
                    src = src.replace("this.src='", "").rstrip("''")
                    self.img_queue.put(src)
                else:
                    self.img_queue.put(src_list[n])


class Consumer(threading.Thread):
    def __init__(self, img_queue):
        super(Consumer, self).__init__()
        self.img_queue = img_queue
        self.headers = {
            "Referer": "http://www.doutula.com/",
            "User-Agent": ua.random
        }

    def run(self):
        """
        若队列不为空则获取url
        :return:
        """
        while True:
            if not self.img_queue.empty():
                url = self.img_queue.get()
                self.download(url)

    def download(self, url):
        """
        下载图片
        :param url: 图片url
        :return:
        """
        time.sleep(random.randint(1, 4))
        filename = url.split('/')[-1]
        print("[INFO]Downloading ", filename)
        with open("Images/" + filename, 'wb') as f:
            f.write(requests.get(url, headers=self.headers).content)


if __name__ == '__main__':
    urls, imgs = queue.Queue(), queue.Queue()

    # 将要爬取的url添加到队列中，这里的数字代表爬取页数
    for i in range(1, 5):
        urls.put('https://www.doutula.com/article/list/?page={}'.format(i))

    # 生产者线程
    for x in range(4):
        t = Producer(urls, imgs)
        t.start()

    # 消费者线程
    for x in range(4):
        t = Consumer(imgs)
        t.start()
