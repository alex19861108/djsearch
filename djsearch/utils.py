"""
@Author         :  liuwei
@Version        :  
------------------------------------
@File           :  utils.py
@Description    :  
@CreateTime     :  2020/3/7 22:08
"""
import json
from django.http import HttpResponse


def JsonResponse(d: object) -> object:
    return HttpResponse(json.dumps(d, ensure_ascii=False), content_type="application/json,charset=utf-8")
