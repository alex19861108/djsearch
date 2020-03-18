from django.shortcuts import render
import requests
import json

from crawler.models import Resource
from djsearch.utils import JsonResponse

# Create your views here.


def mock_get_app(request):
    from crawler.mock import mock_portal
    return JsonResponse(json.loads(mock_portal))


def translate_dct(dct, trans_map):
    """ 不在变换字典中的值会被舍弃 """
    result = dict()
    for key, value in dct.items():
        if key in trans_map.keys():
            result[trans_map[key]] = value
        # else:
        #     result[key] = value
    return result


def translate(lst, trans_map):
    if trans_map is None:
        return lst

    result = list()
    for dct in lst:
        result.append(translate_dct(dct, trans_map))
    return result


def api_portal(request):
    page = int(request.GET.get("page", 1))
    size = int(request.GET.get("size", 10))

    portal = Resource.objects.filter(name="portal").first()
    if not portal:
        return JsonResponse({
            "status": -1,
            "message": "there's no resource named portal",
            "data": ""
        })

    pre_action = json.loads(portal.config).get("pre_action")
    site_api = pre_action.get("api")

    response = requests.get(site_api).json()

    # from apps.crawler.mock import mock_portal
    # response = mock_portal
    data = translate(response.get("data"), pre_action.get("translate", None))

    result = {
        "total": len(data),
        "page": page,
        "size": size,
        "data": data
    }
    return result

