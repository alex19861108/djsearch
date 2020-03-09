from django.shortcuts import render

# Create your views here.
import json
from elasticsearch import Elasticsearch
from django.views.generic import View

from djsearch import settings
from djsearch.utils import JsonResponse
from crawler.models import Resource


class IndicesView(View):
    def get(self, request):
        resources = Resource.objects.filter(deleted=0).order_by('order')
        data = [{"name": item.name, "cn_name": item.cn_name} for item in resources]
        return JsonResponse(data)


class SearchMixin:
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

    def _search(self, wd, index, **kwargs):
        fields = self.generate_fields(index)
        body = {
            "query": {
                "multi_match": {
                    "query": wd,
                    "fields": fields,
                }
            },
            "highlight": {
                "pre_tags": ['<b style="color:red;">'],
                "post_tags": ['</b>'],
                "fields": {key: {} for key in fields}
            }
        }
        if 'start' in kwargs.keys():
            kwargs['from'] = kwargs['start']
            del kwargs['start']
        body.update(kwargs)

        result = self.conn.search(index=index, body=body)

        hits = result["hits"]["hits"]
        data = [item["_source"] for item in hits]
        highlight = [item["highlight"] for item in hits if hasattr(item, "highlight")]
        if highlight:
            for idx, item in enumerate(data):
                hl = highlight[idx]
                for k, v in hl.items():
                    if k in item.keys():
                        if isinstance(v, list):
                            item[k] = "...".join(v)
                        else:
                            item[k] = v
        return result["hits"]["total"]["value"], data


class SearchView(SearchMixin, View):
    def get(self, request):
        """
        参数：
        index: 需要检索的索引
        field根据mapping计算出来
        """
        index = request.GET.get("index").replace(" ", "") if request.GET.get("index") else self.index
        wd = request.GET.get("wd", "")
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

    def portal_suggester(self, request, index="portal"):
        wd = request.GET.get("wd", "")
        page = int(request.GET.get("page", 1))
        size = int(request.GET.get("size", 1000))
        start = (page - 1) * size

        sort = [
            {"level1_ref.title": {"nested": {"path": "level1_ref"}}},
            {"level2_ref.title": {"nested": {"path": "level2_ref"}}}
        ]
        total, data = self._search(wd, index, start=start, size=size, sort=sort)

        level1_children = list()
        level2_children = list()
        level3_children = list()
        last_item = None
        for item in data:
            if last_item and last_item["level1_ref"]["title"] == item["level1_ref"]["title"]:
                if last_item["level2_ref"] == item["level2_ref"]:
                    level3_children.append({
                        "name": item["name"],
                        "url": item["url"],
                        "title": item["title"],
                        "desc": item["desc"],
                        "breadcrumb": item["breadcrumb"]
                    })
                else:
                    level2_children.append({
                        "name": last_item["level2_ref"]["name"],
                        "url": last_item["level2_ref"]["url"],
                        "title": last_item["level2_ref"]["title"],
                        "desc": last_item["level2_ref"]["desc"],
                        # "breadcrumb": last_item["breadcrumb"],
                        "children": level3_children
                    })
                    level3_children = list()
                    level3_children.append({
                        "name": item["name"],
                        "url": item["url"],
                        "title": item["title"],
                        "desc": item["desc"],
                        "breadcrumb": item["breadcrumb"]
                    })
            else:
                if last_item:
                    level2_children.append({
                        "name": last_item["level2_ref"]["name"],
                        "url": last_item["level2_ref"]["url"],
                        "title": last_item["level2_ref"]["title"],
                        "desc": last_item["level2_ref"]["desc"],
                        # "breadcrumb": last_item["level2_ref"]["breadcrumb"],
                        "children": level3_children
                    })
                    level1_children.append({
                        "name": last_item["level1_ref"]["name"],
                        "url": last_item["level1_ref"]["url"],
                        "title": last_item["level1_ref"]["title"],
                        "desc": last_item["level1_ref"]["desc"],
                        "children": level2_children
                    })
                level2_children = list()
                level3_children = list()
                level3_children.append({
                    "name": item["name"],
                    "url": item["url"],
                    "title": item["title"],
                    "desc": item["desc"],
                    "breadcrumb": item["breadcrumb"]
                })

            last_item = item

        # 处理最后一条记录
        if level3_children:
            level2_children.append({
                "name": last_item["level2_ref"]["name"],
                "url": last_item["level2_ref"]["url"],
                "title": last_item["level2_ref"]["title"],
                "desc": last_item["level2_ref"]["desc"],
                "children": level3_children
            })
            level1_children.append({
                "name": last_item["level1_ref"]["name"],
                "url": last_item["level1_ref"]["url"],
                "title": last_item["level1_ref"]["title"],
                "desc": last_item["level1_ref"]["desc"],
                "children": level2_children
            })

        return JsonResponse({
            "total": total,
            "data": level1_children,
            "page": page,
            "size": size
        })

    def completion_suggester(self, request, index, size=20):
        wd = request.GET.get("wd", "")
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
        wd = request.GET.get("wd", "")
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

    def term_suggester(self, request, index, size=5):
        wd = request.GET.get("wd", "")
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
