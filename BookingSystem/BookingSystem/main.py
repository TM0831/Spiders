from BookingSystem.user import TrainUser
from BookingSystem.ticket import TrainTicket
from BookingSystem.settings import *

token = ""


# 检查用户是否登录
def check_passenger():
    try:
        url = "https://kyfw.12306.cn/otn/login/checkUser"
        data = {
            "_json_att": ""
        }
        res = requests.post(url, headers=headers, data=data)
        return res.json()['data']['flag']
    except Exception as e:
        print(e)


# 初始化，获取token值
def init_dc():
    global token
    url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
    data = {
        "_json_att": ""
    }
    res = requests.post(url, headers=headers, data=data)
    result = re.findall(" var globalRepeatSubmitToken = '(.*?)';", res.text)
    # print(result)
    if len(result):
        token = result[0]
    else:
        raise Exception("Error init")


# 初始化购票页面
def init_page():
    url = "https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc"
    res = requests.get(url)
    # print(res.text)


# 确认用户登录状态
def check_user():
    url = "https://kyfw.12306.cn/otn/login/checkUser"
    data = {
        "_json_att": ""
    }
    res = requests.post(url, headers=headers, data=data)
    # print(res.text)


# 提交车票预订信息
def submit_order(back_date, purpose_codes, from_name, to_name, secret, train_date):
    url = "https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest"
    data = {
        "back_train_date": back_date,
        "purpose_codes": purpose_codes,
        "query_from_station_name": from_name,
        "query_to_station_name": to_name,
        "secretStr": secret,
        "tour_flag": "dc",
        "train_date": train_date,
        "undefined": ""
    }
    res = requests.post(url, headers=headers, data=data)
    # print(res.text)


# 确认预订信息
def check_init():
    url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
    data = {
        "_json_att": ""
    }
    res = requests.post(url, headers=headers, data=data)
    return res.text


# 获取乘客信息
def get_passenger():
    url = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
    res = requests.get(url, headers=headers)
    js = json.loads(res.text)
    result = js['data']['normal_passengers']
    return result


# 确认订单信息
def check_order_info(name, uid, mobile, type_id):
    # 商务座，一等座，二等座，软卧，硬卧，硬座
    type_str = ["9,0,1,", "M,0,1,", "O,0,1,", "4,0,1,", "3,0,1,", "1,0,1,"][type_id]
    url = "https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo"
    data = {
        "_json_att": "",
        "bed_level_order_num": "000000000000000000000000000000",
        "cancel_flag": "2",
        "oldPassengerStr": name + ",1," + uid + ",1_",
        "passengerTicketStr": type_str + name + ",1," + uid + "," + mobile + ",N",
        "REPEAT_SUBMIT_TOKEN": token,
        "randCode": "",
        "tour_flag": "dc",
        "whatsSelect": "1"
    }
    res = requests.post(url, headers=headers, data=data)
    # print(res.text)


# 提交预订请求
def get_queue_count(train_date, train_no, from_station, to_station, this_code, location):
    url = "https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount"
    train_date = datetime.datetime.strptime(train_date, "%Y-%m-%d").date()
    this_date = train_date.strftime("%a+%b+%d+%Y")
    data = {
        "train_date": this_date,
        "train_no": train_no,
        "stationTrainCode": this_code,
        "seatType": "3",
        "fromStationTelecode": from_station,
        "toStationTelecode": to_station,
        "leftTicket": "",
        "purpose_codes": "00",
        "train_location": location,
        "_json_att": "",
    }
    res = requests.post(url, headers=headers, data=data)
    result = res.text
    return result


# 检查提交状态
def confirm(key_check, left_ticket, passenger_name, passenger_id, passenger_mobile, location, type_id):
    # 商务座，一等座，二等座，软卧，硬卧，硬座
    type_str = ["9,0,1,", "M,0,1,", "O,0,1,", "4,0,1,", "3,0,1,", "1,0,1,"][type_id]
    url = "https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue"
    data = {
        "choose_seats": "",
        "dwAll": "N",
        "key_check_isChange": key_check,
        "leftTicketStr": left_ticket,
        "oldPassengerStr": passenger_name + ",1," + passenger_id + ",1_",
        "passengerTicketStr": type_str + passenger_name + ",1," + passenger_id + "," + passenger_mobile + ",N",
        "purpose_codes": "00",
        "randCode": "",
        "REPEAT_SUBMIT_TOKEN": token,
        "roomType": "00",
        "seatDetailType": "000",
        "train_location": location,
        "whatsSelect": "1",
        "_json_att": "", }
    res = requests.post(url, headers=headers, data=data)
    try:
        js = json.loads(res.text)
        status = js["data"]["submitStatus"]
        # print(status)
        return status
    except Exception as e:
        print(e)
        raise Exception("Confirm Error!")


# 排队等待
def query_order():
    url = "https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime?random=" + str(int(time() * 1000))
    data = {
        "_json_att": "",
        "tourFlag": "dc",
        "REPEAT_SUBMIT_TOKEN": token
    }
    res = requests.post(url, headers=headers, data=data)
    # print(res.text)
    try:
        js = json.loads(res.text)
        order_id = js["data"]["orderId"]
        # print(order_id)
        return order_id
    except Exception as e:
        print(e)
        raise Exception("Query Error!")


# 请求预订结果
def result_order(order_id):
    url = "https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue"
    data = {
        "_json_att": "",
        "orderSequence_no": order_id,
        "REPEAT_SUBMIT_TOKEN": token,
    }
    res = requests.post(url, headers=headers, data=data)
    # print(res.text)


def main():
    global headers

    print("1：模拟登录12306网站...")
    print("-" * 20)
    usr = input("请输入账号：")
    pwd = input("请输入密码：")
    print("正在尝试登录中，请稍等。")
    user = TrainUser(usr, pwd)
    user.login()
    headers = user.headers

    check_result = check_passenger()
    # 检查用户是否登录
    if check_result:
        # 初始化，获取token
        init_dc()
        # print(token)
        # 初始化购票页面
        init_page()

        # 确认用户登录状态
        print("2：确认用户登录状态...")
        print("-" * 20)
        check_user()

        # 查询余票信息
        print("3：查询火车票余票信息...")
        print("-" * 20)
        from_city = input("请输入出发城市：")
        to_city = input("请输入目的城市：")
        train_day = input("请输入日期(如；2019-01-01)：")
        is_gd = True if int(input("是否只看高铁动车(1-是，2-否)：")) == 1 else False
        back_day = datetime.datetime.now()
        back_day = back_day.strftime("%Y-%m-%d")
        tt = TrainTicket(train_day, from_city, to_city, is_gd)
        tt.crawl_ticket()
        the_sort = int(input("请选择车票排序方式(1-最早出发，2-最晚出发，3-耗时最短)：")) - 1
        tt.sort_ticket(the_sort)

        # 输入车票预订信息
        print("4：输入车票预订信息...")
        print("-" * 20)
        tid = input("请输入您想要乘坐的车次名称：")
        if tid[0] == "G" or tid[0] == "D":
            type_id = int(input("请输入座位类别(1-商务座，2-一等座，3-二等座)：")) - 1
        else:
            type_id = int(input("请输入座位类别(1-软卧，2-硬卧，3-硬座)：")) + 2
        train_str = tt.get_ticket(tid)  # 返回该车次的加密字符串
        # print(train_str)

        # 提交预订信息
        print("5：提交车票预订信息...")
        print("-" * 20)
        submit_order(back_date=back_day, purpose_codes="ADULT", from_name=from_city,
                     to_name=to_city, secret=train_str, train_date=train_day)

        # 确认预订信息
        print("6：确认车票预订信息...")
        print("-" * 20)
        html = check_init()
        train_no = re.findall("'train_no':'(.*?)'", html)
        left_ticket_str = re.findall("'leftTicketStr':'(.*?)'", html)
        from_station = re.findall("'from_station_telecode':'(.*?)'", html)
        to_station = re.findall("'to_station_telecode':'(.*?)'", html)
        train_location = re.findall("'train_location':'(.*?)'", html)
        key_check_is_change = re.findall("'key_check_isChange':'(.*?)'", html)
        if len(left_ticket_str):
            left_ticket = left_ticket_str[0]
        else:
            print(html)
            raise Exception("left_ticket_str获取失败！")
        if len(train_location):
            location = train_location[0]
        else:
            print(html)
            raise Exception("train_location获取失败！")
        if len(key_check_is_change):
            key_check = key_check_is_change[0]
        else:
            print(html)
            raise Exception("key_check_is_change获取失败！")

        # 获取乘客信息
        print("7：获取乘客基本信息...")
        print("-" * 20)
        passengers = get_passenger()
        for i in range(len(passengers)):
            print("第{}位乘客：{}".format(i + 1, passengers[i]["passenger_name"]))
        the_no = int(input("请输入乘客序号：")) - 1
        if the_no > len(passengers):
            raise Exception("请输入合法的乘客序号")
        passenger = passengers[the_no]

        # 确认订单信息
        print("8：确认车票订单...")
        print("-" * 20)
        check_order_info(passenger["passenger_name"], passenger["passenger_id_no"], passenger["mobile_no"], type_id)

        # 提交预订请求
        print("9：提交车票订单...")
        print("-" * 20)
        get_queue_count(train_day, train_no, from_station, to_station, tid, location)
        # 检查预订状态
        result = confirm(key_check, left_ticket, passenger["passenger_name"], passenger["passenger_id_no"],
                         passenger["mobile_no"], location, type_id)
        if not result:
            raise Exception("Confirm Error!")

        # 排队等待--直到获取orderid
        print("10：排队等待中，请稍后...")
        print("-" * 20)
        time1 = time()
        the_order_id = ""
        while True:
            time2 = time()
            if int(time2 - time1) == 60:
                print("获取order_id超时！")
                break
            else:
                the_order_id = query_order()
                if the_order_id:
                    print("获取order_id成功！")
                    break
                else:
                    print("获取order_id失败！正在进行新的请求...")
                    sleep(5)

        # 请求预订结果
        print("11：正在请求预订结果... ")
        print("-" * 20)
        result_order(order_id=the_order_id)
        print("抢票成功!")
    else:
        print("请重新登录！")


if __name__ == '__main__':
    main()
