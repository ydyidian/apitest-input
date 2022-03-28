# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2022/03/25 17:24
@Desc: 同步等待Mongo查询
"""

import time

from common.logging.logger import Logger
from common.dbs.mongo_client import MongoPool

logger = Logger(__name__)


class SyncWait(object):
    conn = MongoPool()

    @classmethod
    def wait_for_album_created(cls, album_id, goods_id, timeout=10, interval=500):
        """
        等待商品创建完成
        :param album_id: 相册id
        :param goods_id: 商品id
        :param timeout: 超时时间，单位s
        :param interval: 访问间隔，单位ms
        :return:
        """
        res = None
        count = 0
        count_endpoint = int(timeout * 1000 / interval)
        sleep_interval = interval / 1000
        while res is None and count < count_endpoint:
            res = cls.conn.find_one(f"db{album_id[-3]}", "tb_album_item", {"itemId": goods_id, "albumId": album_id})
            logger.debug(f"当前查询结果: {res}")
            time.sleep(sleep_interval)
            count += 1
        else:
            end_tm = interval * count
            if res is None:
                logger.error(f"查询超时，超时时间为{end_tm}ms")
                raise TimeoutError("查询超时")
            else:
                logger.info(f"等待时间为{end_tm}ms [灵敏度：{interval}ms]: {album_id} - {goods_id}")
        return res

    @classmethod
    def wait_for_doc_exist(cls, dbname, table, filterer, *args, timeout=10, interval=500, **kwargs):
        """
        等待商品创建完成
        :param dbname: 数据库名称
        :param table: 表名
        :param filterer: 过滤条件
        :param timeout: 超时时间，单位s
        :param interval: 访问间隔，单位ms
        :return:
        """
        res = None
        count = 0
        count_endpoint = int(timeout * 1000 / interval)
        sleep_interval = interval / 1000
        logger.debug(f"查询条件：{dbname} - {table} - {filterer}")
        while res is None and count < count_endpoint:
            res = cls.conn.find_one(dbname, table, filterer, *args, **kwargs)
            logger.debug(f"当前查询结果: {res}")
            time.sleep(sleep_interval)
            count += 1
        else:
            end_tm = interval * count
            if res is None:
                logger.error(f"查询超时，超时时间为{end_tm}ms")
                raise TimeoutError("查询超时")
            else:
                logger.info(f"等待时间为{end_tm}ms [灵敏度：{interval}ms]: {dbname} - {table} - {filterer}")
        return res


if __name__ == "__main__":
    SyncWait.wait_for_album_created("A201901242007447790000766", "I0de60m61e0eac0j00000f326")
    # 轮询等待数据存在，查询结果可以在第二个字典里里面控制，0表示不返回该字段, 1表示返回该字段
    SyncWait.wait_for_doc_exist("nhot", "tb_album_item", {"itemId": "I202111141820303160001761"}, {"_id": 0})
