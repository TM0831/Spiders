from BookingSystem.settings import *


class TrainUser:
    def __init__(self, username, password):
        self.name = ""
        self.username = username
        self.password = password
        self.url = "https://kyfw.12306.cn/otn/resources/login.html"
        self.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Length": "0",
            "Cookie": "JSESSIONID=3EE5CF7C86F87740B6854C647028C1BD; tk=hht-Etxts2U8F50eG7wLLLIPFIyPJf5CGmrX1gbcl1l0; JSESSIONID=F37CB71CF788F5B0C14BB511E5A97B1C; _jc_save_fromStation=%u6B66%u6C49%2CWHN; _jc_save_toStation=%u957F%u6C99%2CCSQ; _jc_save_wfdc_flag=dc; RAIL_EXPIRATION=1557180493556; RAIL_DEVICEID=PJwzDm1TjEnDumA9PPl7rv_TISjh2VABdM-CCJe4TyNx9VOX-IkY9Z5oePNINN52eRg5PsT62ag3N633D7NKYeWNqw0rJduVCzGRAzypSp5rAgnnK8v5hyhokFL9-vQc3LWeWiryirfUjRRcssiHM79DJQyGydjk; _jc_save_fromDate=2019-05-20; _jc_save_toDate=2019-05-05; BIGipServerotn=1123025418.50210.0000; route=6f50b51faa11b987e576cdb301e545c4; BIGipServerpool_passport=283968010.50215.0000",
            "Host": "kyfw.12306.cn",
            "Origin": "https://kyfw.12306.cn",
            "Referer": "https://kyfw.12306.cn/otn/view/information.html",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
        }

    def login(self):
        """
        模拟登录12306
        :return:
        """
        back_day = datetime.datetime.now()
        back_day = back_day.strftime("%Y-%m-%d")

        # options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        # browser = webdriver.Chrome(options=options)  # 设置为无头模式
        browser = webdriver.Chrome()
        browser.maximize_window()
        try:
            browser.get(self.url)
            browser.add_cookie({
                "name": "JSESSIONID",
                "value": "5E632327B65DFD1C5A9457E48C537B73",
            })
            browser.add_cookie({
                "name": "_jc_save_fromStation",
                "value": "%u6B66%u6C49%2CWHN",
            })
            browser.add_cookie({
                "name": "_jc_save_toStation",
                "value": "%u957F%u6C99%2CCSQ",
            })
            browser.add_cookie({
                "name": "_jc_save_wfdc_flag",
                "value": "dc",
            })
            browser.add_cookie({
                "name": "RAIL_EXPIRATION",
                "value": "1560095439082",
            })
            browser.add_cookie({
                "name": "RAIL_DEVICEID",
                "value": "P2wunHEkKFe9MgTM56h-NxsWiIGNkK6JLCOVaG0DHzRm-RxYa7YnDwftPoumiZ0wL7GPsQ93YBHRHgMgB_GLWwZ9Vb65tNiVuwaIOytW8lVG7B1KopI4pSyUr1u06RWpKPhvExBg3FA7ed87WxO3E-68Wg-hXZLl",
            })
            browser.add_cookie({
                "name": "_jc_save_fromDate",
                "value": "2019-05-20",
            })
            browser.add_cookie({
                "name": "_jc_save_toDate",
                "value": back_day,
            })
            browser.add_cookie({
                "name": "BIGipServerotn",
                "value": "300941834.24610.0000",
            })
            browser.add_cookie({
                "name": "BIGipServerpool_passport",
                "value": "250413578.50215.0000",
            })
            browser.add_cookie({
                "name": "route",
                "value": "495c805987d0f5c8c84b14f60212447d",
            })

            sleep(10)
            browser.find_element_by_xpath('/html/body/div[2]/div[2]/ul/li[1]/a').click()  # 扫码登录
            browser.find_element_by_xpath('/html/body/div[2]/div[2]/ul/li[2]/a').click()  # 账号登录

            browser.find_element_by_xpath('//*[@id="J-userName"]').send_keys(self.username)
            sleep(2)
            browser.find_element_by_xpath('//*[@id="J-password"]').send_keys(self.password)
            sleep(2)

            # 定位验证码图片
            img_element = WebDriverWait(browser, 100).until(EC.presence_of_element_located((By.ID, "J-loginImg")))
            base64_str = img_element.get_attribute("src").split(",")[-1]
            img = base64.b64decode(base64_str)
            with open('captcha.jpg', 'wb') as file:
                file.write(img)
            # 调用超级鹰识别验证码
            capture_result = use_cjy('captcha.jpg')
            # print(capture_result)
            # 对返回的结果进行解析
            groups = capture_result.get("pic_str").split('|')
            points = [[int(number) for number in group.split(',')] for group in groups]
            # print(points)
            for point in points:
                # 先定位到验证图片
                element = WebDriverWait(browser, 20).until(
                    EC.presence_of_element_located((By.ID, "J-loginImg")))
                # 模拟点击验证图片
                ActionChains(browser).move_to_element_with_offset(element, point[0], point[1]).click().perform()
                sleep(2)

            sleep(10)
            btn = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="J-login"]')))
            btn.click()
            sleep(5)
            cookie = browser.execute_script("return document.cookie;")
            # print(cookie)
            self.headers["Cookie"] = cookie
        except Exception as e:
            print("Error login!", e)
        finally:
            browser.quit()
            self.get_name()

    def get_name(self):
        """
        获取用户姓名
        :return:
        """
        url = "https://kyfw.12306.cn/otn/login/conf"
        res = requests.post(url, headers=self.headers)
        is_login = res.json()['data']['is_login']
        if is_login == 'Y':
            self.name = res.json()['data']['name']
            print("欢迎用户：{}".format(self.name))
        else:
            print("未登录！请先登录。")


if __name__ == '__main__':
    u = TrainUser("用户名", "密码")
    u.login()
