import json
import requests
from PIL import Image
from time import sleep
from .CJYDemo import use_cjy
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1"
                  " Safari/537.1"
}


class TrainUser:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.cookie = ""
        self.station_data = ""

    # 登录12306
    def login(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        browser = webdriver.Chrome(chrome_options=chrome_options)
        browser.get("https://kyfw.12306.cn/otn/login/init")
        browser.find_element_by_xpath('//*[@id="username"]').send_keys(self.username)
        sleep(2)
        browser.find_element_by_xpath('//*[@id="password"]').send_keys(self.password)
        sleep(2)
        captcha_img = browser.find_element_by_xpath('//*[@id="loginForm"]/div/ul[2]/li[4]/div/div/div[3]/img')
        location = captcha_img.location
        size = captcha_img.size
        # 写成我们需要截取的位置坐标
        coordinates = (int(location['x']), int(location['y']),
                       int(location['x'] + size['width']), int(location['y'] + size['height']))
        browser.save_screenshot('screen.png')
        i = Image.open('screen.png')
        # 使用Image的crop函数，从截图中再次截取我们需要的区域
        verify_code_image = i.crop(coordinates)
        verify_code_image.save('captcha.png')
        # 调用超级鹰识别验证码
        capture_result = use_cjy('captcha.png')
        print(capture_result)
        # 对返回的结果进行解析
        groups = capture_result.get("pic_str").split('|')
        points = [[int(number) for number in group.split(',')] for group in groups]
        for point in points:
            # 先定位到验证图片
            element = WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "touclick-bgimg")))
            # 模拟点击验证图片
            ActionChains(browser).move_to_element_with_offset(element, point[0], point[1]).click().perform()
            sleep(1)
        browser.find_element_by_xpath('//*[@id="loginSub"]').click()
        cookie = json.dumps(browser.get_cookies())
        cookie_list = [item['name'] + "=" + item['value'] for item in json.loads(cookie)]
        cookie_str = ';'.join(item for item in cookie_list)
        self.cookie = cookie_str
        print(self.cookie + "\n您已登录成功！")

    # 显示可购车票信息
    def show_ticket(self):
        # 请求保存列车站点代码的链接
        res1 = requests.get("https://kyfw.12306.cn/otn/resources/js/framework/station_name.js")
        # 把分割处理后的车站信息保存在station_data中
        self.station_data = res1.text.lstrip("var station_names ='").rstrip("'").split('@')
        # 需要按2018-01-01的格式输入日期，不然会出现错误
        d = input("请输入日期（如：2018-01-01）：")
        f = self.get_station(input("请输入您的出发站："))
        t = self.get_station(input("请输入您的目的站："))
        url = "https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}" \
              "&leftTicketDTO.to_station={}&purpose_codes=ADULT".format(d, f, t)
        res2 = requests.get(url)
        result = json.loads(res2.text)['data']['result']
        seat_data = [(32, "商务座"), (31, "一等座"), (30, "二等座"), (26, "无座"), (23, "软卧"), (28, "硬卧"), (29, "硬座")]
        for i in result:
            i = i.split('|')
            info = {
                "车次": i[3], "出发日期": i[13], "始发站": self.get_city(i[4]), "终点站": self.get_city(i[7]),
                "出发站": self.get_city(i[6]), "目的站": self.get_city(i[5]), "出发时间": i[8], "到达时间": i[9],
                "总耗时": str(int(i[10][:i[10].index(":")])) + "小时" + str(int(i[10][i[10].index(":") + 1:])) + "分钟",
                "商务座": '', "一等座": '', "二等座": '', "无座": '', "软卧": '', "硬卧": '', "硬座": ''
            }
            for j in range(7):
                if i[seat_data[j][0]] == "有" or i[seat_data[j][0]].isdigit():
                    info[seat_data[j][1]] = i[seat_data[j][0]]
                else:
                    del info[seat_data[j][1]]
            print(info)

    # 返回车站英文缩写
    def get_station(self, city):
        for i in self.station_data:
            if city in i:
                return i.split('|')[2]

    # 返回车站中文缩写
    def get_city(self, station):
        for i in self.station_data:
            if station in i:
                return i.split('|')[1]


if __name__ == '__main__':
    u = TrainUser(input("请输入您的用户名："), input("请输入您的密码："))
    u.login()
    u.show_ticket()
