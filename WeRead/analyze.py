"""
Version: Python3.7
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/12/1 14:50
"""
from WeRead.config import *


def analyze_data():
    """
    analyze data
    :return:
    """
    # connect database
    client = pymongo.MongoClient(host=MONGO_HOST, port=MONGO_PORT)
    col = client[MONGO_DB][MONGO_COL]
    # sort books by star
    star_sort = col.find().sort("star", pymongo.DESCENDING).limit(20)
    id_list, star_ret = [], []
    for i in star_sort:
        if i["book_id"] not in id_list:
            star_ret.append((i["title"], i["star"] / 10))
            id_list.append(i["book_id"])
    star_ret = star_ret[:10]
    # sort books by read count
    read_sort = col.find().sort("read_count", pymongo.DESCENDING).limit(20)
    id_list, read_ret = [], []
    for i in read_sort:
        if i["book_id"] not in id_list:
            read_ret.append((i["title"], i["read_count"]))
            id_list.append(i["book_id"])
    read_ret = read_ret[:10]
    # sort authors by read count
    result = {}
    pipeline = [
        {'$group': {'_id': '$author', 'read_count': {'$sum': '$read_count'}}}
    ]
    for i in col.aggregate(pipeline):
        result[i["_id"]] = int(i["read_count"])
    result = sorted(result.items(), key=lambda x: x[1], reverse=True)
    result = result[:10]
    # print(star_ret)
    # print(read_ret)
    # print(result)
    paint_star(star_ret)
    paint_read(read_ret)
    paint_result(result)


def paint_star(data_list: list):
    """
    use pyecharts to paint data
    :param data_list: data list
    :return:
    """
    # initial data
    x_data = [i[0] for i in data_list][::-1]
    y_data = [i[1] for i in data_list][::-1]
    # paint
    bar = (
        Bar()
        .add_xaxis(x_data)
        .add_yaxis("书籍", y_data, category_gap="70%")
        .set_global_opts(
            title_opts=opts.TitleOpts(title="评分前十的书籍"),
            xaxis_opts=opts.AxisOpts(name="评分"),
            yaxis_opts=opts.AxisOpts(name="书名")
        )
    )
    bar.reversal_axis()
    bar.render("star.html")


def paint_read(data_list: list):
    """
    use pyecharts to paint data
    :param data_list: data list
    :return:
    """
    # initial data
    x_data = [i[0] for i in data_list][::-1]
    y_data = [i[1] for i in data_list][::-1]
    # paint
    bar = (
        Bar()
        .add_xaxis(x_data)
        .add_yaxis("书籍", y_data, category_gap="70%")
        .set_global_opts(
            title_opts=opts.TitleOpts(title="阅读量前十的书籍"),
            xaxis_opts=opts.AxisOpts(name="阅读量"),
            yaxis_opts=opts.AxisOpts(name="书名")
        )
    )
    bar.reversal_axis()
    bar.render("read.html")


def paint_result(data_list: list):
    """
    use pyecharts to paint data
    :param data_list: data list
    :return:
    """
    # initial data
    x_data = [i[0] for i in data_list][::-1]
    y_data = [i[1] for i in data_list][::-1]
    # paint
    bar = (
        Bar()
        .add_xaxis(x_data)
        .add_yaxis("作者", y_data, category_gap="70%")
        .set_global_opts(
            title_opts=opts.TitleOpts(title="阅读量前十的作者"),
            xaxis_opts=opts.AxisOpts(name="阅读量"),
            yaxis_opts=opts.AxisOpts(name="作者")
        )
    )
    bar.reversal_axis()
    bar.render("result.html")
