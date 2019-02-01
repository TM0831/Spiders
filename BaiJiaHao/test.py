"""
Version: Python3.5
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/1/31 14:08
"""
import re
import time
import requests
import numpy as np
import matplotlib.pyplot as plt
from lxml import etree
from multiprocessing import Pool
from fake_useragent import UserAgent


class BaiJiaHao:
    def __init__(self):
        url1 = "http://top.baidu.com/buzz?b=341&c=513&fr=topbuzz_b11_c513"  # 今日热点
        url2 = "http://top.baidu.com/buzz?b=344&c=513&fr=topbuzz_b341_c513"  # 娱乐热点
        url3 = "http://top.baidu.com/buzz?b=11&c=513&fr=topbuzz_b344_c513"  # 体育热点
        self.urls = [url1, url2, url3]  # 热点链接
        ua = UserAgent()
        self.headers = {
            "User-Agent": ua.random  # 随机UA
        }
        self.url_list = []  # 各热点下的事件链接
        self.filename = 'result_urls.txt'  # 用于储存解析得到的链接
        fig, self.ax = plt.subplots()  # 绘图

    def get_list(self, url):
        # 获取各个事件列表，每个列表有50条
        res = requests.get(url=url, headers=self.headers)
        et = etree.HTML(res.text)
        for i in range(2, 52):
            href = et.xpath('//*[@id="main"]/div[2]/div/table/tr[{}]/td[2]/a[1]/@href'.format(i))
            if len(href):
                self.url_list.append(href[0])

    def get_page(self, url):
        # 获取第一页内容
        print("[INFO] Crawling url {}...".format(self.url_list.index(url)))
        res = requests.get(url, headers=self.headers)
        time.sleep(5)
        et = etree.HTML(res.text)
        try:
            for i in range(1, 11):
                href = et.xpath('//*[@id="{}"]/h3/a/@href'.format(i))[0]
                if href.startswith('http'):
                    self.get_real_url(href)
        except Exception as e:
            print(e)

    def get_real_url(self, fake_url):
        # 获取真实的链接
        try:
            res = requests.get(fake_url, headers=self.headers)
            time.sleep(1)
            real_url = res.url
            if real_url != fake_url:
                with open(self.filename, 'a', encoding='utf-8') as f:
                    f.write(real_url + '\n')
        except Exception as e:
            print(e)

    def analyze(self):
        # 对结果进行简单分析
        with open(self.filename, 'r', encoding='utf-8') as f:  # 读取数据
            txt = f.readlines()
        txt = [i.strip() for i in txt]
        result = []
        for i in txt:
            match = re.match("(http[s]?://.+?[com,cn,net]/)", i)  # 正则匹配
            if match:
                result.append(match.group())
        dic = {k: result.count(k) for k in result}  # 列表解析
        lst = sorted(dic.items(), key=lambda x: x[1])  # 字典解析
        lst = lst[-10:]  # 取前十项
        for i in lst[::-1]:
            print(i[0],i[1])
        href_list, num_list = [], []
        for i in lst:
            href = i[0]
            href = href.replace('cn', 'com').replace('net', 'com')
            href = href[href.index(':') + 3:].rstrip('.com/')

            href_list.append(href)
            num_list.append(int(i[1] / len(result) * 100))
        self.plot(href_list, num_list)

    def plot(self, index_list, value_list):
        b = self.ax.barh(range(len(index_list)), value_list, color='blue', height=0.8)
        # 添加数据标签
        for rect in b:
            w = rect.get_width()
            self.ax.text(w, rect.get_y() + rect.get_height() / 2, '{}%'.format(w),
                         ha='left', va='center')
        # 设置Y轴刻度线标签
        self.ax.set_yticks(range(len(index_list)))
        self.ax.set_yticklabels(index_list)
        # 设置X轴刻度线
        lst = ["{}%".format(i) for i in range(0, 20, 2)]
        self.ax.set_xticklabels(lst)

        plt.subplots_adjust(left=0.25)
        plt.xlabel("占比")
        plt.ylabel("网站")
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.savefig("bjh.jpg")
        print("已保存为bjh.jpg！")

    def main(self):
        for url in self.urls:
            self.get_list(url)
        # 使用进程池
        self.url_list = list(set(self.url_list))  # 去重
        print("Url counts : {}".format(len(self.url_list)))
        pool = Pool(processes=4)
        pool.map(self.get_page, self.url_list)
        self.analyze()


if __name__ == '__main__':
    bjh = BaiJiaHao()
    bjh.main()
