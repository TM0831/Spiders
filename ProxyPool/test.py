"""
Version: Python3.5
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/2/14 14:24
"""
import time
import random
import requests
from fake_useragent import UserAgent
from ProxyPool.crawl import Crawler
from ProxyPool.pool import RedisClient


class TestProxy:
    def __init__(self):
        self.crawler = Crawler()
        self.redis = RedisClient()
        ua = UserAgent()  # 使用随机UA
        self.headers = {
            "UserAgent": ua.random
        }

    def test(self):
        """
        测试函数，测试代理池中的代理
        :return:
        """
        proxy_list = self.redis.all()
        proxy_list = [i.decode('utf-8') for i in proxy_list]  # 字节型转字符串型

        print("[INFO]Test Start...")
        for proxy in proxy_list:
            self.request(proxy)
        print("[INFO]Test End...\n\n")

    def request(self, proxy):
        """
        测试请求函数
        :param proxy:
        :return:
        """
        print("当前测试代理：{}   该代理分数为：{}".format(proxy, self.redis.db.zscore(self.redis.key, proxy)))
        time.sleep(random.randint(1, 4))
        try:
            url = "https://www.baidu.com/"
            proxies = {
                "https": "https://" + proxy
            }
            res = requests.get(url, headers=self.headers, proxies=proxies, timeout=5)

            if res.status_code == 200:
                print("代理可用，分数设置为100")
                self.redis.max(proxy)
            else:
                print("错误的请求状态码，分数减1")
                self.redis.decrease(proxy)
        except:
            print("代理请求失败，分数减1")
            self.redis.decrease(proxy)

