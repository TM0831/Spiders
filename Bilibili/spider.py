"""
Version: Python3.7
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/10/3 10:49
"""
from Bilibili.config import *


class CrawlThread(threading.Thread):
    def __init__(self, url: str, name: str, data_queue: Queue):
        """
        initial function
        :param url: room url
        :param name: thread name
        :param data_queue: data queue
        """
        super(CrawlThread, self).__init__()
        self.room_url = url
        self.room_id = re.findall(r"/(\d+)\?", url)[0]
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://live.bilibili.com",
            "Referer": "",
            "Sec-Fetch-Mode": "cors",
            "UserAgent": get_random_ua()
        }
        self.name = name
        self.data_queue = data_queue

    def run(self):
        """
        send request and receive response
        :return:
        """
        while 1:
            try:
                time.sleep(1)
                msg_url = "https://api.live.bilibili.com/ajax/msg"
                # set referer
                self.headers["Referer"] = self.room_url
                # set data
                data = {
                    "roomid": self.room_id,
                    "csrf_token": "e7433feb8e629e50c8c316aa52e78cb2",
                    "csrf": "e7433feb8e629e50c8c316aa52e78cb2",
                    "visit_id": ""
                }
                res = requests.post(msg_url, headers=self.headers, data=data)
                self.data_queue.put(res.json()["data"]["room"])
            except Exception as e:
                logging.error(self.name, e)


class ParseThread(threading.Thread):
    def __init__(self, url: str, name: str, data_queue: Queue):
        """
        initial function
        :param url: room url
        :param name: thread name
        :param data_queue: data queue
        """
        super(ParseThread, self).__init__()
        self.name = name
        self.data_queue = data_queue
        self.room_id = re.findall(r"/(\d+)\?", url)[0]
        client = pymongo.MongoClient(host=MONGO_HOST, port=MONGO_PORT)
        self.col = client[MONGO_DB][MONGO_COL + self.room_id]

    def run(self):
        """
        get data from queue
        :return:
        """
        while 1:
            comments = self.data_queue.get()
            logging.info("Comment count: {}".format(len(comments)))
            self.parse(comments)

    def parse(self, comments):
        """
        parse comment to get message
        :return:
        """
        for x in comments:
            comment = {
                "text": x["text"],
                "time": x["timeline"],
                "username": x["nickname"],
                "user_id": x["uid"]
            }
            # print(comment)
            self.save_msg(comment)

    def save_msg(self, msg: dict):
        """
        save comment to MongoDB
        :param msg: comment
        :return:
        """
        try:
            self.col.insert_one(msg)
        except Exception as e:
            logging.info(msg)
            logging.error(e)


def create_crawl_thread(url: str, data_queue: Queue):
    """
    create thread to crawl comments
    :param url: room url
    :param data_queue: data queue
    :return:
    """
    crawl_name = ['crawler_1', 'crawler_2', 'crawler_3', 'crawler_4']
    for name in crawl_name:
        crawl_list.append(CrawlThread(url, name, data_queue))


def create_parse_thread(url: str, data_queue: Queue):
    """
    create thread to parse comments
    :param url: room url
    :param data_queue: data queue
    :return:
    """
    parse_name = ['parser_1', 'parser_2']
    for name in parse_name:
        parse_list.append(ParseThread(url, name, data_queue))


def is_chinese(word: str) -> bool:
    """
    judge it is Chinese or not
    :param word: word
    :return:
    """
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


def get_words(txt: str) -> str:
    """
    use jieba to cut words
    :param txt: input text
    :return:
    """
    # cut words
    seg_list = jieba.cut(txt)
    c = Counter()
    # count words
    for x in seg_list:
        if len(x) > 1 and x != '\r\n':
            c[x] += 1
    result = ""
    for (k, v) in c.most_common(300):
        # print('%s %d' % (k, v))
        result += "\n" + k
    return result


def cut_text(url: str):
    """
    query data from database
    :param url: room url
    :return:
    """
    room_id = re.findall(r"/(\d+)\?", url)[0]
    client = pymongo.MongoClient(host=MONGO_HOST, port=MONGO_PORT)
    col = client[MONGO_DB][MONGO_COL + room_id]
    # query
    data = [i["text"] for i in col.find({}, {"_id": 0, "text": 1})]
    txt = ""
    for text in data:
        for x in text:
            if x.isalpha() or is_chinese(x):
                txt += x
    jieba.load_userdict("userdict.txt")
    text = get_words(txt)
    generate_word_cloud(text)


def generate_word_cloud(text):
    """
    generate word cloud
    :param text: text
    :return:
    """
    # text cleaning
    with open("stopwords.txt", "r", encoding='utf-8') as f:
        stopwords = set(f.read().split("\n"))
    wc = WordCloud(
        font_path="font.ttf",
        background_color="white",
        width=1200,
        height=800,
        max_words=100,
        max_font_size=200,
        min_font_size=10,
        stopwords=stopwords,  # 设置停用词
    )
    # generate word cloud
    wc.generate("".join(text))
    # save as an image
    wc.to_file("rng_vs_skt.png")


if __name__ == "__main__":
    # the room href
    href = "https://live.bilibili.com/6?broadcast_type=0&visit_id=8abcmywu95s0#/"
    # create queue
    queue = Queue()
    crawl_list, parse_list = [], []
    create_crawl_thread(href, queue)
    create_parse_thread(href, queue)
    logging.info("Crawl Start!")
    # thread start
    for i in crawl_list:
        i.start()
    for i in parse_list:
        i.start()
    # thread run
    for i in crawl_list:
        i.join()
    for i in parse_list:
        i.join()
    cut_text(href)
