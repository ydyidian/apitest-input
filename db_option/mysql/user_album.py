# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2022/03/30 17:37
@Desc:
"""

from typing import AnyStr, List

import allure

from common.dbs.mysql_client import MySQLPool
from common.logging.logger import Logger

logger = Logger(__name__)


class UserAlbum(object):
    pool = MySQLPool()

    @classmethod
    @allure.step("获取用户相册信息")
    def get_user_album_infos(cls, *album_ids: str):
        """
        获取用户相册信息
        :param album_ids: 相册ID, 可以传入多个
        """
        sel_album_info = f"""
            select c_album_id,
                   c_album_name,
                   c_album_icon,
                   c_album_desc,
                   c_album_code_share_desc,
                   c_album_code,
                   c_album_qrcode,
                   c_album_minicode,
                   c_album_minicode_backup,
                   c_album_only_minicode,
                   c_album_only_minicode_backup,
                   c_album_minicode_nine_photo,
                   c_album_minicode_backup_nine_photo,
                   c_album_code_nine_photo,
                   c_baner_img,
                   n_is_enabled,
                   t_first_show_time,
                   t_create_time,
                   t_update_time
            from tb_album_info
            where c_album_id in ({cls.pool.convert_sql_in_cond(album_ids)})
        """
        logger.info(f"用户相册信息SQL: \n{sel_album_info}")
        _, infos = cls.pool.query(sel_album_info)
        return {item[0]: item for item in infos}

    @classmethod
    @allure.step("获取用户ID信息")
    def get_user_infos(cls, *album_ids: str):
        """
        获取用户ID信息
        :param album_ids: 相册ID, 可以传入多个
        """
        sel_user_id = f"""
            select c_album_id,
                   c_user_id
            from tb_user_album
            where c_album_id in ({cls.pool.convert_sql_in_cond(album_ids)})
        """
        logger.info(f"用户相册信息SQL: \n{sel_user_id}")
        _, infos = cls.pool.query(sel_user_id)
        return {item[0]: item for item in infos}
