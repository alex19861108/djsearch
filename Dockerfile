#FROM docker.caas.dev.jh/basic/python:3.7.5
FROM rackspacedot/python37:latest
MAINTAINER liuwei.bj@ccbft.com

RUN mkdir -p /home/work/djsearch

COPY ./ /home/work/djsearch

WORKDIR /home/work/djsearch

RUN pip install -r conf/requirements.txt

EXPOSE 8000

CMD ["uwsgi", "--ini", "conf/uwsgi.ini"]
