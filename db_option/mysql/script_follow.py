# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2022/03/28 16:58
@Desc:
"""

import re
from typing import AnyStr, List

import allure

from common.dbs.mysql_client import MySQLPool
from common.logging.logger import Logger

logger = Logger(__name__)


class Follower(object):

    pool = MySQLPool()

    @classmethod
    @allure.step("获取粉丝关注信息")
    def get_script_follower_info(
        cls,
        *,
        n_id: str = None,
        album_id: str = None,
        follow_ids: List[AnyStr] = None,
        is_read: int = None,
        slip_type: str = None,
        ts: int = None,
        sort_field: str = None,
        sort_mode: str = None,
        start_row: int = None,
        num: int = None,
    ):
        """
        获取粉丝关注信息
        :param album_id: 相册ID, 默认值: None
        :param follow_ids: 粉丝相册ID列表, 默认值: None
        :param is_read: 是否已读, 默认值: None
        :param slip_type: 翻页类型, 默认值: None， 0：上滑 ｜ 1：下拉
        :param ts: 翻页时间戳, 默认值: None
        :param n_id: 主键ID, 默认值: None
        :param sort_field: 排序字段, 默认值: None
        :param sort_mode: 排序方式, 默认值: None， asc | desc
        :param start_row: 起始行, 默认值: None
        :param num: 查询数量, 默认值: None
        """
        if sort_mode is not None:
            assert sort_field is not None, "排序需要传入字段"
            assert re.match("asc|desc", sort_mode, re.I)
        if start_row:
            assert num is not None
        if ts is not None:
            assert slip_type in ("0", "1")
        sel_follow_info = f"""
            select
                n_id,
                c_album_id,
                c_follow_album_id,
                n_is_read,
                n_sort_num,
                t_create_time,
                t_update_time
            from tb_script_follow_info
            where 1 = 1
            {f"and n_id = '{n_id}'" if n_id else ''}
            {f"and c_album_id = '{album_id}'" if album_id else ''}
            {f"and n_is_read = '{n_id}'" if is_read else ''}
            {f"and n_id {'<' if slip_type else '>'} {ts}" if ts else ''}
            {f"and c_follow_album_id in ({cls.pool.convert_sql_in_cond(follow_ids)})" if follow_ids else ''}
            {f"order by {sort_field}" if sort_field else ""} {sort_mode if sort_mode else ""}
            {f"limit {start_row}, {num}" if start_row and num else (f"limit {num}" if num else "")}
        """
        logger.info(f"粉丝关注信息SQL: \n{sel_follow_info}")
        return cls.pool.query(sel_follow_info)

    @classmethod
    @allure.step("删除关注信息")
    def del_follow_info(cls, *, n_ids: List = None, album_ids: List = None, follow_album_ids: List = None):
        """
        删除关注信息
        :param n_ids: 主键ID, 默认值: None
        :param album_ids: 相册ID列表, 默认值: None
        :param follow_album_ids: 关注相册ID列表, 默认值: None
        :return: 删除数
        """
        if not n_ids and not album_ids and not follow_album_ids:
            raise ValueError("三个参数必填其一「防止删表」！")
        del_follow_inf = f"""
            delete from tb_script_follow_info
            where 1 = 1
                {f'and n_id in ({cls.pool.convert_sql_in_cond(n_ids)})' if n_ids else ''}
                {f'and c_album_id in ({cls.pool.convert_sql_in_cond(album_ids or [])})' if not n_ids else ''}
                {f'and c_follow_album_id in ({cls.pool.convert_sql_in_cond(follow_album_ids or [])})'
                if not n_ids else ''}
        """
        logger.info(f"删除粉丝关注信息SQL: \n{del_follow_inf}")
        return cls.pool.execute(del_follow_inf)

    @classmethod
    @allure.step("更新关注信息")
    def update_follow_info(
        cls, update_str, *, n_ids: List = None, album_ids: List = None, follow_album_ids: List = None
    ):
        """
        更新关注信息
        :param update_str: 更新字段
        :param n_ids: 主键ID, 默认值: None
        :param album_ids: 相册ID, 默认值: None
        :param follow_album_ids: 关注相册ID, 默认值: None
        :return: 更新数
        """
        del_follow_inf = f"""
            update tb_script_follow_info set {update_str}
            where 1 = 1
                {f'and n_id in ({cls.pool.convert_sql_in_cond(n_ids)})' if n_ids else ''}
                {f'and c_album_id in ({cls.pool.convert_sql_in_cond(album_ids or [])})' if not n_ids else ''}
                {f'and c_follow_album_id in ({cls.pool.convert_sql_in_cond(follow_album_ids or [])})'
                if not n_ids else ''}
        """
        logger.info(f"删除粉丝关注信息SQL: \n{del_follow_inf}")
        return cls.pool.execute(del_follow_inf)


if __name__ == "__main__":
    print(Follower.get_script_follower_info(1072))
