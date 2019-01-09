"""
Version: Python3.5
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/1/6 13:57
"""
import re
import time
import json
import socket
import pymongo
import logging
import requests
import threading

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DouYu:
    def __init__(self, room_id):
        self.room_id = room_id
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostbyname("openbarrage.douyutv.com")
        port = 8601
        self.client.connect((host, port))
        self.gift_dict = {}
        db = pymongo.MongoClient(host="127.0.0.1", port=27017)
        self.col = db['Spider']['DouYu-{}'.format(room_id)]

    def get_gift_dict(self):
        # 获取礼物信息
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/68.0.3440.75 Safari/537.36"
        }
        url1 = "https://webconf.douyucdn.cn/resource/common/gift/flash/gift_effect.json"
        res1 = requests.get(url1, headers=headers)
        js1 = json.loads(res1.text.lstrip('DYConfigCallback(').rstrip(');'))
        gift_data1 = js1['data']['flashConfig']
        for i in gift_data1.keys():
            self.gift_dict[gift_data1[i]['id']] = gift_data1[i]['name']

        url2 = "https://webconf.douyucdn.cn/resource/common/prop_gift_list/prop_gift_config.json"
        res2 = requests.get(url2, headers=headers)
        js2 = json.loads(res2.text.lstrip('DYConfigCallback(').rstrip(');'))
        gift_data2 = js2['data']
        for i in gift_data2.keys():
            self.gift_dict[int(i)] = gift_data2[i]['name']
        # print(self.gift_dict)
        logging.info("Succeed in getting gifts.")

    def send_msg(self, msg):
        # 发送数据
        msg = msg + '\0'  # 数据以'\0'结尾
        msg = msg.encode('utf-8')  # 使用utf-8编码
        length = len(msg) + 8  # 消息长度
        code = 689  # 消息类型
        # 消息头部：消息长度+消息长度+消息类型+加密字段(默认为0)+保留字段(默认为0)
        head = int.to_bytes(length, 4, 'little') + int.to_bytes(length, 4, 'little') + int.to_bytes(code, 4, 'little')
        # 发送头部部分
        self.client.send(head)
        # 发送数据部分
        sent = 0
        while sent < len(msg):
            n = self.client.send(msg[sent:])  # 返回已发送的数据长度
            sent = sent + n

    def login(self):
        # 登录授权
        login_msg = "type@=loginreq/roomid@={}/".format(self.room_id)
        self.send_msg(login_msg)
        # 加入房间
        join_msg = "type@=joingroup/rid@={}/gid@=-9999/".format(self.room_id)
        self.send_msg(join_msg)
        logging.info("Succeed in logging in.")

    def get(self):
        # 获取弹幕和礼物信息
        while True:
            try:
                data = self.client.recv(2048)
                data = data[12:].decode('utf-8', 'ignore')
                # 弹幕
                if re.search('type@=chatmsg', data):
                    pattern1 = re.compile('uid@=(.+?)/nn@=(.+?)/txt@=(.+?)/cid@=(.+?)/')
                    chat = re.findall(pattern1, data)[0]
                    # print(chat)
                    chat_data = {
                        "data_type": "chat",
                        "chat_id": chat[3],
                        "chat_txt": chat[2],
                        "user_id": chat[0],
                        "user_name": chat[1]
                    }
                    self.col.insert(chat_data)
                # 礼物
                if re.search('type@=dgb', data):
                    pattern2 = re.compile('gfid@=(.+?)/.+?/uid@=(.+?)/nn@=(.+?)/')
                    gift = re.findall(pattern2, data)[0]
                    # print(gift)
                    gift_data = {
                        "data_type": "gift",
                        "gift_id": gift[0],
                        "gift_name": self.gift_dict[int(gift[0])],
                        "user_id": gift[1],
                        "user_name": gift[2]
                    }
                    logging.info("{}送出了:{}".format(gift[2], self.gift_dict[int(gift[0])]))
                    self.col.insert(gift_data)
                time.sleep(0.05)
            except KeyError:
                pass
            except Exception as e:
                logging.info(e)

    def keep_live(self):
        # 用于维持和后台间的心跳
        while True:
            # keep_msg = "type@=keeplive/tick@={}".format(get_time())  # 旧版心跳消息
            keep_msg = "mrkl/"  # 新版心跳消息
            self.send_msg(keep_msg)
            time.sleep(40)
            logging.info("Keep live...")

    def main(self):
        self.get_gift_dict()
        self.login()
        t = threading.Thread(target=self.keep_live)
        t.setDaemon(True)  # 设置守护线程
        t.start()
        while True:
            t1 = threading.Thread(target=self.get)
            t1.start()
            t1.join()


if __name__ == '__main__':
    dy = DouYu(6039226)
    dy.main()
