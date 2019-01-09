"""
Version: Python3.5
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2018/12/27 14:49
"""
import re
import time
import requests
from lxml import etree
from fake_useragent import UserAgent


class DianPing:
    def __init__(self):
        self.url = "http://www.dianping.com/wuhan/ch10"
        self.ua = UserAgent()
        self.headers = {
            "Cookie": "s_ViewType=10; _lxsdk_cuid=167ca93f5c2c8-0c73da94a9dd08-68151275-1fa400-167ca93f5c2c8; _lxsdk=167ca93f5c2c8-0c73da94a9dd08-68151275-1fa400-167ca93f5c2c8; _hc.v=232064fb-c9a6-d4e0-cc6b-d6303e5eed9b.1545291954; cy=16; cye=wuhan; td_cookie=686763714; _lxsdk_s=%7C%7CNaN",
            "User-Agent": self.ua.random  # 获取随机的User-Agent
        }
        self.dic = {}  # class-digit字典

    def get_page(self):
        res = requests.get(self.url, headers=self.headers)
        s = etree.HTML(res.text)
        title_list = s.xpath('//*[@id="shop-all-list"]/ul/li/div[2]/div[1]/a[1]/@title')  # 标题
        dish_list = []  # 招牌菜
        if len(title_list):
            self.get_dict(res.text)
            for i in range(len(title_list)):
                dish_list.append(s.xpath('//*[@id="shop-all-list"]/ul/li[{}]/div[2]/div[4]/a/text()'.format(i + 1))[0])
            score1_list = self.get_score(res.text, len(title_list), 1)  # 口味评分
            score2_list = self.get_score(res.text, len(title_list), 2)  # 环境评分
            score3_list = self.get_score(res.text, len(title_list), 3)  # 服务评分
            for i in range(len(title_list)):
                info = {
                    "店名": title_list[i],
                    "口味评分": score1_list[i],
                    "环境评分": score2_list[i],
                    "服务评分": score3_list[i],
                    "招牌菜": dish_list[i]
                }
                print(info)
        else:
            print("Error！")

    def get_dict(self, html):
        # 提取css文件的url
        css_url = "http:" + re.search('(//.+svgtextcss.+\.css)', html).group()
        css_res = requests.get(css_url)
        # 这一步得到的列表内容为css中class的名字及其对应的偏移量
        css_list = re.findall('(un\w+){background:(.+)px (.+)px;', '\n'.join(css_res.text.split('}')))
        # 过滤掉匹配错误的内容，并对y方向上的偏移量初步处理
        css_list = [[i[0], i[1], abs(float(i[2]))] for i in css_list if len(i[0]) == 5]
        # y_list表示在y方向上的偏移量，完成排序和去重
        y_list = [i[2] for i in css_list]
        y_list = sorted(list(set(y_list)))
        # 生成一个字典
        y_dict = {y_list[i]: i for i in range(len(y_list))}
        # 提取svg图片的url
        svg_url = "http:" + re.findall('class\^="un".+(//.+svgtextcss.+\.svg)', '\n'.join(css_res.text.split('}')))[0]
        svg_res = requests.get(svg_url)
        # 得到svg图片中的所有数字
        digits_list = re.findall('>(\d+)<', svg_res.text)
        for i in css_list:
            # index表示x方向上的索引(最小的索引值是0)
            index = int((float(i[1]) + 7) / -12)
            self.dic[i[0]] = digits_list[y_dict[i[2]]][index]

    def get_score(self, html, l, x):
        """
        :param html: 网页源码
        :param l: 迭代长度
        :param x: 1或2或3
        :return: 评分列表
        """
        s = etree.HTML(html)
        num_list = []
        for i in range(l):
            t = s.xpath('//*[@id="shop-all-list"]/ul/li[{}]/div[2]/span/span[{}]/b/text()'.format(i + 1, x))[0]
            c = s.xpath('//*[@id="shop-all-list"]/ul/li[{}]/div[2]/span/span[{}]/b/span/@class'.format(i + 1, x))
            num = self.dic[c[0]] + '.' + self.dic[c[1]] if t == '.' else self.dic[c[0]] + '.1'
            num_list.append(num)
        return num_list


if __name__ == '__main__':
    dp = DianPing()
    dp.get_page()