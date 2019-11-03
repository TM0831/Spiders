"""
Version: Python3.7
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/11/2 22:22
"""
from FJCourt.config import *


class FJSpider:
    def __init__(self):
        """
        initialize
        """
        ua = UserAgent(verify_ssl=False)
        self.base_url = "http://www.fjcourt.gov.cn/page/public/courtreport.html"
        self.base_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": "Hm_lvt_5b3a903dfec5ceeedc657e93ebc7c5f4=1572268428; Hm_lpvt_5b3a903dfec5ceeedc657e93ebc7c5f4=1572268428",
            "Host": "www.fjcourt.gov.cn",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": ua.random
        }
        self.href_list = []
        self.col = None

    def request(self, data):
        """
        send request
        :param data: post data
        :return:
        """
        try:
            resp = requests.post(url=self.base_url, headers=self.base_headers, data=data)
            html = resp.text
            self.parse(html)
        except Exception as e:
            logging.error(e)

    def parse(self, html=None):
        """
        parse html and get href
        :param html: response html
        :return:
        """
        if html:
            # use xpath to parse html
            data = {
                "ctl00$cplContent$txt_search_content": "",
                "ctl00$cplContent$txtdq": ""
            }

            et = etree.HTML(html)
            href_list = et.xpath('//*[@id="bd-timeline-list"]/li/ul/li/a/@href')
            for href in href_list:
                self.href_list.append("http://www.fjcourt.gov.cn" + href)

            data["__VIEWSTATE"] = et.xpath('//*[@id="__VIEWSTATE"]/@value')[0]
            data["__VIEWSTATEGENERATOR"] = et.xpath('//*[@id="__VIEWSTATEGENERATOR"]/@value')[0]
            data["__EVENTVALIDATION"] = et.xpath('//*[@id="__EVENTVALIDATION"]/@value')[0]
            # use regex match
            pat = re.compile(
                r'</span><a class="pagination" class href="javascript:__doPostBack\(&#39;(.*?)&#39;,&#39;(\d*?)'
                r'&#39;\)" style="margin-right:2px;">下一页</a>')
            next_page = re.findall(pat, html)
            # get next page
            if len(next_page):
                logging.info("Crawling page: {}".format(next_page[0][1]))
                data["__EVENTTARGET"] = next_page[0][0]
                data["__EVENTARGUMENT"] = next_page[0][1]
                self.request(data)
        else:
            # if html is none, send get request
            resp = requests.get(url=self.base_url, headers=self.base_headers)
            logging.info("Crawling page: 1")
            self.parse(resp.text)

    def get_page(self, page_url):
        """
        get content page
        :param page_url: page url
        :return:
        """
        self.base_headers["Referer"] = self.base_url
        resp = requests.get(url=page_url, headers=self.base_headers)
        et = etree.HTML(resp.text)
        title = et.xpath('//*[@class="article-hd-title"]/text()')[0]
        content = et.xpath('//*[@class="article-content"]/text()')[0]
        info = {
            "url": page_url,
            "title": title,
            "content": content
        }
        self.save(info)

    def save(self, data):
        """
        use MongoDB to save data
        :param data: data
        :return:
        """
        try:
            client = pymongo.MongoClient(host=MONGO_HOST, port=MONGO_PORT)
            self.col = client[MONGO_DB][MONGO_COL]
            self.col.insert_one(data)
        except Exception as e:
            logging.error(e)

    def main(self):
        """
        main function
        :return:
        """
        self.parse()
        # process pool
        pool = Pool(processes=4)
        pool.map(self.get_page, self.href_list)


if __name__ == '__main__':
    fj = FJSpider()
    fj.main()
