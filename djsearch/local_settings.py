"""
@Author         :  liuwei
@Version        :  
------------------------------------
@File           :  local_settings.py
@Description    :  
@CreateTime     :  2020/3/12 16:30
"""
#############################
# system settings
#############################
from kombu import Exchange, Queue

ALLOWED_HOSTS = ['*']
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'search',
#         'USER': 'root',
#         'PASSWORD': '123456',
#         'HOST': 'localhost',
#         'PORT': '3306',
#     }
# }

#############################
# third party app settings
#############################
# sentry
SENTRY_DSN = "http://cb1b4f982c7142dab41c1324ab3d7459@localhost:9000/3"


#############################
# my app settings
#############################
BUILDER = {
    "ES_HOSTS": ["http://62.234.146.101:9200"]
}

#############################
# celery setting.
#############################
from datetime import timedelta
from celery.schedules import crontab
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ENABLE_UTC = True

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACKS_LATE = True
CELERYD_FORCE_EXECV = True
CELERYD_MAX_TASKS_PER_CHILD = 100
CELERYD_TASK_TIME_LIMIT = 12*30

CELERY_BROKER_URL = 'redis://127.0.0.1:6379/1'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/1'
# CELERY_CACHE_BACKEND = 'django-cache'

CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'
CELERY_BEAT_SCHEDULE = {
    'build every day': {
        'task': 'builder.tasks.build',
        'schedule': crontab(minute=0, hour=0),
        # 'schedule': timedelta(days=1),
        # 'args': (1, 2)
    }
}

# CELERY_QUEUES = (
#     Queue('celery', Exchange('celery'), routing_key='celery'),
# )
#
# CELERY_ROUTES = {
#     'builder.tasks.add': {'queue': 'celery', 'routing_key': 'celery'},
# }

# CELERY_IMPORTS = (
#     'builder.tasks'
# )
