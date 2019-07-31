"""
Version: Python3.7
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/7/29 11:12
"""
import json
import time
import random
import pymongo
import pymysql
import requests
from lxml import etree
from itertools import product
from multiprocessing import Pool
from fake_useragent import UserAgent

ua = UserAgent(verify_ssl=False)  # 随机UserAgent
headers = {
    "Cookie": "_ga=GA1.2.117287736.1563932876; _gid=GA1.2.2043475287.1564386587; PHPSESSID=o7gohp2oea5826209mimj3obf5; _csrf=276309c0888832ececf73f6b299697abd9f51845d1f5afd8e50b8f541a80eb5fs%3A32%3A%221XcSjzdWIbn7h94C8xVyCwXOZ7UVk0gk%22%3B; _gat_gtag_UA_48535903_19=1",
    "Host": "www.ctic.org",
    "UserAgent": ua.random,
    "X-Requested-With": "XMLHttpRequest"
}
csrf = ""  # 加密参数
years = ["1989", "1990", "1991", "1992", "1993", "1994", "1995", "1996",
         "1997", "1998", "2002", "2004", "2006", "2007", "2008", "2011"]  # 年份
regions = ["Midwest", "Northeast", "South", "West"]  # 地区


def request():
    """
    请求页面，获取csrf
    :return:
    """
    global csrf
    url = "https://www.ctic.org/crm?tdsourcetag=s_pctim_aiomsg"
    res = requests.get(url, headers=headers)
    et = etree.HTML(res.text)
    csrf = et.xpath("/html/head/meta[3]/@content")[0]
    # print("Now csrf: ", csrf)
    return csrf


def get_states(data):
    """
    获取地区下的州信息
    :param data: 请求参数
    :return:
    """
    time.sleep(random.randint(1, 5))
    url = "https://www.ctic.org/admin/custom/crm/getstates/"
    region = data["region"]
    year = data["year"]
    res = requests.post(url, headers=headers, data=data)
    et = etree.HTML(res.text)
    result = et.xpath('//option/@value')
    result = [i[2:4] for i in result]
    # print("state num :", len(result))
    data_ = {
        "_csrf": csrf,
        "CRMSearchForm[area]": "National",
        "CRMSearchForm[region]": region,
        "CRMSearchForm[state]": "",
        "CRMSearchForm[county]": "",
        "CRMSearchForm[year]": year,
        "CRMSearchForm[format]": "Acres",
        "CRMSearchForm[crop_type]": "All",
        "summary": "county"
    }
    data.pop("region")
    for i in result:
        data_["CRMSearchForm[state]"] = i
        data["state"] = i
        get_countries(data, data_)


def get_countries(data, data_):
    """
    获取各个州下面的郡县信息
    :param data: 请求参数
    :return:
    """
    time.sleep(random.randint(1, 5))  # 随机等待
    db = pymongo.MongoClient(host="127.0.0.1", port=27017)  # 使用MongoDB数据库
    col = db["Spiders"]["CRM_Params"]
    url = "https://www.ctic.org/admin/custom/crm/getcounties/"
    res = requests.post(url, headers=headers, data=data)
    et = etree.HTML(res.text)
    result = et.xpath('//option/text()')
    result = [i.rstrip('"') for i in result]
    # print("county num :", len(result))
    for i in result:
        data_["CRMSearchForm[county]"] = i
        # print({"data": str(data_)})
        col.insert_one({"data": str(data_)})


def get_page(data):
    """
    请求农田数据页面，返回网页源码
    :param data: 请求参数
    :return:
    """
    time.sleep(random.randint(1, 5))
    the_csrf = request()
    url1 = "https://www.ctic.org/crm?tdsourcetag=s_pctim_aiomsg"
    data['_csrf'] = the_csrf
    res1 = requests.post(url1, headers=headers, data=data)  # 模拟提交表单
    # 构造作物数据信息
    crop_data = {
        "year": data["CRMSearchForm[year]"],
        "area": data["CRMSearchForm[area]"],
        "region": data["CRMSearchForm[region]"],
        "state": data["CRMSearchForm[state]"],
        "county": data["CRMSearchForm[county]"],
        "crop_name": "",
        "total_area": "",
        "conservation_area": ""
    }

    url2 = "https://www.ctic.org/crm/?action=result"
    headers["Referer"] = url1
    res2 = requests.get(url2, headers=headers, timeout=5)
    if res2.status_code == 200:
        parse_page(res2.text, crop_data)
    else:
        with open('log.txt', 'a', encoding="utf-8") as f:
            f.write(str(data) + '\n')


def parse_page(html, crop_data):
    """
    解析页面
    :param html: 网页源码
    :param crop_data: 作物数据
    :return:
    """
    et = etree.HTML(html)
    crop_list = et.xpath('//*[@id="crm_results_eight"]/tbody/tr/td[1]/text()')
    area_list = et.xpath('//*[@id="crm_results_eight"]/tbody/tr/td[2]/text()')
    conservation_list = et.xpath('//*[@id="crm_results_eight"]/tbody/tr/td[6]/text()')
    crop_list = crop_list[:-3]
    area_list = area_list[:-3]
    conservation_list = conservation_list[:-3]

    for crop, area, cons in zip(crop_list, area_list, conservation_list):
        crop_data["crop_name"] = crop
        crop_data["total_area"] = area
        crop_data["conservation_area"] = cons
        # print(crop_data)
        save_data(crop_data)


def save_data(crop_data):
    """
    保存数据，使用的数据库为MySQL
    :param crop_data: 作物数据
    :return:
    """
    conn = pymysql.Connect(host="127.0.0.1", port=3306, user="root", password="root", database="spiders")
    cursor = conn.cursor()
    try:
        sql = "insert into crm_data values ('%s','%s','%s','%s','%s','%s','%s','%s')" \
              % (crop_data["year"], crop_data["area"], crop_data["region"], crop_data["state"], crop_data["county"],
                 crop_data["crop_name"], crop_data["total_area"], crop_data["conservation_area"])
        cursor.execute(sql)
    except Exception as e:
        with open('log.txt', 'a', encoding="utf-8") as f:
            f.write(str(e) + "\n" + str(crop_data))
    finally:
        conn.commit()
        conn.close()


def create_table():
    """
    在数据库中创建数据表
    :return:
    """
    conn = pymysql.Connect(host="127.0.0.1", port=3306, user="root", password="root", database="spiders")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            create table CRM_DATA (
            year varchar(4) not null,
            area varchar(20) not null,
            region varchar(20) not null,
            state varchar(20) not null,
            county varchar(20) not null,
            crop_name varchar(20) not null,
            tatol_area varchar(10) not null,
            cons_area varchar(10) not null
            );
            """)
    except:
        print("创建数据表失败！")
    finally:
        cursor.close()


def main():
    """
    先创建数据表，然后获取郡县信息，最后获取农田数据
    :return:
    """
    print("[INFO]Creating table...")
    create_table()

    print("[INFO]Crawling params...")
    request()
    params_list = product(years, regions)  # 排列组合
    params_list = [{"year": i[0], "region": i[1], "_csrf": csrf} for i in params_list]  # 列表生成式
    pool = Pool(processes=4)  # 使用进程池
    pool.map(get_states, params_list)

    mon_db = pymongo.MongoClient(host="127.0.0.1", port=27017)
    mon_col = mon_db["Spiders"]["CRM_Params"]
    data_list = mon_col.find({}, {"_id": 0, "data": 1})
    data_list = [i["data"] for i in data_list]
    print("[INFO]Params count: ", len(data_list))

    print("[INFO]Crawling data...")
    data_list = [json.loads(data.replace("'", '"')) for data in data_list]
    pool = Pool(processes=4)  # 使用进程池
    pool.map(get_page, data_list)
    print("[INFO]Crawling done!")


if __name__ == '__main__':
    main()
