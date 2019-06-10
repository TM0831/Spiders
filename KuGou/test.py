"""
Version: Python3.7
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/6/10 15:00
"""
import re
import json
import time
import requests
from fake_useragent import UserAgent

ua = UserAgent()


def get_song(song_name):
    search_url = "https://songsearch.kugou.com/song_search_v2?callback=jQuery112405132987859127838_1550204317910&page" \
                 "=1&pagesize=30&userid=-1&clientver=&platform=WebFilter&tag=em&filter=2&iscorrection=1&privilege_fil" \
                 "ter=0&_=1550204317912&keyword={}".format(song_name)
    headers1 = {
        "UserAgent": ua.random
    }
    headers2 = {
        "Cookie": "kg_mid=3786e26250f01bf2c64bc515820d9752; Hm_lvt_aedee6983d4cfc62f509129360d6bb3d=1559960644; Hm_lpvt_aedee6983d4cfc62f509129360d6bb3d=1559960644; ACK_SERVER_10015=%7B%22list%22%3A%5B%5B%22bjlogin-user.kugou.com%22%5D%5D%7D; ACK_SERVER_10016=%7B%22list%22%3A%5B%5B%22bjreg-user.kugou.com%22%5D%5D%7D; ACK_SERVER_10017=%7B%22list%22%3A%5B%5B%22bjverifycode.service.kugou.com%22%5D%5D%7D; kg_dfid=0iEqIA1uep0h0AogH30Jq1Od; kg_dfid_collect=d41d8cd98f00b204e9800998ecf8427e",
        "Host": "www.kugou.com",
        "Referer": "http://www.kugou.com/",
        "UserAgent": ua.random
    }
    res = requests.get(search_url, headers=headers1)
    # print(res.text)
    start = re.search("jQuery\d+_\d+\(?", res.text)
    js = json.loads(res.text.strip().lstrip(start.group()).rstrip(")"))  # 注意：末尾有一个换行需要去掉
    song_list = js['data']['lists']

    for i in range(10):
        print(str(i + 1) + ">>>" + str(song_list[i]['FileName']).replace('<em>', '').replace('</em>', ''))

    num = int(input("\n请输入您想要下载的歌曲序号："))

    print("请稍等，下载歌曲中...")
    time.sleep(1)

    file_hash = song_list[num - 1]['FileHash']

    hash_url = "http://www.kugou.com/yy/index.php?r=play/getdata&hash={}".format(file_hash)
    # print(hash_url)
    hash_res = requests.get(hash_url, headers=headers2)
    hash_js = hash_res.json()  # json格式
    # print(hash_js)
    play_url = hash_js['data']['play_url']

    # 下载歌曲
    try:
        with open("music/" + song_name + ".mp3", "wb")as fp:
            fp.write(requests.get(play_url).content)
        print("歌曲已下载完成！")
    except Exception as e:
        print(e)


if __name__ == '__main__':
    get_song(input("请输入您想要搜索的歌曲名称："))
