"""
Version: Python3.7
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2020/5/27 20:30
"""
import os
import re
import uuid
import base64
import requests
from PIL import Image
from lxml import etree


class SpriteSpider:
    def __init__(self):
        self.headers = {
            "Cookie": "_ga=GA1.2.269529141.1590493054; _gid=GA1.2.235464343.1590493054; footprints=eyJpdiI6IjZwMnZGNW16"
                      "N0l6U0xYK2RTeHFVOUE9PSIsInZhbHVlIjoiT05HXC8yblVhTk5RaktsbnZMWGRFcVpFUyt2NnFNaHJpN1d1cUtsSUlwTkJq"
                      "REhJc1kzeFlCTlpVY1loMVRBbzQiLCJtYWMiOiJjYzUwOTA1M2VjZjI1MzdlYzg5ZjVhMzMxZjQwMWE5NDFmZjRhMzdkZWE3"
                      "YWUzNzIwYzJlMzg0MjJhNWIyMzdjIn0%3D; Hm_lvt_020fbaad6104bcddd1db12d6b78812f6=1590493054,159058163"
                      "4; remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d=eyJpdiI6IjJyMWw0RE5aS0FtWHhvUm16blh6MkE"
                      "9PSIsInZhbHVlIjoiXC94MEVlWDdUNEhFZ0RPWDY2R1JDMkxZcE1ZekdiNlJcLzFFUE5pV05xRDdIaDNTWDlUM1wvT09idDV"
                      "tbG5GeUxERkxnRmh5dzlMdXR4VUtwbkh2cU5MNTkxcXJwN2dVcnpaSFRPNHgyRDZrRGMrTFJPZGREb1kzZmZqenZVd1p3ZVV"
                      "vWlE4RkJldzk2YXNnVlhwaHk0N3QwYVJudlJnZUJJK0NGRzNBRllwSkFzPSIsIm1hYyI6IjA2MTU2OGQ5MTFiNjIzZDRkZWJ"
                      "kZjJmN2Y0NjMyZWEzZmRmMjQ4NDcwMzdhNmVlMzllNTQzNjdhMzdjZjYzNmUifQ%3D%3D; XSRF-TOKEN=eyJpdiI6Imp1dU"
                      "d4RlJcL1E0U09Ma0JIRWhjSjVRPT0iLCJ2YWx1ZSI6Ik5CU3FnS1wvVU1uS1wvbU92WUFvRHhuMmlxd3l4cGlNNmFcLzA0NT"
                      "dPXC9ZZFViNkRoQmM5czlCNUhYa1pmMVF0VmZoIiwibWFjIjoiYzFlYWEyZjNhNTg5YzE3ZTE2NTVjY2UwM2E1YTcyMjFkNm"
                      "ZhYWZmZGQ4MzgzYWMyZjZmZDFlMjU5NDRlM2FhYSJ9; glidedsky_session=eyJpdiI6Ijk5WlhmblhpdmR1YkU0NFNrT1"
                      "BycEE9PSIsInZhbHVlIjoibGFVNGh4RXI4M0hXNlJqeTltTjFwM3FNajBwOHhJc0pMRldneTFYXC9id3dBcWFMQ3lqTERHUX"
                      "JmUE5LRWlVTEciLCJtYWMiOiJlZTRiMGQwYTU1NDNiODJiNWY4ZTcyMTdlZTRjYWIxOGEzY2FlMjVjODY3OGZiYTAwMTExNj"
                      "hhMzE3ODU5YTcyIn0%3D; Hm_lpvt_020fbaad6104bcddd1db12d6b78812f6=1590581651",
            "UserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/83.0.4103.61 Safari/537.36"
        }

    def crawl(self, url):
        """
        crawl the page
        :param url: page url
        :return:
        """
        res = requests.get(url, headers=self.headers)
        img_data = re.findall("data:image/png;base64,(.+)?", res.text)
        img_data = img_data[0].replace('") }', '')
        width = self.save_img(img_data)
        nums = re.findall(r"background-position-x:-?(\d+)?px", res.text)
        nums = sorted([int(i) for i in list(set(nums))])
        self.get_digits(res.text, self.parse(nums, width / 10))

    @staticmethod
    def save_img(img_data):
        """
        save image in local directory
        :param img_data: image base64 data
        :return: width of image
        """
        img = base64.urlsafe_b64decode(img_data)
        filename = "{}.{}".format(uuid.uuid4(), "png")
        filepath = os.path.join("./Images", filename)
        with open(filepath, "wb") as f:
            f.write(img)
        image = Image.open(filepath)
        return image.width

    @staticmethod
    def parse(num_list: list, gap: int):
        """
        translate position to digit
        :param num_list: number list
        :param gap: average gap between numbers
        :return:
        """
        return {str(num): str(int(num // gap)) for num in num_list}

    @staticmethod
    def get_digits(html, pos_dict):
        """
        get digit according to the class and sum up the numbers
        :param html: html
        :param pos_dict: position to digit
        :return:
        """
        et = etree.HTML(html)
        pos_classes = et.xpath('//*[@id="app"]/main/div[1]/div/div/div/div/div/@class')
        digits, d = [], ""
        for pos in pos_classes:
            if len(d) == 3:
                digits.append(d)
                d = ""
            pos_x = re.findall(pos.split(" ")[0] + r" { background-position-x:-?(\d+?)px }", html)
            d = d + pos_dict[pos_x[0]]
        digits.append(d)
        result = sum([int(i) for i in digits])
        print("The result is : {}".format(result))


if __name__ == "__main__":
    spider = SpriteSpider()
    spider.crawl("http://www.glidedsky.com/level/web/crawler-sprite-image-1?page=1")
