import os

from celery import Celery

# 为celery运行设置django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_market.settings')

# main: 脚本路径
app = Celery(main="celery_handler")

app.config_from_object("celery_handler.config")

app.autodiscover_tasks(['celery_handler.sms', 'celery_handler.email'])

