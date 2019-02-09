"""
Version: Python3.5
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/2/9 17:53
"""
from aip import AipSpeech

# 你的APP_ID,API_KEY,SECRET_KEY
APP_ID = ""
API_KEY = ""
SECRET_KEY = ""


# 获取语音文件
def get_mp3(text):
    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

    result = client.synthesis(text, 'zh', 1, {"spd": 4, "vol": 6})

    # 识别正确返回语音二进制，错误则返回dict
    if not isinstance(result, dict):
        with open('weather.mp3', 'wb') as f:
            f.write(result)
    else:
        print("Error!")
        exit()
