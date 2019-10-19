"""
Version: Python3.7
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/10/19 13:08
"""
import re
import time
import jieba
import logging
import pymongo
import requests
import threading
from queue import Queue
from collections import Counter
from wordcloud import WordCloud
from Bilibili.get_ua import get_random_ua


MONGO_HOST = "127.0.0.1"
MONGO_PORT = 27017
MONGO_DB = "Spiders"
MONGO_COL = "bilibili"

logging.basicConfig(filename="run.log", datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(module)s: %(message)s")
