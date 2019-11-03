"""
Version: Python3.7
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/11/3 14:29
"""
import re
import logging
import pymongo
import requests
from lxml import etree
from multiprocessing import Pool
from fake_useragent import UserAgent


MONGO_HOST = "127.0.0.1"
MONGO_PORT = 27017
MONGO_DB = "Spiders"
MONGO_COL = "FJCourt"

logging.basicConfig(datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO, format="%(asctime)s : %(message)s")
