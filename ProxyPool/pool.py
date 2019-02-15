"""
Version: Python3.5
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/2/12 14:54
"""
import redis
import random

MAX_SCORE = 100  # 最高分
MIN_SCORE = 0  # 最低分
INITIAL_SCORE = 10  # 初始分数
REDIS_HOST = "localhost"
REDIS_PORT = 6379


class RedisClient:
    def __init__(self):
        self.db = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        self.key = "proxies"

    def add(self, proxy, score=INITIAL_SCORE):
        """
        将代理添加到代理池中
        :param proxy: 代理
        :param score: 分数
        :return:
        """
        if not self.is_exist(proxy):
            self.db.zadd(self.key, proxy, score)

    def is_exist(self, proxy):
        """
        判断代理池中是否存在该代理
        :param proxy: 代理
        :return: True or False
        """
        if self.db.zscore(self.key, proxy):
            return True
        else:
            return False

    def random(self):
        """
        获取有效代理，先获取最高分代理，如果不存在，则按分数排名然后随机获取
        :return: 代理
        """
        result = self.db.zrangebyscore(self.key, MAX_SCORE, MAX_SCORE)
        if len(result):
            return random.choice(result)
        else:
            result = self.db.zrangebyscore(self.key, MIN_SCORE, MAX_SCORE)
            if len(result):
                return random.choice(result)
            else:
                print("代理池已空！")

    def decrease(self, proxy):
        """
        代理分数减1分，若小于最低分，则从代理池中移除
        :param proxy:
        :return:
        """
        if self.is_exist(proxy):
            score = self.db.zscore(self.key, proxy)
            if score > MIN_SCORE:
                score -= 1
                self.db.zadd(self.key, proxy, score)
            else:
                self.delete(proxy)

    def max(self, proxy):
        """
        将代理分数设置为最高分
        :param proxy: 代理
        :return:
        """
        if self.is_exist(proxy):
            self.db.zadd(self.key, proxy, MAX_SCORE)

    def delete(self, proxy):
        """
        从代理池中移除该代理
        :param proxy: 代理
        :return:
        """
        if self.is_exist(proxy):
            self.db.zrem(self.key, proxy)

    def all(self):
        """
        获取代理池中的所有代理
        :return:
        """
        if self.count():
            return self.db.zrange(self.key, MIN_SCORE, MAX_SCORE)

    def count(self):
        """
        获取代理池中代理数量
        :return:
        """
        return self.db.zcard(self.key)
