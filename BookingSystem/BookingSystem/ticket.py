from BookingSystem.settings import *


class TrainTicket:
    def __init__(self, day, fr, to, gd=True):
        # 请求保存列车站点代码的链接
        res1 = requests.get("https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9098")
        # 把分割处理后的车站信息保存在station_data中
        self.station_data = res1.text.replace("var station_names ='", '').rstrip("'").split('@')
        self.station_data = self.station_data[1:-1]
        self.day = day
        self.the_day = '/'.join([str(int(i)) for i in day.split('-')])
        self.fr = self.get_station(fr)
        self.to = self.get_station(to)
        self.gd = gd  # 只看高铁动车
        self.data_list = []

    def crawl_ticket(self):
        """
        获取火车票余票信息
        :return:
        """
        url = "https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}" \
              "&leftTicketDTO.to_station={}&purpose_codes=ADULT".format(self.day, self.fr, self.to)
        res2 = requests.get(url)
        result = json.loads(res2.text)['data']['result']
        seat_data = [(32, "商务座"), (31, "一等座"), (30, "二等座"), (26, "无座"), (23, "软卧"), (28, "硬卧"), (29, "硬座")]

        for i in result:
            data = {
                "str": i.split('|')[0],
                "info": {}
            }
            i = i.split('|')
            if i[13] == ''.join(self.day.split('-')) and i[8] != i[9]:
                data['info'] = {
                    "车次": i[3], "出发日期": i[13], "始发站": self.get_city(i[4]), "终点站": self.get_city(i[5]),
                    "出发站": self.get_city(i[6]), "目的站": self.get_city(i[7]), "出发时间": i[8], "到达时间": i[9],
                    "总耗时": str(int(i[10][:i[10].index(":")])) + "小时" + str(int(i[10][i[10].index(":") + 1:])) + "分钟",
                    "商务座": '', "一等座": '', "二等座": '', "无座": '', "软卧": '', "硬卧": '', "硬座": ''
                }
                for j in range(7):
                    if i[seat_data[j][0]] == "有" or i[seat_data[j][0]].isdigit():
                        data['info'][seat_data[j][1]] = i[seat_data[j][0]]
                    else:
                        data['info'][seat_data[j][1]] = "-"
                self.data_list.append(data)

    def sort_ticket(self, sort_id=0):
        """
        对火车票余票进行排序然后打印出来
        :param sort_id: 排序方式：0-按时间从早到晚排序 1-按时间从晚到早排序 2-按耗时排序
        :return:
        """
        if sort_id == 0:
            self.show_ticket([i["info"] for i in self.data_list])
        elif sort_id == 1:
            self.show_ticket([i["info"] for i in self.data_list[::-1]])
        elif sort_id == 2:
            lst = [i["info"] for i in self.data_list]
            for i in lst:
                i["time"] = int(i["总耗时"].split("小时")[0])*60 + int(i["总耗时"].split("小时")[1].rstrip("分钟"))
            self.show_ticket(sorted(lst, key=lambda x: x["time"]))

    def show_ticket(self, data_list):
        """
        打印火车票余票信息
        :param data_list:
        :return:
        """
        if self.gd:
            print("%-6s%-10s%-6s%-6s%-6s%-8s%-8s%-5s%-5s%-5s"
                  % ("车次", "出发日期", "出发站", "目的站", "出发时间", "到达时间", "总耗时", "商务座", "一等座", "二等座"))
        else:
            print("%-6s%-10s%-6s%-6s%-6s%-8s%-8s%-5s%-5s%-5s%-4s%-4s%-4s%-4s"
                  % ("车次", "出发日期", "出发站", "目的站", "出发时间", "到达时间", "总耗时", "商务座", "一等座", "二等座", "无座", "软卧", "硬卧", "硬座"))
        for data in data_list:
            if self.gd:
                if data["车次"][0] == "G" or data["车次"][0] == "D":
                    print("%-7s%-13s%-5s\t%-3s\t%-9s%-9s%-10s%-7s%-7s%-7s"
                          % (data["车次"], self.the_day, data["出发站"], data["目的站"], data["出发时间"],
                             data["到达时间"], data["总耗时"], data["商务座"], data["一等座"], data["二等座"]))
            else:
                print("%-7s%-13s%-5s\t%-3s\t%-9s%-9s%-10s%-7s%-7s%-7s%-5s%-5s%-5s%-5s"
                      % (data["车次"], self.the_day, data["出发站"], data["目的站"], data["出发时间"], data["到达时间"],
                         data["总耗时"], data["商务座"], data["一等座"], data["二等座"], data["无座"], data["软卧"],
                         data["硬卧"], data["硬座"]))

    # 返回车站英文缩写
    def get_station(self, city):
        for i in self.station_data:
            if city == i.split('|')[1]:
                return i.split('|')[2]

    # 返回车站中文缩写
    def get_city(self, station):
        for i in self.station_data:
            if station == i.split('|')[2]:
                return i.split('|')[1]

    # 根据选择的车次返回对应车次数据
    def get_ticket(self, tid):
        for data in self.data_list:
            if data['info']['车次'] == tid:
                return parse.unquote(data['str'])


if __name__ == '__main__':
    tt = TrainTicket("2019-06-30", "武汉", "上海", True)
    tt.crawl_ticket()
    the_sort = int(input("请选择车票排序方式(1-最早出发，2-最晚出发，3-耗时最短)：")) - 1
    tt.sort_ticket(the_sort)
