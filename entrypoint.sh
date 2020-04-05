#!/bin/bash

# 启动flower
flower -A djsearch --broker=redis://:111111@128.196.245.160:30017/12 &

# 启动celery beat
celery -A djsearch beat --detach

# 启动worker Windows
# celery -A djsearch worker -l info -P eventlet

# 启动worker Linux
celery -A djsearch worker -l info --detach

# 启动django
uwsgi --ini conf/uwsgi.ini
