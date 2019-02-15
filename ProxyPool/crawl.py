"""
Version: Python3.5
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/2/12 15:07
"""
import requests
from lxml import etree
from fake_useragent import UserAgent


# 设置元类
class CrawlMetaClass(type):
    def __new__(cls, name, bases, attrs):
        attrs['__CrawlFuncCount__'] = 0
        attrs['__CrawlFunc__'] = []
        for k, v in attrs.items():
            if 'crawl_' in k:
                attrs['__CrawlFunc__'].append(k)
                attrs['__CrawlFuncCount__'] += 1
        # attrs['__CrawlFuncCount__'] = count
        return type.__new__(cls, name, bases, attrs)


class Crawler(object, metaclass=CrawlMetaClass):
    def __init__(self):
        self.proxies = []  # 代理列表
        ua = UserAgent()  # 使用随机UA
        self.headers = {
            "UserAgent": ua.random
        }

    def get_proxies(self, callback):
        """
        运行各个代理爬虫
        :param callback: crawl函数名称
        :return:
        """
        for proxy in eval("self.{}()".format(callback)):
            print("成功获取代理：", proxy)
            self.proxies.append(proxy)
        return self.proxies

    def crawl_kdd(self):
        """
        快代理爬虫
        :return:
        """
        urls = ["https://www.kuaidaili.com/free/inha/{}/".format(i) for i in range(1, 4)]
        for url in urls:
            res = requests.get(url, headers=self.headers)
            try:
                et = etree.HTML(res.text)
                ip_list = et.xpath('//*[@data-title="IP"]/text()')
                port_list = et.xpath('//*[@data-title="PORT"]/text()')
                for ip, port in zip(ip_list, port_list):
                    yield ip + ":" + port
            except Exception as e:
                print(e)

    def crawl_89ip(self):
        """
        89IP爬虫
        :return:
        """
        urls = ["http://www.89ip.cn/index_{}.html".format(i) for i in range(1, 4)]
        for url in urls:
            res = requests.get(url, headers=self.headers)
            try:
                et = etree.HTML(res.text)
                ip_list = et.xpath('//*[@class="layui-table"]/tbody/tr/td[1]/text()')
                port_list = et.xpath('//*[@class="layui-table"]/tbody/tr/td[2]/text()')
                ip_list = [i.strip() for i in ip_list]
                port_list = [i.strip() for i in port_list]
                for ip, port in zip(ip_list, port_list):
                    yield ip + ":" + port
            except Exception as e:
                print(e)

    def crawl_xc(self):
        """
        西刺代理爬虫
        :return:
        """
        url = "https://www.xicidaili.com/?t=253"
        res = requests.get(url, headers=self.headers)
        try:
            et = etree.HTML(res.text)
            ip_list = et.xpath('//*[@id="ip_list"]/tr[3]/td[2]/text()')
            port_list = et.xpath('//*[@id="ip_list"]/tr[3]/td[3]/text()')
            for ip, port in zip(ip_list, port_list):
                yield ip + ":" + port
        except Exception as e:
            print(e)
