#FROM docker.caas.dev.jh/basic/python:3.7.5
FROM rackspacedot/python37:latest
MAINTAINER liuwei.bj@ccbft.com

RUN mkdir -p /home/work

COPY ./ /home/work

RUN pip install -r conf/requirements.txt

EXPOSE 8000

WORKDIR /home/work/
CMD ["uwsgi", "conf/uwsgi.ini"]