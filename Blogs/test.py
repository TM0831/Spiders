"""
Version: Python3.5
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/1/23 13:03
"""
import urllib
import pymysql
from time import sleep
from lxml import etree
import matplotlib.pyplot as plt
from multiprocessing import Pool

# 连接MySQL数据库
db = pymysql.connect(host="localhost", port=3306, user="root", password="123456", db="spider")
cursor = db.cursor()


def parse(data):
    url = "https://www.cnblogs.com/mvc/AggSite/PostList.aspx"
    # 发送请求
    data = bytes(urllib.parse.urlencode(data), encoding="utf-8")
    res = urllib.request.urlopen(url, data=data)
    html = res.read().decode('utf-8')
    sleep(2)

    # 解析网页
    et = etree.HTML(html)
    title_list = et.xpath('//*[@class="post_item_body"]/h3/a/text()')  # 标题
    author_list = et.xpath('//*[@class="post_item_foot"]/a/text()')  # 作者
    time_list = et.xpath('//*[@class="post_item_foot"]/text()')  # 发布时间
    read_list = et.xpath('//*[@class="post_item_foot"]/span[2]/a/text()')  # 阅读数
    comment_list = et.xpath('//*[@class="post_item_foot"]/span[1]/a/text()')  # 评论数

    # 处理数据
    time_list = [i.strip().lstrip('发布于 ') for i in time_list if i.strip() != '']
    comment_list = [int(i.strip().strip('评论(').rstrip(')')) for i in comment_list]
    read_list = [int(i.strip().strip('阅读(').rstrip(')')) for i in read_list]

    for title, author, time, read, comment in zip(title_list, author_list, time_list, read_list, comment_list):
        save((title, author, time, read, comment))


def create_table():
    # 创建表
    sql = """
        create table if not exists blogs(
        title varchar(100) not null,
        author varchar(30) not null,
        rtime varchar(30) not null,
        readnum int(6) not null,
        commentnum int(6) not null);
    """
    cursor.execute(sql)


def save(data):
    # 把数据保存到MySQL数据库中
    sql = "insert into blogs(title, author, rtime, readnum, commentnum) values (%s,%s,%s,%s,%s)"
    try:
        cursor.execute(sql, data)
        db.commit()
    except:
        db.rollback()


def plot(dic, k, name):
    index = list(dic.keys())
    value = list(dic.values())
    # 绘制柱状图
    plt.bar(range(len(value)), value, tick_label=index, color="green", width=0.8)
    # 显示具体数值
    for x, y in zip(index, value):
        if y:
            plt.text(x, y + k, "%d" % y, ha="center", va="top")
    plt.xlabel("时间")
    plt.ylabel("{}".format(name))
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.savefig('{}.jpg'.format(name))


def analyze():
    sql = "select rtime,readnum from blogs"
    cursor.execute(sql)
    # 查询结果
    all_data = cursor.fetchall()
    # 每一个数字代表一个小时，比如0就代表0:00-0:59
    dic1 = {
        0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0,
        13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0,
    }
    dic2 = {
        0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0,
        13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0,
    }
    # 查看2018年12月的数据
    day_list = ["2018-12-{}".format(str(i).zfill(2)) for i in range(1, 32)]
    for day in day_list:
        results = [i for i in all_data if day in i[0]]
        for result in results:
            t = int(result[0].split(' ')[1].split(':')[0])
            dic1[t] += 1
            dic2[t] += result[1]
    plot(dic1, 10, '博客篇数')
    plot(dic2, 5000, '阅读数')


if __name__ == '__main__':
    create_table()
    params = {
        "CategoryId": 808,
        "CategoryType": "SiteHome",
        "ItemListActionName": "PostList",
        "PageIndex": 0,
        "ParentCategoryId": 0,
        "TotalPostCount": 4000
    }
    data_list = []  # data参数列表
    for n in range(1, 201):
        params["PageIndex"] = n
        data_list.append(params.copy())
    pool = Pool(processes=4)  # 进程池
    pool.map(parse, data_list)
    pool.close()
    db.close()
    analyze()
