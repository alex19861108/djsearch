"""
@Author         :  liuwei
@Version        :  
------------------------------------
@File           :  local_settings.py
@Description    :  
@CreateTime     :  2020/3/12 16:30
"""
ALLOWED_HOSTS = ['*']
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'

# ============== third party app settings ==============
SENTRY_DSN = "http://cb1b4f982c7142dab41c1324ab3d7459@localhost:9000/3"

# ============== my app settings ==============
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'search',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

BUILDER = {
    "ES_HOSTS": ["http://62.234.146.101:9200"]
}
