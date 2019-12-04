"""
Version: Python3.7
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/12/1 11:41
"""
from WeRead.config import *
from WeRead.analyze import analyze_data


def prepare(base_url="https://weread.qq.com/web/category/1700000") -> list:
    """
    prepare for crawler
    :param base_url: weread base url
    :return: page url list
    """
    def request(url) -> list:
        """
        request function
        :param url: url
        :return: page url list
        """
        page_urls = []
        try:
            res = requests.get(url=url, headers=headers)
            if res.status_code == 200:
                count = res.json()["totalCount"]
                cnt = 50 if count >= 1000 else count // 20
                page_urls = [url + "?maxIndex={}".format(i * 20) for i in range(cnt)]
            else:
                logging.error("Error request!")
        except Exception as e:
            logging.error(e)
        finally:
            return page_urls

    resp = requests.get(url=base_url, headers=headers)
    # check status code
    if resp.status_code == 200:
        id_list = re.findall('"CategoryId":"(.+?)"', resp.text)
        id_list = list(set([i for i in id_list if i[0].isdigit()]))
        href_list = ["https://weread.qq.com/web/bookListInCategory/{}".format(i) for i in id_list]
        result = []
        for href in href_list:
            result += request(href)
        logging.info("Url count: {}".format(len(result)))
        return result
    else:
        logging.error("Prepare error!")
        exit()


def get_page(page_url: str):
    """
    request page and get data
    :param page_url: page url
    :return:
    """
    try:
        time.sleep(random.randint(1, 3))
        resp = requests.get(url=page_url, headers=headers, verify=False)
        # check status code
        if resp.status_code == 200:
            books = resp.json()["books"]
            info_list = []
            with open("id.txt", "r") as f:
                ids = f.readlines()
            with open("id.txt", "a") as f:
                for book in books:
                    if str(book["bookInfo"]["bookId"]) not in ids:
                        f.write(str(book["bookInfo"]["bookId"]) + "\n")
                        book_info = {
                            "author": book["bookInfo"]["author"],
                            "book_id": book["bookInfo"]["bookId"],
                            "category": book["bookInfo"]["category"],
                            "introduce": book["bookInfo"]["intro"],
                            "price": book["bookInfo"]["price"],
                            "title": book["bookInfo"]["title"],
                            "read_count": book["readingCount"],
                            "star": book["bookInfo"]["star"]
                        }
                        info_list.append(book_info)
            save_data(info_list)
        else:
            logging.info("Crawl url: " + page_url)
            logging.error("Error request!")
    except Exception as e:
        logging.info("Crawl url: " + page_url)
        logging.error(e)


def save_data(data: list):
    """
    use MongoDB to save data
    :param data: data need to save
    :return:
    """
    client = pymongo.MongoClient(host=MONGO_HOST, port=MONGO_PORT)
    col = client[MONGO_DB][MONGO_COL]
    try:
        col.insert_many(data)
    except Exception as e:
        logging.error(e)
    finally:
        client.close()


if __name__ == '__main__':
    urls = prepare()
    pool = Pool(processes=8)
    pool.map(func=get_page, iterable=urls)
    logging.info("Crawl Finished!")
    analyze_data()
