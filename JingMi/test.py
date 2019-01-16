"""
Version: Python3.5
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/1/14 16:23
"""
import aiohttp
import asyncio
from lxml import etree
import pymongo
import pyecharts as pye

info_list = []
db = pymongo.MongoClient(host="127.0.0.1", port=27017)
col = db['Spider']['JingMi']


async def get(url):
    session = aiohttp.ClientSession()
    response = await session.get(url)
    text = await response.text()
    session.close()
    return text


async def parse(url):
    html = await get(url)
    s = etree.HTML(html)
    titles = s.xpath('/html/body/section/div[2]/div/article/header/h2/a/@title')
    urls = s.xpath('/html/body/section/div[2]/div/article/header/h2/a/@href')
    eyes = s.xpath('/html/body/section/div[2]/div/article/p/span[3]/text()')
    comments = s.xpath('/html/body/section/div[2]/div/article/p/span[4]/a/text()')
    likes = s.xpath('/html/body/section/div[2]/div/article/p/span[5]/a/span/text()')
    for title, url, eye, comment, like in zip(titles, urls, eyes, comments, likes):
        info = {
            "标题": title,
            "链接": url,
            "浏览数": eye.rstrip("浏览"),
            "评论数": comment.rstrip("评论"),
            "喜欢数": like
        }
        info_list.append(info)


def plot(title, name, index_list, value_list):
    index_list = index_list[::-1]
    value_list = value_list[::-1]
    bar = pye.Bar(title=title)
    bar.add("数量", index_list, value_list, is_convert=True, is_label_show=True, label_pos='right')
    bar.render("{}.html".format(name))


def analyze():
    data = [(i['标题'], i['浏览数'], i['评论数'], i['喜欢数']) for i in col.find()]
    list1 = sorted(data, key=lambda x: int(x[1]), reverse=True)
    list2 = sorted(data, key=lambda x: int(x[2]), reverse=True)
    list3 = sorted(data, key=lambda x: int(x[3]), reverse=True)
    plot("浏览数前十的文章", 'Eye', [i[0] for i in list1[:10]], [int(i[1]) for i in list1[:10]])
    plot("评论数前十的文章", 'Comment', [i[0] for i in list2[:10]], [int(i[2]) for i in list2[:10]])
    plot("喜欢数前十的文章", 'Like', [i[0] for i in list3[:10]], [int(i[3]) for i in list3[:10]])


def main():
    urls = ["https://cuiqingcai.com/page/{}".format(i) for i in (1, 36)]
    tasks = [asyncio.ensure_future(parse(url)) for url in urls]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
    col.insert(info_list)
    analyze()


if __name__ == '__main__':
    main()
