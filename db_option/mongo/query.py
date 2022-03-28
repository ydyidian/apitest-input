# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2021/8/9 16:47
@Desc:
"""

from common.dbs.mongo_client import MongoPool


class Query(object):
    conn = MongoPool()

    @classmethod
    def get_album_inf(cls, album_id, goods_id, dbname):
        return cls.conn.find_one(dbname, "tb_album_item",  {"itemId": goods_id, "albumId": album_id})
