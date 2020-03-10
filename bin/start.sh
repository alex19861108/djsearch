#!/usr/bin/env sh
WORKPATH=$(cd $(dirname ${BASH_SOURCE:-$0});pwd)
HOST="0.0.0.0"
PORT="8000"
nohup venv/bin/uliweb runserver -h ${HOST} -p ${PORT} 1>log.stdout 2>&1 &
