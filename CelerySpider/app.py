from celery import Celery


app = Celery("spiders", include=["CelerySpider.tasks"])
# 导入配置文件
app.config_from_object("CelerySpider.celeryconfig")


if __name__ == '__main__':
    app.start()
