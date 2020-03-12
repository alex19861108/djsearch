#!/bin/sh

WORKPATH=$(cd $(dirname ${BASH_SOURCE:-$0});pwd)
HOMEPATH=$(dirname $WORKPATH)
MODULE_NAME="djsearch"
VERSION="0.1"
docker build -f $HOMEPATH/Dockerfile -t $MODULE_NAME:$VERSION $HOMEPATH
