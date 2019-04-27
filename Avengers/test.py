"""
Version: Python3.7
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/4/25 15:28
"""
import time
import jieba
import random
import pymongo
import requests
import numpy as np
from PIL import Image
from lxml import etree
from snownlp import SnowNLP
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from fake_useragent import UserAgent


class AvengersSpider:
    """
    复仇者联盟4爬虫：爬取短评并进行解析，最终进行情感分析和生成词云
    """

    def __init__(self, username, password):
        self.username = username
        self.password = password
        ua = UserAgent()
        self.headers = {
            "Accept": "application/json",
            "onnection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "accounts.douban.com",
            "Origin": "https://accounts.douban.com",
            "Referer": "https://accounts.douban.com/passport/login?",
            "User-Agent": ua.random,
            "X-Requested-With": "XMLHttpRequest"
        }
        self.session = requests.Session()
        client = pymongo.MongoClient(host="127.0.0.1", port=27017)
        self.col = client["Spiders"]["Avengers"]

    def login(self):
        """
        模拟登录
        :return:
        """
        url = "https://accounts.douban.com/j/mobile/login/basic"
        data = {
            "ck": "",
            "name": self.username,
            "password": self.password,
            "remember": "false",
            "ticket": ""
        }
        res = self.session.post(url, headers=self.headers, data=data)
        print("登录成功！欢迎用户：", res.json()["payload"]["account_info"]["name"])

    def crawl(self, url):
        """
        爬取并保存数据
        :param url:
        :return:
        """
        time.sleep(random.randint(1, 4))
        res = self.session.get(url)
        et = etree.HTML(res.text)
        users = et.xpath('//*[@id="comments"]/div/div[2]/h3/span[2]/a/text()')
        comments = et.xpath('//*[@id="comments"]/div/div[2]/p/span/text()')
        stars = et.xpath('//*[@id="comments"]/div/div[2]/h3/span[2]/span[2]/@class')
        the_times = et.xpath('//*[@id="comments"]/div/div[2]/h3/span[2]/span[3]/text()')
        data_list = []
        for user, comment, star, the_time in zip(users, comments, stars, the_times):
            data = {
                "昵称": user,
                "评论": comment.strip(),
                "评分": star.strip().replace("allstar", "").rstrip("0 rating") + "星",
                "时间": the_time.strip()
            }
            data_list.append(data)
            print(data)
        self.col.insert_many(data_list)

    def analyze(self):
        """
        情感分析
        :return:
        """
        result = self.col.find()
        comments = []
        for i in result:
            comments.append(i["评论"])
        sentiments_list = []
        for i in comments:
            s = SnowNLP(i)
            sentiments_list.append(s.sentiments)
        plt.hist(sentiments_list, bins=np.arange(0, 1, 0.01), facecolor="g")
        plt.xlabel('Sentiments Probability')
        plt.ylabel('Quantity')
        plt.title('Analysis of Sentiments')
        plt.savefig("Sentiments.png")
        print("情感分析完毕，生成图片Sentiments.png")

    def generate(self):
        """
        生成词云
        :return:
        """
        result = self.col.find()
        comments = []
        for i in result:
            comments.append(i["评论"])
        text = jieba.cut("\n".join(comments))

        # 文本清洗，去除标点符号和长度为1的词
        with open("stopwords.txt", "r", encoding='utf-8') as f:
            stopwords = set(f.read().split("\n"))
        stopwords.update({"一部", "一场", "电影", "小时", "分钟"})
        # 使用图片
        mask = np.array(Image.open("Avengers.jpg"))

        # 生成词云
        wc = WordCloud(
            mask=mask,
            stopwords=stopwords,
            font_path="font.ttf",
            max_font_size=200,
            min_font_size=20,
            max_words=100,
            width=1200,
            height=800
        )
        wc.generate(' '.join(text))
        wc.to_file('Avengers.png')
        print("词云已生成，保存为Avengers.png。")

    def main(self):
        """
        主函数，先登录，然后爬取评论，最后解析评论生成词云
        :return:
        """
        self.login()
        print("开始爬取评论，请稍等...")
        url1 = ["https://movie.douban.com/subject/26100958/comments?start={}&limit=20&sort=new_score&status=P&"
                "percent_type=h".format(i * 20) for i in range(25)]  # 好评
        url2 = ["https://movie.douban.com/subject/26100958/comments?start={}&limit=20&sort=new_score&status=P&"
                "percent_type=m".format(i * 20) for i in range(25)]  # 一般
        url3 = ["https://movie.douban.com/subject/26100958/comments?start={}&limit=20&sort=new_score&status=P&"
                "percent_type=l".format(i * 20) for i in range(25)]  # 差评
        url4 = ["https://movie.douban.com/subject/26100958/comments?start={}&limit=20&sort=time&"
                "status=P".format(i * 20) for i in range(5)]  # 最新
        all_url = url1 + url2 + url3 + url4
        for i in all_url:
            self.crawl(i)
            # print("Crawling url: ", i)
        print("爬取完毕，正在进行情感分析...")
        self.analyze()
        print("分析完毕，正在解析生成词云...")
        self.generate()


if __name__ == '__main__':
	usr = ""  # 用户名
	pwd = ""  # 密码
    spider = AvengersSpider(usr, pwd)
    spider.main()
