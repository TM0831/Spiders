"""
Version: Python3.5
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/3/11 10:46
"""
import re
import queue
import requests
from lxml import etree


class CrawlQueue:
    def __init__(self):
        """
        初始化
        """
        self.q = queue.Queue()  # 爬取队列
        self.username = input("请输入您的博客名称：")
        self.q.put("http://www.cnblogs.com/" + self.username)
        self.urls = ["http://www.cnblogs.com/" + self.username]  # 记录爬取过的url
        self.result = []  # 储存阅读量数据

    def request(self, url):
        """
        发送请求和解析网页
        :param url: 链接
        :return:
        """
        res = requests.get(url)
        et = etree.HTML(res.text)
        lst = et.xpath('//*[@class="postDesc"]/text()')
        for i in lst:
            num = i.split(" ")[5].lstrip("阅读(").rstrip(")")
            self.result.append(int(num))

        # 下一页
        next_page = re.search('<a href="(.*?)">下一页</a>', res.text)
        if next_page:
            href = next_page.group().split('&nbsp;')[-1].replace('<a href="', '').replace('">下一页</a>', '')
            if href not in self.urls:  # 确保之前没有爬过
                self.q.put(href)
                self.urls.append(href)

    def get_url(self):
        """
        从爬取队列中取出url
        :return:
        """
        if not self.q.empty():
            url = self.q.get()
            self.request(url)

    def main(self):
        """
        主函数
        :return:
        """
        while not self.q.empty():
            self.get_url()


if __name__ == '__main__':
    crawl = CrawlQueue()
    crawl.main()
    print("您的博客总阅读量为：{}".format(sum(crawl.result)))
