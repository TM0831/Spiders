# 使用Redis作为消息代理
BROKER_URL = "redis://localhost:6379/1"
# 使用Redis存储结果
CELERY_RESULT_BACKEND = "redis://localhost:6379/2"
# 设定时区
CELERY_TIMEZONE = 'Asia/Shanghai'
# 任务的序列化方式
CELERY_TASK_SERIALIZER = 'json'
# 任务执行结果的序列化方式
CELERY_RESULT_SERIALIZER = 'json'
