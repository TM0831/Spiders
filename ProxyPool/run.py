"""
Version: Python3.5
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/2/14 14:26
"""
from ProxyPool.pool import RedisClient
from ProxyPool.get import GetProxy
from ProxyPool.test import TestProxy


class Main:
    def __init__(self):
        self.gp = GetProxy()
        self.tp = TestProxy()
        self.db = RedisClient()

    def run(self):
        """
        运行的主函数，先爬取代理，然后测试，最后获取一个有效代理
        :return:
        """
        self.gp.get_proxy()
        self.tp.test()
        proxy = self.db.random()
        proxy = proxy.decode('utf-8')
        print("从代理池中取出的代理为：{}".format(proxy))


if __name__ == '__main__':
    m = Main()
    m.run()
