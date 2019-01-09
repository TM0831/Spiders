"""
Version: Python3.5
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2018/12/6 14:58
"""
import re
import requests
from lxml import etree
from fontTools.ttLib import TTFont

headers = {
    "Host": "maoyan.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 "
                  "Safari/537.36"
}


# 解析字体库
def parse_ttf(font_name):
    """
    :param font_name: 字体文件名
    :return: 字符-数字字典
    """
    base_nums = ['3', '0', '1', '6', '4', '2', '5', '8', '9', '7']
    base_fonts = ['uniEB84', 'uniF8CA', 'uniEB66', 'uniE9DB', 'uniE03C',
                  'uniF778', 'uniE590', 'uniED12', 'uniEA5E', 'uniE172']
    font1 = TTFont('base.woff')  # 本地保存的字体文件
    font2 = TTFont(font_name)  # 网上下载的字体文件

    uni_list = font2.getGlyphNames()[1:-1]  # 去掉头尾的多余字符
    temp = {}
    # 解析字体库
    for i in range(10):
        uni2 = font2['glyf'][uni_list[i]]
        for j in range(10):
            uni1 = font1['glyf'][base_fonts[j]]
            if uni2 == uni1:
                temp["&#x" + uni_list[i][3:].lower() + ";"] = base_nums[j]
    return temp


# 解析网页得到数字信息
def get_nums(font_dict):
    """
    :param font_dict: 字符-数字字典
    :return: 由评分、评分人数、票房和票价组成的列表
    """
    num_list = []
    with open('html', 'r', encoding='utf-8') as f:
        for line in f.readlines():
            lst = re.findall('(&#x.*?)<', line)
            if lst:
                num = lst[0]
                for i in font_dict.keys():
                    if i in num:
                        num = num.replace(i, font_dict[i])
                num_list.append(num)
    return num_list


# 爬取页面
def get_page():
    url = "http://maoyan.com/cinemas?movieId=42964"
    res = requests.get(url, headers=headers)
    # 提取woff字体的链接
    woff_url = re.findall(r"vfile.*?woff", res.text)[0]
    # 下载字体文件
    font_name = 'online.woff'
    with open(font_name, 'wb') as f:
        f.write(requests.get("http://" + woff_url).content)
    # 保存res.text用于后面解析
    with open('html', 'w', encoding='utf-8') as f:
        f.write(res.text)
    # 解析字体文件
    font_dict = parse_ttf(font_name)
    nums = get_nums(font_dict)
    price_list = nums[3:]  # 得到票价信息列表
    s = etree.HTML(res.text)
    movie_name = s.xpath('/html/body/div[3]/div/div[2]/div[1]/h3/text()')[0]  # 名字
    movie_type = s.xpath('/html/body/div[3]/div/div[2]/div[1]/ul/li[1]/text()')[0]  # 类型
    info = s.xpath('/html/body/div[3]/div/div[2]/div[1]/ul/li[2]/text()')[0]
    movie_country = info.strip().split('\n')[0]  # 国家
    movie_time = info.strip().split('\n')[1].split('/ ')[-1]  # 时长
    movie_score = nums[0] + '(评分人数：{})'.format(nums[1])  # 评分
    box_office = nums[2] + s.xpath('/html/body/div[3]/div/div[2]/div[3]/div[2]/div/span[2]/text()')[0]  # 票房
    cinema_list = s.xpath('//*[@id="app"]/div[2]/div/div[1]/a/text()')
    address_list = s.xpath('//*[@id="app"]/div[2]/div/div[1]/p/text()')
    print(movie_name)
    print(movie_type + "/" + movie_country + "/" + movie_time)
    print("评分："+movie_score, "票房："+box_office)
    for cinema, address, price in zip(cinema_list, address_list, price_list):
        print(cinema, address, "票价：" + price + "元")


if __name__ == '__main__':
    get_page()
