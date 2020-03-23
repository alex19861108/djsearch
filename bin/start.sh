#!/usr/bin/env sh
WORKPATH=$(cd $(dirname ${BASH_SOURCE:-$0});pwd)
HOMEPATH=$(dirname $WORKPATH)
CONFIGPATH="$HOMEPATH/conf"
LOGPATH=$HOMEPATH/log

[ ! -d $LOGPATH ] && mkdir -p $LOGPATH

HOST="0.0.0.0"
PORT="8000"

mode=$@
if [ "X$mode" == "Xdocker" ]; then
	docker run -p $PORT:$PORT djsearch:0.1
else
	nohup $HOMEPATH/venv/bin/uwsgi --ini $CONFIGPATH/uwsgi.ini 1>$LOGPATH/log.stdout 2>&1 &
	# flower -A djsearch --broker=redis://127.0.0.1:6379/1
	# celery -A djsearch worker -l info -P eventlet
fi
