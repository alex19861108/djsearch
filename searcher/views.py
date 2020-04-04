from django.shortcuts import render

# Create your views here.
import json
import requests
from elasticsearch import Elasticsearch
from django.views.generic import View
from django.core.cache import cache

from djsearch import settings
from djsearch.utils import JsonResponse
from crawler.models import Resource


def get_user_permissions(ad_username):
    perm_common = "fCommon"
    if not ad_username:
        return [perm_common]

    permissions = cache.get(ad_username)
    if permissions:
        return permissions

    url = settings.ITM_DOAMIN + "/api/getUserPermissions"
    resp = requests.post(url, json={"userId": ad_username}).json()
    if "success" in resp and resp["success"] is True:
        permissions = [v["name"] for v in resp["data"][ad_username]]
        if perm_common not in permissions:
            permissions.append(perm_common)
        cache.set(ad_username, permissions, settings.CACHE_REDIS_EXPIRE)
        return permissions
    return [perm_common]


class IndicesView(View):
    def get(self, request):
        resources = Resource.objects.filter(deleted=0).order_by('order')
        data = [{"name": item.name, "cn_name": item.cn_name} for item in resources]
        return JsonResponse(data)


class SearchMixin:
    HIGHLIGHT_JOINER = " "
    ABSTRCT_MIN_LENGTH = 5
    ABSTRCT_MAX_LENGTH = 200

    def __init__(self):
        self.conn = Elasticsearch(hosts=settings.BUILDER.get("ES_HOSTS"))
        self.index = ",".join([item.name for item in Resource.objects.filter(deleted=0)])

    def generate_fields(self, index):
        fields = list()
        rows = Resource.objects.filter(name__in=(index.split(",")))
        for row in rows:
            mapping = json.loads(row.mapping)
            for column, attr in mapping.items():
                # index属性的值为true或者不存在index属性时，将当前列名称添加到fields中
                if isinstance(attr, dict) and attr.get("index") is False:
                    continue
                fields.append(column)
        return fields

    def make_conditions(self, permissions):
        result = list()
        for perm in permissions:
            result.append(
                {
                    "match": {
                        "permissions": perm
                    }
                }
            )
        return result

    def make_body(self, wd, fields, **kwargs):
        body = {
            "query": {
                "multi_match": {
                    "query": wd,
                    "type": "best_fields",
                    "fields": fields,
                }
            },

        }
        # 高亮
        body.update(
            {
                "highlight": {
                    "pre_tags": ['<b style="color:red;">'],
                    "post_tags": ['</b>'],
                    "fields": {key: {} for key in fields}
                }
            })
        # 起止
        if 'start' in kwargs.keys():
            kwargs['from'] = kwargs['start']
            del kwargs['start']
        body.update(kwargs)
        return body

    def _search(self, wd, index, **kwargs):
        fields = self.generate_fields(index)

        body = self.make_body(wd, fields, **kwargs)

        result = self.conn.search(index=index, body=body)

        hits = result["hits"]["hits"]
        data = [item["_source"] for item in hits]
        highlight = [item["highlight"] for item in hits if "highlight" in item.keys()]
        if highlight:
            for idx, item in enumerate(data):
                hl = highlight[idx]
                for k, v in hl.items():
                    if k in item.keys():
                        if isinstance(v, list):
                            abstract = SearchMixin.HIGHLIGHT_JOINER.join(v)[:SearchMixin.ABSTRCT_MAX_LENGTH]
                            if len(abstract) >= SearchMixin.ABSTRCT_MIN_LENGTH:
                                item[k] = abstract
                            else:
                                item[k] = item[k][:SearchMixin.ABSTRCT_MAX_LENGTH]
                        else:
                            item[k] = v[:SearchMixin.ABSTRCT_MAX_LENGTH]

        for item in data:
            for k, v in item.items():
                if isinstance(v, str):
                    item[k] = v[:SearchMixin.ABSTRCT_MAX_LENGTH]
        return result["hits"]["total"]["value"], data


class SearchView(SearchMixin, View):
    def get(self, request):
        """
        参数：
        index: 需要检索的索引
        field根据mapping计算出来
        """
        index = request.GET.get("index").replace(" ", "") if request.GET.get("index") else self.index
        wd = request.GET.get("wd", "").strip()
        page = int(request.GET.get("page", 1))
        size = int(request.GET.get("size", 10))
        start = (page - 1) * size

        total, data = self._search(wd, index, start=start, size=size)

        return JsonResponse({
            "total": total,
            "data": data,
            "page": page,
            "size": size
        })


class SugView(SearchMixin, View):
    def get(self, request):
        index = request.GET.get("index", "portal").replace(" ", "")
        if index == "portal":
            return self.portal_suggester(request, index)
        else:
            return self.term_suggester(request, index)

    def make_body(self, wd, fields, **kwargs):
        permissions = kwargs["permissions"]
        del kwargs["permissions"]
        if not permissions:
            body = {
                "query": {
                    "bool": {
                        "must": [{
                            "multi_match": {
                                "query": wd,
                                "type": "best_fields",
                                "fields": fields,
                            }
                        }, {
                            "term": {
                                "deleted": 0
                            }
                        }]
                    }
                },

            }
        else:
            should_conditions = self.make_conditions(permissions)
            body = {
                "query": {
                    "bool": {
                        "must": [{
                            "multi_match": {
                                "query": wd,
                                "type": "best_fields",
                                "fields": fields,
                            }
                        }, {
                            "bool": {
                                "should": should_conditions
                            }
                        }, {
                            "term": {
                                "deleted": 0
                            }
                        }]
                    }
                },
            }
        # 高亮
        body.update(
            {
                "highlight": {
                    "pre_tags": ['<b style="color:red;">'],
                    "post_tags": ['</b>'],
                    "fields": {key: {} for key in fields}
                }
            })
        # 起止
        if 'start' in kwargs.keys():
            kwargs['from'] = kwargs['start']
            del kwargs['start']
        body.update(kwargs)
        return body

    def optimize_level3_refs(self, nodes):
        """
        三级菜单中会存在breadcrumb为空的，需要删除
        :param nodes:
        :return:
        """
        if len(nodes) == 1:
            return nodes

        for idx, node in enumerate(nodes):
            if not node["breadcrumb"]:
                del nodes[idx]
        return nodes

    def portal_suggester(self, request, index="portal"):
        username = request.GET.get("userName", "").strip()
        wd = request.GET.get("wd", "").strip()
        page = int(request.GET.get("page", 1))
        size = int(request.GET.get("size", 10))
        start = (page - 1) * size
        permissions = get_user_permissions(username)

        sort = [
            # {"breadcrumb.title": {"nested": {"path": "breadcrumb"}}}
        ]

        # 产品sug搜索时最多显示10条记录，防止搜索出的内容太多，导致下拉列表太长
        total, data = self._search(wd, index, start=start, size=size, sort=sort, permissions=permissions)

        # 重新排序
        from collections import OrderedDict
        cached_dict = OrderedDict()
        for item in data:
            level1_id = item["breadcrumb"][0]["title"]
            level2_id = item["breadcrumb"][1]["title"]
            if level1_id not in cached_dict.keys():
                cached_dict[level1_id] = OrderedDict()
            if level2_id not in cached_dict[level1_id].keys():
                cached_dict[level1_id][level2_id] = []
            cached_dict[level1_id][level2_id].append(item)

        sorted_data = list()
        for level1_id, level1_group in cached_dict.items():
            for level2_id, level2_group in level1_group.items():
                sorted_data.extend(level2_group)

        # 飘红处理
        for item in sorted_data:
            if len(item["breadcrumb"]) > 2:
                for key, value in item.items():
                    if key != "breadcrumb":
                        item["breadcrumb"][-1][key] = value
        # sorted_data = sorted(data, key=lambda x: (x["breadcrumb"][0]["title"], x["breadcrumb"][1]["title"]))

        # 结果合并成前端展现格式
        level1_children = list()
        level2_children = list()
        level3_children = list()
        last_item = None
        for item in sorted_data:
            if last_item and last_item["breadcrumb"][0]["title"] == item["breadcrumb"][0]["title"]:
                if last_item["breadcrumb"][1] == item["breadcrumb"][1]:
                    level3_children.append({
                        "id": item["id"],
                        "title": item["title"],
                        "url": item["url"],
                        "desc": item["desc"],
                        "deleted": item["deleted"],
                        "permissions": item["permissions"],
                        "breadcrumb": item["breadcrumb"][2:]
                    })
                else:
                    level2_children.append({
                        "id": last_item["breadcrumb"][1]["id"],
                        "title": last_item["breadcrumb"][1]["title"],
                        "url": last_item["breadcrumb"][1]["url"],
                        "desc": last_item["breadcrumb"][1]["desc"],
                        "deleted": last_item["breadcrumb"][1]["deleted"],
                        "permissions": last_item["breadcrumb"][1]["permissions"],
                        # "breadcrumb": last_item["breadcrumb"],
                        "children": self.optimize_level3_refs(level3_children)
                        # "children": level3_children
                    })

                    level3_children = list()
                    level3_children.append({
                        "id": item["id"],
                        "title": item["title"],
                        "url": item["url"],
                        "desc": item["desc"],
                        "deleted": item["deleted"],
                        "permissions": item["permissions"],
                        "breadcrumb": item["breadcrumb"][2:]
                    })
            else:
                if last_item:
                    level2_children.append({
                        "id": last_item["breadcrumb"][1]["id"],
                        "title": last_item["breadcrumb"][1]["title"],
                        "url": last_item["breadcrumb"][1]["url"],
                        "desc": last_item["breadcrumb"][1]["desc"],
                        "deleted": last_item["breadcrumb"][1]["deleted"],
                        "permissions": last_item["breadcrumb"][1]["permissions"],
                        # "breadcrumb": last_item["level2_ref"]["breadcrumb"],
                        "children": self.optimize_level3_refs(level3_children)
                        # "children": level3_children
                    })
                    level1_children.append({
                        "id": last_item["breadcrumb"][0]["id"],
                        "title": last_item["breadcrumb"][0]["title"],
                        "url": last_item["breadcrumb"][0]["url"],
                        "desc": last_item["breadcrumb"][0]["desc"],
                        "deleted": last_item["breadcrumb"][0]["deleted"],
                        "permissions": last_item["breadcrumb"][0]["permissions"],
                        "children": level2_children
                    })
                level2_children = list()
                level3_children = list()
                level3_children.append({
                    "id": item["id"],
                    "title": item["title"],
                    "url": item["url"],
                    "desc": item["desc"],
                    "deleted": item["deleted"],
                    "permissions": item["permissions"],
                    "breadcrumb": item["breadcrumb"][2:]
                })

            last_item = item

        # 处理最后一条记录
        if level3_children:
            level2_children.append({
                "id": last_item["breadcrumb"][1]["id"],
                "title": last_item["breadcrumb"][1]["title"],
                "url": last_item["breadcrumb"][1]["url"],
                "desc": last_item["breadcrumb"][1]["desc"],
                "deleted": last_item["breadcrumb"][1]["deleted"],
                "permissions": last_item["breadcrumb"][1]["permissions"],
                "children": self.optimize_level3_refs(level3_children)
                # "children": level3_children
            })
            level1_children.append({
                "id": last_item["breadcrumb"][0]["id"],
                "title": last_item["breadcrumb"][0]["title"],
                "url": last_item["breadcrumb"][0]["url"],
                "desc": last_item["breadcrumb"][0]["desc"],
                "deleted": last_item["breadcrumb"][0]["deleted"],
                "permissions": last_item["breadcrumb"][0]["permissions"],
                "children": level2_children
            })

        return JsonResponse({
            "total": total,
            "data": level1_children,
            "page": page,
            "size": size
        })

    def completion_suggester(self, request, index, size=20):
        wd = request.GET.get("wd", "").strip()
        fields = self.generate_fields(index)
        body = {
            "suggest": {
                "sug": {
                    "prefix": wd,
                    "completion": {
                        "field": "title.suggest",
                        "size": size,
                        "skip_duplicates": True,
                        "fuzzy": {
                            "fuzziness": 2
                        }
                    }
                }
            }
        }

        result = self.conn.search(index=index, body=body)
        data = list()
        for sug in result["suggest"]["sug"]:
            for opt in sug["options"]:
                data.append(opt["text"])

        return JsonResponse({
            "total": result["hits"]["total"]["value"],
            "data": data
        })

    def phrase_suggester(self, request, index, size=5):
        wd = request.GET.get("wd", "").strip()
        field = "title"
        body = {
            "suggest": {
                "sug": {
                    "text": wd,
                    "phrase": {
                        "field": field,
                        "size": size,
                        "highlight": {
                            "pre_tag": "<em>",
                            "post_tag": "</em>"
                        }
                    }
                }
            }
        }
        result = self.conn.search(index=index, body=body)
        data = list()
        for sug in result["suggest"]["sug"]:
            for opt in sug["options"]:
                data.append(opt["text"])

        return JsonResponse({
            "total": result["hits"]["total"]["value"],
            "data": data
        })

    def term_suggester(self, request, index, size=10):
        wd = request.GET.get("wd", "").strip()
        field = "content"
        body = {
            "suggest": {
                "sug": {
                    "text": wd,
                    "term": {
                        "suggest_mode": "popular",
                        "min_word_length": 2,
                        "field": field,
                        "size": size,
                        "string_distance": "ngram"
                    }
                }
            }
        }
        result = self.conn.search(index=index, body=body)
        data = list()
        for sug in result["suggest"]["sug"]:
            for opt in sug["options"]:
                data.append(opt["text"])

        return JsonResponse({
            "total": result["hits"]["total"]["value"],
            "data": data
        })
