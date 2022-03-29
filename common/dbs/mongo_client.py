# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2022/03/25 17:34
@Desc: Mongo数据库查询
"""


from urllib import parse

import pymongo
from common.settings import Settings


class MongoPool(object):

    CONNECTION_MAP = Settings.CONFIG.get("mongodb", {})  # 加载数据库连接信息字典
    SEARCH_MAP = {
        "0": "nzero",
        "1": "nnone",
        "2": "ntwo",
        "3": "nthree",
        "4": "nfour",
        "5": "nfive",
        "6": "nsix",
        "7": "nseven",
        "8": "neight",
        "9": "nnine",
    }

    client_cache = {}

    def __init__(self, read_preference="secondaryPreferred"):
        """
        实例化MongoConn(后续创建连接，会去调用test_x_config.yml里面的配置)
        *** 配置文件中search在1和3中对应的名称不同
        :param read_preference: 读取方式，默认优先从节点读取
        """
        # self.user = user if user else config.get_MongoDB('user')
        # self.host = host if host else config.get_MongoDB('host')
        # self.password = password if password else config.get_MongoDB('pwd')
        # self.port = port if port else config.get_MongoDB('port')
        # uri = f"mongodb://{parse.quote_plus(self.user)}:{parse.quote_plus(self.password)}@{self.host}:{self.port}/"
        # k = f"{self.user}^{self.password}^{self.host}^{self.port}"
        # client = self.client_cache.get(k)
        # if client is not None:
        #     self._client = client
        # else:
        #     self._client = pymongo.MongoClient(uri, readpreference=read_preference)
        #     self.client_cache[k] = client
        self._client = None
        self._read_preference = read_preference

    def get_collection(self, database, collection):
        """
        切换集合
        :param database: 数据库名
        :param collection: 集合名称
        :return: 连接信息
        """

        conn_info = self.CONNECTION_MAP[database]
        username, password, host, port = (
            conn_info["username"],
            conn_info["password"],
            conn_info["host"],
            conn_info["port"],
        )
        k = f"{username}^{password}^{host}^{port}"
        client = MongoPool.client_cache.get(k)

        if client is not None:
            self._client = client
        else:
            uri = f"mongodb://{parse.quote_plus(username)}:{parse.quote_plus(password)}@{host}:{port}/"
            self._client = pymongo.MongoClient(uri, readpreference=self._read_preference)
            MongoPool.client_cache[k] = self._client

        db = conn_info["database"]
        return self._client[db][collection]

    def insert(
        self, database, collection, doc_or_docs, manipulate=True, check_keys=True, continue_on_error=False, **kwargs
    ):
        """
        插入文档
        :param database: 数据库名称
        :param collection: 集合名称
        :param doc_or_docs:
        :param manipulate:
        :param check_keys:
        :param continue_on_error:
        :param kwargs:
        :return:
        """
        coll = self.get_collection(database, collection)
        return coll.insert(doc_or_docs, manipulate, check_keys, continue_on_error, **kwargs)

    def find(self, database, collection, *args, **kwargs):
        """
        查询文档
        :param database: 数据库名称
        :param collection: 集合名称
        :param args:
        :param kwargs:
        :return: 查询结果
        """
        coll = self.get_collection(database, collection)
        return coll.find(*args, **kwargs)

    def find_one(self, database, collection, filterer, *args, **kwargs):
        """
        查询单条文档
        :param database: 数据库名称
        :param collection: 集合名称
        :param filterer: 查询条件
        :param args:
        :param kwargs:
        :return: 查询结果
        """
        coll = self.get_collection(database, collection)
        return coll.find_one(filterer, *args, **kwargs)

    def update_one(
        self,
        database,
        collection,
        filterer,
        update,
        upsert=False,
        bypass_document_validation=False,
        collation=None,
        array_filters=None,
        hint=None,
        session=None,
    ):
        """
        更新单条文档
        :param database: 数据库名称
        :param collection: 集合名称
        :param filterer: 过滤条件
        :param update: 更新内容
        :param upsert:
        :param bypass_document_validation:
        :param collation:
        :param array_filters:
        :param hint:
        :param session:
        :return: 更新结果
        """
        coll = self.get_collection(database, collection)
        return coll.update_one(
            filterer, update, upsert, bypass_document_validation, collation, array_filters, hint, session
        )

    def update_many(
        self,
        database,
        collection,
        filterer,
        update,
        upsert=False,
        array_filters=None,
        bypass_document_validation=False,
        collation=None,
        hint=None,
        session=None,
    ):
        """
        更新多条文档
        :param database: 数据库名称
        :param collection: 集合名称
        :param filterer: 过滤条件
        :param update: 更新内容
        :param upsert:
        :param array_filters:
        :param bypass_document_validation:
        :param collation:
        :param hint:
        :param session:
        :return: 更新结果
        """
        coll = self.get_collection(database, collection)
        return coll.update_many(
            filterer, update, upsert, array_filters, bypass_document_validation, collation, hint, session
        )

    def delete_one(self, database, collection, filterer, collation=None, hint=None, session=None):
        """
        删除单条文档
        :param database: 数据库名称
        :param collection: 集合名称
        :param filterer: 过滤条件
        :param collation:
        :param hint:
        :param session:
        :return: 删除结果
        """
        coll = self.get_collection(database, collection)
        return coll.delete_one(filterer, collation, hint, session)

    def delete_many(self, database, collection, filterer, collation=None, hint=None, session=None):
        """
        删除多条文档
        :param database: 数据库名称
        :param collection: 集合名称
        :param filterer: 过滤条件
        :param collation:
        :param hint:
        :param session:
        :return: 删除结果
        """
        coll = self.get_collection(database, collection)
        return coll.delete_many(filterer, collation, hint, session)

    @classmethod
    def get_search_dbname(cls, idx: str):
        """
        获取查询库的库名信息
        :param idx: 相册最后一位
        :return:
        """
        return cls.SEARCH_MAP.get(idx)


if __name__ == "__main__":
    # m = MongoConn(database='db7', collection='tb_album_item')
    m = MongoPool()
    # print(
    #     m.find_one(
    #         "db6", "tb_album_item", {"itemId": "I0ldbdj2b4b9z08v00h00b354", "srcAlbumId": "A201903161122585580000642"}
    #     )
    # )

    a = m.find(
        "nhot",
        "tb_album_item",
        {"albumId": "A202106041639417500001376", "state": 0},
        sort=(("updateTime", -1),),
        limit=64,
    )
    li = [[i["itemId"], i["itemName"], i["updateTime"]] for i in a]
    ids = "', '".join(i[0] for i in li)
    print(li)
    print(ids)
