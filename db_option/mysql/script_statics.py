# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2022/03/31 16:58
@Desc:
"""


import allure

from common.dbs.mysql_client import MySQLPool
from common.logging.logger import Logger

logger = Logger(__name__)


class ScriptStatics(object):

    pool = MySQLPool()

    @classmethod
    @allure.step("获取粉丝关注信息")
    def get_user_statics(cls, *album_ids: str):
        """
        获取用户统计信息
        :param album_ids: 相册ID, 默认值: None
        """
        sel_statics_info = f"""
            select
                c_album_id,
                n_script_count,
                t_script_last_update_time
            from tb_script_album_config
            where c_album_id in ({cls.pool.convert_sql_in_cond(album_ids)})
        """
        logger.info(f"用户统计信息SQL: \n{sel_statics_info}")
        _, statics = cls.pool.query(sel_statics_info)
        return {i[0]: i for i in statics}
