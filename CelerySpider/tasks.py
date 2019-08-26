import requests
from lxml import etree
from celery import group
from CelerySpider.app import app


headers = {
    "Cookie": "__cfduid=d5d815918f19b7370d14f80fc93f1f27e1566719058; UM_distinctid=16cc7bba92f7b6-0aac860ea9b9a7-7373e61-144000-16cc7bba930727; CNZZDATA1256911977=1379501843-1566718872-https%253A%252F%252Fwww.baidu.com%252F%7C1566718872; XSRF-TOKEN=eyJpdiI6InJvNVdZM0krZ1wvXC9BQjg3YUk5aGM1Zz09IiwidmFsdWUiOiI5WkI4QU42a0VTQUxKU2ZZelVxK1dFdVFydlVxb3g0NVpicEdkSGtyN0Uya3VkXC9pUkhTd2plVUtUTE5FNWR1aCIsIm1hYyI6Ijg4NjViZTQzNGRhZDcxNTdhMDZlMWM5MzI4NmVkOGZhNmRlNTBlYWM0MzUyODIyOWQ4ZmFhOTUxYjBjMTRmNDMifQ%3D%3D; doutula_session=eyJpdiI6IjFoK25pTG50azEwOXlZbmpWZGtacnc9PSIsInZhbHVlIjoiVGY2MU5Ob2pocnJsNVBLZUNMTWw5OVpjT0J6REJmOGVpSkZwNFlUZVwvd0tsMnZsaiszWEpTbEdyZFZ6cW9UR1QiLCJtYWMiOiIxZGQzNTJlNzBmYWE0MmQzMzQ0YzUzYmYwYmMyOWY3YzkxZjJlZTllNDdiZTlkODA2YmQ3YWRjNGRmZDgzYzNmIn0%3D",
    "Referer": "https://www.doutula.com/article/list/?page=1",
    "UserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
}


@app.task(trail=True)
def main(urls):
    # 主函数
    return group(call.s(url) for url in urls)()


@app.task(trail=True)
def call(url):
    # 发送请求
    try:
        res = requests.get(url, headers=headers)
        parse.delay(res.text)
    except Exception as e:
        print(e)


@app.task(trail=True)
def parse(html):
    # 解析网页
    et = etree.HTML(html)
    href_list = et.xpath('//*[@id="home"]/div/div[2]/a/@href')
    result = []
    for href in href_list:
        href_res = requests.get(href, headers=headers)
        href_et = etree.HTML(href_res.text)
        src_list = href_et.xpath('//*[@class="artile_des"]/table/tbody/tr/td/a/img/@src')
        result.extend(src_list)
    return result
