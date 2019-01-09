import random
import pymongo
import requests
from time import sleep
import matplotlib.pyplot as plt
from multiprocessing import Pool


# 返回随机的User-Agent
def get_random_ua():
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/"
        "536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 "
        "Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]
    return {
        "User-Agent": random.choice(user_agent_list)
    }


# 返回关注数和粉丝数
def get():
    res = requests.get("https://m.weibo.cn/profile/info?uid=5720474518")
    return res.json()['data']['user']['follow_count'], res.json()['data']['user']['followers_count']


# 获取内容并解析
def get_and_parse1(url):
    res = requests.get(url)
    cards = res.json()['data']['cards']
    info_list = []
    try:
        for i in cards:
            if "title" not in i:
                for j in i['card_group'][1]['users']:
                    user_name = j['screen_name']  # 用户名
                    user_id = j['id']  # 用户id
                    fans_count = j['followers_count']  # 粉丝数量
                    sex, add = get_user_info(user_id)
                    info = {
                        "用户名": user_name,
                        "性别": sex,
                        "所在地": add,
                        "粉丝数": fans_count,
                    }
                    info_list.append(info)
            else:
                for j in i['card_group']:
                    user_name = j['user']['screen_name']  # 用户名
                    user_id = j['user']['id']  # 用户id
                    fans_count = j['user']['followers_count']  # 粉丝数量
                    sex, add = get_user_info(user_id)
                    info = {
                        "用户名": user_name,
                        "性别": sex,
                        "所在地": add,
                        "粉丝数": fans_count,
                    }
                    info_list.append(info)
        if "followers" in url:
            print("第1页关注信息爬取完毕...")
        else:
            print("第1页粉丝信息爬取完毕...")
        save_info(info_list)
    except Exception as e:
        print(e)


# 爬取第一页的关注和粉丝信息
def get_first_page():
    url1 = "https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_5720474518"  # 关注
    url2 = "https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_5720474518"  # 粉丝
    get_and_parse1(url1)
    get_and_parse1(url2)


# 获取内容并解析
def get_and_parse2(url, data):
    res = requests.get(url, headers=get_random_ua(), data=data)
    sleep(3)
    info_list = []
    try:
        if 'cards' in res.json()['data']:
            card_group = res.json()['data']['cards'][0]['card_group']
        else:
            card_group = res.json()['data']['cardlistInfo']['cards'][0]['card_group']
        for card in card_group:
            user_name = card['user']['screen_name']  # 用户名
            user_id = card['user']['id']  # 用户id
            fans_count = card['user']['followers_count']  # 粉丝数量
            sex, add = get_user_info(user_id)
            info = {
                "用户名": user_name,
                "性别": sex,
                "所在地": add,
                "粉丝数": fans_count,
            }
            info_list.append(info)
        if "page" in data:
            print("第{}页关注信息爬取完毕...".format(data['page']))
        else:
            print("第{}页粉丝信息爬取完毕...".format(data['since_id']))
        save_info(info_list)
    except Exception as e:
        print(e)


# 爬取关注的用户信息
def get_follow(num):
    url1 = "https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_5720474518&page={}".format(num)
    data1 = {
        "containerid": "231051_ - _followers_ - _5720474518",
        "page": num
    }
    get_and_parse2(url1, data1)


# 爬取粉丝的用户信息
def get_followers(num):
    url2 = "https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_5720474518&since_id={}".format(num)
    data2 = {
        "containerid": "231051_-_fans_-_5720474518",
        "since_id": num
    }
    get_and_parse2(url2, data2)


# 爬取用户的基本资料（性别和所在地）
def get_user_info(uid):
    uid_str = "230283" + str(uid)
    url2 = "https://m.weibo.cn/api/container/getIndex?containerid={}_-_INFO&title=%E5%9F%BA%E6%9C%AC%E8%B5%84%E6%96%99&luicode=10000011&lfid={}&featurecode=10000326".format(
        uid_str, uid_str)
    data2 = {
        "containerid": "{}_-_INFO".format(uid_str),
        "title": "基本资料",
        "luicode": 10000011,
        "lfid": int(uid_str),
        "featurecode": 10000326
    }
    res2 = requests.get(url2, headers=get_random_ua(), data=data2)
    data = res2.json()['data']['cards'][1]
    if data['card_group'][0]['desc'] == '个人信息':
        sex = data['card_group'][1]['item_content']
        add = data['card_group'][2]['item_content']
    else:  # 对于企业信息，返回性别为男
        sex = "男"
        add = data['card_group'][1]['item_content']
    # 对于所在地有省市的情况，把省份取出来
    if ' ' in add:
        add = add.split(' ')[0]
    return sex, add


# 把数据保存到MongoDB数据库中
def save_info(data):
    conn = pymongo.MongoClient(host="127.0.0.1", port=27017)
    db = conn["Spider"]
    db.WeiBoUsers.insert(data)


# 绘制男女比例扇形图
def plot_sex():
    conn = pymongo.MongoClient(host="127.0.0.1", port=27017)
    col = conn['Spider'].WeiBoUsers
    sex_data = []
    for i in col.find({}, {"性别": 1}):
        sex_data.append(i['性别'])
    labels = '男', '女'
    sizes = [sex_data.count('男'), sex_data.count('女')]
    # 设置分离的距离，0表示不分离
    explode = (0, 0)
    plt.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
    # 保证画出的是圆形
    plt.axis('equal')
    # 保证能够显示中文
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.savefig("sex.jpg")
    print("已保存为sex.jpg！")


# 绘制用户所在地条形图
def plot_province():
    conn = pymongo.MongoClient(host="127.0.0.1", port=27017)
    col = conn['Spider'].WeiBoUsers
    province_list = ['北京', '天津', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江', '上海', '江苏', '浙江', '安徽',
                     '福建', '江西', '山东', '河南', '湖北', '湖南', '广东', '广西', '海南', '重庆', '四川', '贵州',
                     '云南', '陕西', '甘肃', '青海', '宁夏', '新疆', '西藏', '台湾', '香港', '澳门', '其他', '海外']
    people_data = [0 for _ in range(36)]
    for i in col.find({}, {"所在地": 1}):
        people_data[province_list.index(i['所在地'])] += 1
    # 清洗掉人数为0的数据
    index_list = [i for i in range(len(people_data)) if people_data[i] == 0]
    j = 0
    for i in range(len(index_list)):
        province_list.remove(province_list[index_list[i] - j])
        people_data.remove(people_data[index_list[i] - j])
        j += 1
    # 排序
    for i in range(len(people_data)):
        for j in range(len(people_data) - i - 1):
            if people_data[j] > people_data[j + 1]:
                people_data[j], people_data[j + 1] = people_data[j + 1], people_data[j]
                province_list[j], province_list[j + 1] = province_list[j + 1], province_list[j]
    province_list = province_list[:-1]
    people_data = people_data[:-1]
    # 图像绘制
    fig, ax = plt.subplots()
    b = ax.barh(range(len(province_list)), people_data, color='blue', height=0.8)
    # 添加数据标签
    for rect in b:
        w = rect.get_width()
        ax.text(w, rect.get_y() + rect.get_height() / 2, '%d' % int(w), ha='left', va='center')
    # 设置Y轴刻度线标签
    ax.set_yticks(range(len(province_list)))
    ax.set_yticklabels(province_list)
    plt.xlabel("单位/人")
    plt.ylabel("所在地")
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.savefig("province.jpg")
    print("已保存为province.jpg！")


# 绘制用户粉丝数量柱状图
def plot_fans():
    conn = pymongo.MongoClient(host="127.0.0.1", port=27017)
    col = conn['Spider'].WeiBoUsers
    fans_list = ["1-10", "11-50", "51-100", "101-500", "501-1000", "1000以上"]
    fans_data = [0 for _ in range(6)]
    for i in col.find({}, {"粉丝数": 1}):
        fans_data[0] += 1 if 1 <= i["粉丝数"] <= 10 else 0
        fans_data[1] += 1 if 11 <= i["粉丝数"] <= 50 else 0
        fans_data[2] += 1 if 51 <= i["粉丝数"] <= 100 else 0
        fans_data[3] += 1 if 101 <= i["粉丝数"] <= 500 else 0
        fans_data[4] += 1 if 501 <= i["粉丝数"] <= 1000 else 0
        fans_data[5] += 1 if 1001 <= i["粉丝数"] else 0
    # print(fans_data)
    # 绘制柱状图
    plt.bar(x=fans_list, height=fans_data, color="green", width=0.5)
    # 显示柱状图形的值
    for x, y in zip(fans_list, fans_data):
        plt.text(x, y + sum(fans_data) // 50, "%d" % y, ha="center", va="top")
    plt.xlabel("粉丝数")
    plt.ylabel("单位/人")
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.savefig("fans.jpg")
    print("已保存为fans.jpg！")


if __name__ == '__main__':
    follow_count, followers_count = get()
    get_first_page()
    # 由于当page或者since_id大于250时就已经无法得到内容了，所以要设置最大页数为250
    max_page1 = follow_count // 20 + 1 if follow_count < 5000 else 250
    max_page2 = followers_count // 20 + 1 if followers_count < 5000 else 250
    # 使用进程池加快爬虫的效率
    pool = Pool(processes=4)
    # 爬取关注的用户信息
    start1, end1 = 2, 12
    for i in range(25):
        pool.map(get_follow, range(start1, end1))
        # 超过max_page则跳出循环
        if end1 < max_page1:
            start1 = end1
            end1 = start1 + 10
            sleep(5)
        else:
            break
    # 爬取粉丝的用户信息
    start2, end2 = 2, 50
    for i in range(5):
        pool.map(get_followers, range(start2, end2))
        # 超过max_page则跳出循环
        if end2 < max_page2:
            start2 = end2
            end2 = start2 + 50
            sleep(10)
        else:
            break
    # 可视化成图表
    plot_sex()
    plot_province()
    plot_fans()