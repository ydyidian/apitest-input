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

from common.dbs.mysql_client import Model, MySQLPool
from common.logging.logger import Logger

logger = Logger(__name__)


class ScriptTag(object):

    pool = MySQLPool()

    @classmethod
    @allure.step("获取话术标签信息")
    def get_script_tag_info(
        cls,
        album_id,
        id_=None,
        name: str = None,
        status: int = None,
        order_by: str = None,
        order: str = None,
        start_row: int = None,
        num: int = None,
        search_mode='match'
    ):
        """
        获取话术标签信息
        :param album_id:
        :param id_: 相册ID, 默认值: None
        :param name: 标签名称, 默认值: None
        :param status: 状态, 默认值: None
        :param order_by: 排序字段, 默认值: None
        :param order_method: , 默认值: None
        :param start_row: 起始行, 默认值: None
        :param num: 查询数量, 默认值: None
        :return:
        """
        name_filter = ''
        if name:
            if search_mode == 'match':
                name_filter = f"  and c_name like '%{name}%'"
            else:
                name_filter = f"  and c_name='{name}'"
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
            f"{name_filter}",
            f"  and n_status = '{status}'" if status is not None else "",
            f"order by {order_by} {order}" if order else "",
            f"limit {start_row},{num}" if start_row and num else ("limit {num}" if num else ""),
        )
        logger.info(sel_script_tag_info, desc="查询话术标签信息SQL")
        num, infos = cls.pool.query(sel_script_tag_info)
        return num, Model.data2obj(sel_script_tag_info, infos) if infos else infos

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
        logger.info(del_script_tag_info, desc="删除话术标签信息SQL")
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
        logger.info(upd_script_tag_info, desc="更新话术标签信息SQL")
        return cls.pool.execute(upd_script_tag_info)

    @classmethod
    @allure.step("插入话术标签信息")
    def insert_script_tag_info(cls, values: list):
        upd_script_tag_info = cls.pool.strip_multi_line_sql(
            "insert into tb_script_tag (c_album_id,",
            "c_name,",
            "n_script_count,",
            "n_status,",
            "t_script_last_operation_time,",
            "t_create_time,",
            "t_update_time) values (",
            ', '.join(["%s"] * 7),
            ")",
        )
        logger.info(f"{upd_script_tag_info}\nvalues:\n{values}", desc="插入话术标签信息SQL")
        return cls.pool.execute_many(upd_script_tag_info, values)
