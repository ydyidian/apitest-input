# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2022/03/28 16:58
@Desc:
"""

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
        cls, n_id: str = None, album_id: str = None, follow_ids: List[AnyStr] = None, is_read: int = None
    ):
        """
        获取粉丝关注信息
        :param album_id: 相册ID, 默认值: None
        :param follow_ids: 粉丝相册ID列表, 默认值: None
        :param is_read: 是否已读, 默认值: None
        :param n_id: 主键ID, 默认值: None
        """
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
            {f"and c_follow_album_id in ({cls.pool.convert_sql_in_cond(follow_ids)})" if follow_ids else ''}
        """
        logger.info(f"粉丝关注信息SQL: \n{sel_follow_info}")
        return cls.pool.query(sel_follow_info)


if __name__ == "__main__":
    print(Follower.get_script_follower_info(1072))
