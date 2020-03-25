"""
@Author         :  liuwei
@Version        :  0.0.1
------------------------------------
@File           :  build_index.py
@Description    :  
@CreateTime     :  2020/3/14 19:26
"""
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
            self.conn.indices.create(index, {"mappings": {"properties": mapping}})

        # 数据入库
        is_last_page = False
        page = 1
        while is_last_page is False:
            # 组装要抓取的url
            crawler_api = config.get("api").format(page)

            # 根据api抓取数据
            log.info("[builder.load_resource]: {}".format(crawler_api))
            response = requests.get(crawler_api).json()

            # from crawler.mock import mock_portal, mock_forumpost, mock_wiki
            # if index == "portal":
            #     mock_response = mock_portal
            # elif index == "forumpost":
            #     mock_response = mock_forumpost
            # elif index == "wiki":
            #     mock_response = mock_wiki
            # response = json.loads(mock_response)
            data = response.get("data")

            # 获取下一页的页码
            size, page, total = response.get("size"), response.get("page"), response.get("total")
            is_last_page = page == math.ceil(total / size)
            page += 1

            # 解析api返回的数据
            for document in data:
                # 文档内容
                # document = json.dumps(item)
                # 主键
                id = document.get("id")
                # 删除标记
                if self.conn.exists(index, id) is True:
                    if document.get("deleted", None):
                        self.conn.delete(index, id)
                    else:
                        self.conn.update(index, id=id, body={"doc": document})
                else:
                    self.conn.index(index, document, id=id)

    def build_all(self):
        for row in Resource.objects.filter(deleted=0):
            try:
                self.load_resource(row)
            except Exception as e:
                traceback.print_exc(e)

    def build(self, index):
        row = Resource.objects.filter(deleted=0).filter(name=index).first()
        self.load_resource(row)

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

        #
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
