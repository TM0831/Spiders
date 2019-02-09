"""
Version: Python3.5
Author: OniOn
Site: http://www.cnblogs.com/TM0831/
Time: 2019/2/9 17:11
"""
import os
import re
from AutoWeather.get_ip import get_ip
from AutoWeather.get_mp3 import get_mp3
from AutoWeather.get_wather import get_weather


def main():
    ip = get_ip()
    print("您的IP地址是：{}\t\t您所在的城市是：{}".format(ip[0], ip[1]))
    city = re.findall('省(.+)市', ip[1])[0]
    # print(city)
    print("天气查询中，请稍等...")
    weather = get_weather(city)
    print("{}的天气情况如下：{}".format(city, weather))
    weather_text = "城市名称：{}，日期：{}，天气：{}，温度：{}，相对湿度：{}，PM2.5：{}。".format(
        city, weather["日期"], weather["天气"], weather["温度"], weather["相对湿度"], weather["PM2.5"],
    )
    get_mp3(text=weather_text)

    os.system("weather.mp3")  # 播放MP3文件


if __name__ == '__main__':
    main()
