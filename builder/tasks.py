"""
@Author         :  liuwei
@Version        :  
------------------------------------
@File           :  tasks.py
@Description    :  
@CreateTime     :  2020/3/22 21:33
"""

from __future__ import absolute_import, unicode_literals

from celery import shared_task
from builder.index_builder import IndexBuilder


@shared_task
def build():
    return IndexBuilder().build()


@shared_task
def add(x, y):
    return x + y
