# coding=utf8

# ＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊
#
# @Author: yiciu
# @Version: 1.0
# @Date: 2022/04/06 10:19 | 周三
# @Desc:
#
# ＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊


import allure

from common.dbs.mysql_client import MySQLPool
from common.logging.logger import Logger

logger = Logger(__name__)


class ScriptTag(object):

    pool = MySQLPool()

    @classmethod
    @allure.step("获取话术标签信息")
    def get_script_tag_info(cls, album_id, id_=None, name: str = None, status: int = None):
        """
        获取话术标签信息
        :param album_ids: 相册ID, 默认值: None
        """
        sel_script_tag_info = cls.pool.strip_multi_line_sql(
            "select",
            "    n_id,",
            "    c_album_id,",
            "    c_name,",
            "    t_script_last_operation_time,",
            "    n_script_count,",
            "    t_create_time,",
            "    t_update_time,",
            "    n_status",
            "from tb_script_tag",
            f"where c_album_id = '{album_id}'",
            f"  and n_id = '{id_}'" if id_ else "",
            f"  and c_name like '%{name}%'" if name else "",
            f"  and n_status = '{status}'" if status else "",
        )
        logger.info(f"查询话术标签信息SQL: \n{sel_script_tag_info}")
        return cls.pool.query(sel_script_tag_info)

    @classmethod
    @allure.step("删除话术标签信息")
    def del_script_tag_info(cls, album_id, id_=None, name: str = None, status: int = None):
        """
        删除话术标签信息
        :param album_id: 相册ID
        :param id_: 主键ID, 默认值: None
        :param name: 标签名称, 默认值: None
        :param status: 状态, 默认值: None
        :return:
        """
        del_script_tag_info = cls.pool.strip_multi_line_sql(
            "delete from tb_script_tag",
            f"where c_album_id = '{album_id}'",
            f"  and n_id = '{id_}'" if id_ else "",
            f"  and c_name like '%{name}%'" if name else "",
            f"  and n_status = '{status}'" if status else "",
        )
        logger.info(f"删除话术标签信息SQL: \n{del_script_tag_info}")
        return cls.pool.execute(del_script_tag_info)

    @classmethod
    @allure.step("更新话术标签信息")
    def update_script_tag_info(cls, upd_str, album_id, id_=None, name: str = None, status: int = None):
        """
        更新话术标签信息
        :param upd_str: 更新字段字符串
        :param album_id: 相册ID
        :param id_: 主键ID, 默认值: None
        :param name: 标签名称, 默认值: None
        :param status: 状态, 默认值: None
        :return:
        """
        upd_script_tag_info = cls.pool.strip_multi_line_sql(
            f"update tb_script_tag set {upd_str}",
            f"where c_album_id = '{album_id}'",
            f"  and n_id = '{id_}'" if id_ else "",
            f"  and c_name like '%{name}%'" if name else "",
            f"  and n_status = '{status}'" if status else "",
        )
        logger.info(f"更新话术标签信息SQL: \n{upd_script_tag_info}")
        return cls.pool.execute(upd_script_tag_info)
