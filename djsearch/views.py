"""
@Author         :  liuwei
@Version        :  0.0.1
------------------------------------
@File           :  views.py
@Description    :  
@CreateTime     :  2020/3/12 15:56
"""
from djsearch.utils import JsonResponse


def health(request):
    return JsonResponse({
        "status": 0,
        "message": "OK",
        "data": []
    })
