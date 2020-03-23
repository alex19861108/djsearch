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
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/1'
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_BEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
