#!/usr/bin/env sh
WORKPATH=$(cd $(dirname ${BASH_SOURCE:-$0});pwd)
PORT="8000"
ps aux | grep "uwsgi" | grep -v "grep" | awk '{print $2}' | xargs kill -9
