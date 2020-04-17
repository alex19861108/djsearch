"""
@Author         :  liuwei
@Version        :  0.0.1
------------------------------------
@File           :  build_index.py
@Description    :  
@CreateTime     :  2020/3/14 19:26
"""
import base64
import requests
import datetime
import json
import math
import logging
import traceback
from elasticsearch import Elasticsearch, TransportError
from crawler.models import Resource
from djsearch import settings

log = logging.getLogger(__name__)


class IndexBuilder:
    def __init__(self):
        self.conn = Elasticsearch(hosts=settings.BUILDER.get("ES_HOSTS"))

    def load_resource(self, obj):
        """
        资源入库
        """
        log.info("loading resource [{}]...".format(obj.name))
        config = json.loads(obj.config)

        # 数据存储在ES的索引
        index = obj.name
        # index对应的mapping
        mapping = json.loads(obj.mapping)

        # 建index，建mapping
        if not self.conn.indices.exists(index):
            # self.conn.indices.create(index, mapping)
            self.conn.indices.create(index, {"mappings": {"properties": mapping}})

        # 组装要抓取的url
        crawler_apis = config.get("crawler_apis")
        for api_name, api_url in crawler_apis.items():
            self._load_resource(api_name, api_url, index)

    def _load_resource(self, api_name, api_url, index):
        # 数据入库
        is_last_page = False
        page = 1
        while is_last_page is False:
            fetch_url = api_url.format(page)
            # 根据api抓取数据
            log.info("[builder.load_resource]: {}".format(fetch_url))
            response = requests.get(fetch_url)
            if response.status_code != 200:
                log.error("[builder.load_resource]: {}, status_code: {}".format(fetch_url, response.status_code))
                break

            # from crawler.mock import mock_portal
            # resp_data = json.loads(mock_portal)
            resp_dict = json.loads(response.text)
            data = resp_dict.get("data")

            # 获取下一页的页码
            size, page, total = int(resp_dict.get("size")), int(resp_dict.get("page")), int(resp_dict.get("total"))
            is_last_page = page == math.ceil(total / size)
            page += 1

            # 解析api返回的数据
            for document in data:
                # 主键
                # id = document.get("id")
                id = base64.urlsafe_b64encode("{}@{}".format(api_name, document.get("id")).encode("utf-8"))
                # 删除标记
                if self.conn.exists(index, id) is True:
                    if document.get("deleted", None):
                        self.conn.delete(index, id)
                    else:
                        self.conn.update(index, id=id, body={"doc": document})
                else:
                    self.conn.index(index, document, id=id)

    def build_all(self):
        for row in Resource.objects.filter(enable_build=True):
            try:
                self.load_resource(row)
            except Exception as e:
                traceback.print_exc(e)
                return False
        return True

    def build(self, index):
        row = Resource.objects.filter(enable_build=True).filter(name=index).first()
        try:
            self.load_resource(row)
        except Exception as e:
            traceback.print_exc(e)
            return False
        return True

    def reindex(self, index):
        index_old = "{}_old.{}".format(index, datetime.date.today())
        index_new = "{}_new.{}".format(index, datetime.date.today())
        body = {
            "source": {
                "index": index
            },
            "dest": {
                "index": index_new
            }
        }
        self.conn.reindex(body=body)

        body = {
            "actions": [
                {
                    "remove": {
                        "index": index,
                        "alias": index_old
                    }
                },
                {
                    "add": {
                        "index": index_new,
                        "alias": index
                    }
                }
            ]
        }
        try:
            return self.conn.transport.perform_request("POST", "/_alias", body=body)
        except TransportError:
            return False
