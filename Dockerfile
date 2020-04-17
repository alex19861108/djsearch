# FROM docker.caas.dev.jh/basic/python:3.7.5
FROM python:3.8.2
MAINTAINER liuwei.bj@ccbft.com

RUN mkdir -p /home/work/djsearch

COPY ./ /home/work/djsearch

WORKDIR /home/work/djsearch

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r conf/requirements.txt
# RUN pip install -i http://128.196.0.125:8081/repository/Pypi_Group_bjkfzx/simple/ --trusted-host 128.196.0.125 pip=20.0.2 -U \
#     && pip config set global.index-url http://128.196.0.125:8081/repository/Pypi_Group_bjkfzx/simple/ \
#     && pip config set global.timeout 6000 \
#     && pip config set install.trusted-host 128.196.0.125 \
#     && pip install -r conf/requirements.txt

RUN sed -i '36,37d' /usr/local/lib/python3.8/site-packages/django/db/backends/mysql/base.py

EXPOSE 8000
EXPOSE 5555

# CMD ["uwsgi", "--ini", "conf/uwsgi.ini"]
ENTRYPOINT ["sh", "/home/work/djsearch/entrypoint.sh"]
