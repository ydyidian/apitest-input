# coding=utf8

# ＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊
#
# @Author: yiciu
# @Version: 1.0
# @Date: 2022/04/11 13:50 | 周一
# @Desc:
#
# ＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊


import time
from enum import Enum

from common.logging.logger import Logger
from common.settings import Settings
from elasticsearch import Elasticsearch

logger = Logger(__name__)


class ElasticIndex(Enum):
    SCRIPT_INFO = "tb_script_info"


class ElasticPool(object):

    CONNECTION_MAP = Settings.CONFIG.get("es", {})  # 加载数据库连接信息字典

    client_cache = {}

    @classmethod
    def get_client(cls, alias="normal"):
        """
        获取连接
        :param alias: 数据库连接别名「从配置信息中获取」, 默认值: "normal"
        :return:
        """
        conn_info = cls.CONNECTION_MAP[alias]
        username, password, host, port = (
            conn_info["user"],
            conn_info["password"],
            conn_info["host"],
            conn_info["port"],
        )
        k = f"{username}^{password}^{host}^{port}"
        client = cls.client_cache.get(k)

        if client is not None:
            return client
        else:
            client = Elasticsearch(f"http://{host}:{port}", basic_auth=(username, password))
            cls.client_cache[k] = client
            return client

    @classmethod
    def wait_for_exist(
        cls, alias="normal", body=None, index=None, doc_type=None, params=None, headers=None, timeout=5000
    ):
        client = cls.get_client(alias)
        hits, res = 0, []
        unit, cnt = 500, 0
        start = time.time()
        while not hits and unit * cnt < timeout:
            hits, res = cls.get_hits_info_from_result(
                client.search(body, index, doc_type, params=params, headers=headers)
            )
            cnt += 1
            time.sleep(0.5)
        if unit * cnt >= timeout:
            raise TimeoutError("查询超时···")
        logger.info(f"es查询耗时：{time.time() - start:.2f}s，匹配到{hits}条记录")
        return hits, res

    @classmethod
    def wait_for_not_exist(
        cls, alias="normal", body=None, index=None, doc_type=None, params=None, headers=None, timeout=5000
    ):
        client = cls.get_client(alias)
        hits, res = 1, []
        unit, cnt = 500, 0
        start = time.time()
        while hits and unit * cnt < timeout:
            hits, res = cls.get_hits_info_from_result(
                client.search(body, index, doc_type, params=params, headers=headers)
            )
            cnt += 1
            time.sleep(0.5)
        if unit * cnt >= timeout:
            raise TimeoutError("时间超时，数据依旧存在···")
        logger.info(f"es查询耗时：{time.time() - start:.2f}s，数据已清理！")
        return hits, res

    @staticmethod
    def get_hits_info_from_result(query_result: dict):
        """
        从查询结果中获取命中数以及查询列表
        :param query_result: es查询返回
        :return: 命中数以及查询列表
        """
        return query_result["hits"]["total"]["value"], query_result["hits"]["hits"]


if __name__ == "__main__":
    connection = Elasticsearch("http://10.1.20.3:9200", basic_auth=("aaa", "aaa"))
    print(connection.info())
    print(
        connection.search(
            index="tb_script_info",
            body={"query": {"bool": {"must": [{"term": {"albumId": {"value": "A20180724160331561001573"}}}]}}},
        )
    )
