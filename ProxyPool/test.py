"""
Version: Python3.5
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/2/14 14:24
"""
import time
import random
import aiohttp
import asyncio
from ProxyPool.crawl import Crawler
from ProxyPool.pool import RedisClient


async def request(session, proxy):
    url = "https://www.baidu.com/"
    proxies = "http://" + proxy
    async with session.get(url, proxy=proxies, timeout=10, allow_redirects=False) as response:
        return response.status_code == 200


class TestProxy:
    def __init__(self):
        self.crawler = Crawler()
        self.redis = RedisClient()
        self.proxy_list = []

    async def test(self, proxy):
        """
        测试函数，测试代理的可用性
        :return:
        """
        try:
            conn = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=conn) as session:
                print("当前测试代理：{}   该代理分数为：{}".format(proxy, self.redis.db.zscore(self.redis.key, proxy)))
                time.sleep(random.randint(1, 3))
                code = await request(session, proxy)
                if code:
                    print("代理{}可用，分数设置为100".format(proxy))
                    self.redis.max(proxy)
                else:
                    print("代理{}错误的请求状态码，分数减1".format(proxy))
                    self.redis.decrease(proxy)
        except:
            print("代理{}请求失败，分数减1".format(proxy))
            self.redis.decrease(proxy)

    def main(self):
        """
        测试代理的主函数
        :return:
        """
        proxy_list = self.redis.all()
        self.proxy_list = [i.decode('utf-8') for i in proxy_list]  # 字节型转字符串型
        tasks = [asyncio.ensure_future(self.test(proxy)) for proxy in self.proxy_list]
        print("[INFO]Test Start...")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))
        print("[INFO]Test End...\n\n")
