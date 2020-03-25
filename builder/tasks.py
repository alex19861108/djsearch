"""
@Author         :  liuwei
@Version        :  
------------------------------------
@File           :  tasks.py
@Description    :  
@CreateTime     :  2020/3/22 21:33
"""

from __future__ import absolute_import, unicode_literals
import logging

from celery import shared_task
from djsearch.celery import app
from builder.index_builder import IndexBuilder

log = logging.getLogger(__name__)


@shared_task
def build_all():
    return IndexBuilder().build_all()


@shared_task
def add(x, y):
    log.info("receive shared_task, function [add]")
    return x + y
