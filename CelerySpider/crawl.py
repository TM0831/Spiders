import time
from CelerySpider.tasks import main


start_time = time.time()


url_list = ["https://www.doutula.com/article/list/?page={}".format(i) for i in range(1, 31)]
res = main.delay(url_list)
all_src = []
for i in res.collect():
    if isinstance(i[1], list) and isinstance(i[1][0], str):
        all_src.extend(i[1])

print("Src count: ", len(all_src))


end_time = time.time()
print("Cost time: ", end_time - start_time)
