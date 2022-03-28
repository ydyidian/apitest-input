# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2022/03/26 10:37
@Desc: 用户关系
"""


from typing import List

import allure
from common.dbs.mysql_client import MySQLPool


class Relation(object):
    conn = MySQLPool()

    @classmethod
    @allure.step("数据库-获取粉丝关系")
    def is_fans(cls, album_id, other_album_id):
        """
        获取是否粉丝
        :param album_id: 相册ID
        :param fans_album_id: 粉丝相册ID
        :return:
        """
        sql_is_fans = f"""
            select count(1)
            from tb_album_followers_fans_{album_id[-1]}
            where c_album_id = '{album_id}'
              and c_fans_shop_id = '{other_album_id}'
        """
        return cls.conn.fetch_one_field(sql_is_fans)

    @classmethod
    @allure.step("数据库-查询客户是否存在群组中")
    def is_group_member(cls, album_id: str, member_album_id: str, group_ids: List[int]):
        """
        数据库-查询商品标签数据

        :param album_id: 相册ID
        :param member_album_id: 成员相册ID
        :param group_ids: 群组ID列表
        :return: 是否群组成员
        """
        select_is_in_group = f"""
            select count(1)
            from tb_album_group_fans_member_{album_id[-1]}
            where c_album_id = '{album_id}'
              and c_member_album_id = '{member_album_id}'
              {f'and c_group_id in ({cls.conn.convert_sql_in_cond(group_ids)})' if group_ids else ''}
        """
        return cls.conn.fetch_one_field(select_is_in_group)
