#!/usr/bin/env sh
WORKPATH=$(cd $(dirname ${BASH_SOURCE:-$0});pwd)
HOMEPATH=$(dirname $WORKPATH)
LOGPATH=$HOMEPATH/log

[ ! -d $LOGPATH ] && mkdir -p $LOGPATH

HOST="0.0.0.0"
PORT="8000"

mode=$@
if [ "X$mode" == "Xrunserver" ]; then
	docker run -p $PORT:$PORT djsearch:0.1
else
	nohup venv/bin/uliweb runserver -h ${HOST} -p ${PORT} 1>$LOGPATH/log.stdout 2>&1 &
