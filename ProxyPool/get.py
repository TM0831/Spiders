"""
Version: Python3.5
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/2/14 12:19
"""
from ProxyPool.crawl import Crawler
from ProxyPool.pool import RedisClient


class GetProxy:
    def __init__(self):
        self.crawler = Crawler()
        self.redis = RedisClient()

    def get_proxy(self):
        """
        运行爬虫爬取代理
        :return:
        """
        print("[INFO]Crawl Start...")
        count = 0
        for callback_label in range(self.crawler.__CrawlFuncCount__):
            callback = self.crawler.__CrawlFunc__[callback_label]
            # 获取代理
            proxies = self.crawler.get_proxies(callback)
            for proxy in proxies:
                self.redis.add(proxy)
            count += len(proxies)
        print("此次爬取的代理数量为：{}".format(count))
        print("[INFO]Crawl End...\n\n")
