# coding=utf8

# ＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊
#
# @Author: yiciu
# @Version: 1.0
# @Date: 2022/04/07 19:39 | 周四
# @Desc:
#    - 增加sql去除空行
#    - 增加数据库查询内容转对象
#
# ＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊


import re
from collections import namedtuple
from typing import List

import pymysql
from common.settings import Settings


class MySQLPool(object):
    CONNECTION_MAP = Settings.CONFIG.get("mysql", {})  # 加载数据库连接信息字典
    connection_cache = {}

    def __init__(self):
        self.conn = None

    def _get_cursor(self, dbname):
        """
        获取游标
        :param dbname: 数据库key值，根据yml配置（test_x_config.yml）来
        :return: 游标对象
        """
        conn_inf = self.CONNECTION_MAP.get(dbname)
        host, port, user, password, database = (
            conn_inf["host"],
            conn_inf["port"],
            conn_inf["user"],
            conn_inf["password"],
            conn_inf["database"],
        )
        k = f"{host}^{port}^{user}^{password}"
        if k in MySQLPool.connection_cache:
            conn = MySQLPool.connection_cache[k]
        else:
            conn = pymysql.Connection(user=user, password=password, host=host, port=port)
            MySQLPool.connection_cache.update({k: conn})
        conn.select_db(database)
        self.conn = conn
        return conn.cursor()

    def execute_many(self, sql, args, dbname="wg_tongs_test"):
        """
        执行多条sql
        :param sql: sql语句
        :param args: %s参数列表
        :param dbname: 数据库key值
        :return:
        """
        cursor = self._get_cursor(dbname)
        rows = cursor.executemany(sql, args)
        self.conn.commit()
        return rows

    def execute(self, sql, args=None, dbname="wg_tongs_test"):
        """
        执行sql
        :param sql: sql语句
        :param args: %s参数列表
        :param dbname: 数据库key值
        :return:
        """
        cursor = self._get_cursor(dbname)
        rows = cursor.execute(sql, args)
        self.conn.commit()
        return rows

    def query(self, sql, args=None, dbname="wg_tongs_test"):
        """
        查询mysql
        :param sql: sql语句
        :param args: %s参数列表
        :param dbname: 数据库key值
        :return: 记录条数，记录列表
        """
        cursor = self._get_cursor(dbname)
        rows = cursor.execute(sql, args)
        # 解决数据库重复查询数据不更新
        self.conn.commit()
        fetchs = cursor.fetchall()
        return rows, fetchs

    def fetch_one_row(self, sql, args=None, dbname="wg_tongs_test"):
        """
        查询单条记录
        :param sql: sql语句
        :param args: %s参数列表
        :param dbname: 数据库key值
        :return: 数据库查询结果
        """
        cursor = self._get_cursor(dbname)
        cursor.execute(sql, args)
        self.conn.commit()
        return cursor.fetchone()

    def fetch_one_field(self, sql, args=None, default=None, dbname="wg_tongs_test"):
        """
        查询单个字段
        :param sql: sql语句
        :param args: %s参数列表
        :param default: 查询为空的时候默认返回None
        :param dbname: 数据库key值
        :return: 数据库查询结果
        """
        res = self.fetch_one_row(sql, args)
        return res[0] if res else default

    def convert_sql_in_cond(self, iter_obj, is_dual=False, index=0, quoter="'"):
        """
        转换为sql的in条件字符
        :param iter_obj: 列表对象
        :param is_dual: 是否为二维列表
        :param index: 二维列表中的指定列转为in
        :param quoter: 默认单引号
        :return: sql-in条件
        """
        return (
            (f"{quoter}" + f"{quoter}, {quoter}".join([str(item[index]) for item in iter_obj]) + f"{quoter}")
            if is_dual
            else (f"{quoter}" + f"{quoter}, {quoter}".join([str(item) for item in iter_obj]) + f"{quoter}")
        )

    def strip_multi_line_sql(self, *squence):
        """
        去除空行
        :return: 去掉空行sql
        e.g. squence: ('select', 'name', '', 'from table', 'where name="233"')
        =>  select
            name
            from table
            where name="233"
        """
        return "\n".join(i for i in squence if i)


class Model(object):

    SQL_REGEXP = "(?is).*?select\W+(?P<fields>.+)\W+from\W+(?P<table>[\w_]+(?P<dot>\.)?(?(dot)[\w_]+))"
    AS_CALUSE_REGEXP = ".+as\W+([\w_]+)"

    @classmethod
    def data2obj(cls, query_sql_str: str, query_res: List):
        """
        mysql查询结果转对象类型
        :param query_sql_str: 查询sql语句
        :param query_res: 查询结果列表
        :return: 对象/对象列表「如果是一维的直接返回对象，如果是二维的返回对象列表」
        """
        assert isinstance(query_res, (list, tuple))
        model_name, fields = cls.__get_table_fields(query_sql_str)
        model_class_ = namedtuple(model_name, fields)
        return (
            [model_class_(**dict(zip(fields, item))) for item in query_res]
            if isinstance(query_res[0], (list, tuple))
            else model_class_(**dict(zip(fields, query_res)))
        )

    @classmethod
    def __get_table_fields(cls, query_sql_str):
        """
        从select语句中获取model信息
        :param query_sql_str: select语句
        :return: 表名，字段名列表 「如果是多表查询，默认第一张表，暂不支持select * from (xxx)」
        """
        match = re.match(cls.SQL_REGEXP, query_sql_str)
        if match:
            method_name_use_dic = {}
            md = match.groupdict()
            fields_str, table_name = md["fields"], md["table"].split(".")[-1] if md["dot"] else md["table"]
            model_name = "".join((item.capitalize() if idx else item for idx, item in enumerate(table_name.split("_"))))
            field_list = []
            field_tmp_str, l_bracket_cnt, r_bracket_cnt = "", 0, 0
            for field_tmp in fields_str.split(","):
                if " as " in field_tmp:
                    field_list.append(re.match(cls.AS_CALUSE_REGEXP, field_tmp).group(1))
                # 匹配括号相等：bug：包含'('或者"("
                elif "(" in field_tmp or field_tmp_str:
                    if l_bracket_cnt:
                        bracket_cnt = field_tmp.count(")")
                        field_tmp_str += "," + field_tmp
                        if l_bracket_cnt == r_bracket_cnt + bracket_cnt:
                            if " as " in field_tmp_str:
                                field_list.append(re.match(cls.AS_CALUSE_REGEXP, field_tmp_str).group(1))
                                continue
                            # else
                            method_name = field_tmp_str.strip().split("(")[0].lower()
                            if method_name in method_name_use_dic:
                                field_list.append(f"{method_name}{method_name_use_dic[method_name]}")
                                method_name_use_dic[method_name] += 1
                            else:
                                field_list.append(f"{method_name}1")
                                method_name_use_dic[method_name] = 2
                            l_bracket_cnt, r_bracket_cnt = 0, 0  # 重置
                        else:
                            r_bracket_cnt += bracket_cnt
                    else:
                        l_bracket_cnt, r_bracket_cnt = field_tmp.count("("), field_tmp.count(")")
                        if l_bracket_cnt == r_bracket_cnt:
                            if " as " in field_tmp:
                                field_list.append(re.match(cls.AS_CALUSE_REGEXP, field_tmp).group(1))
                                continue
                            # else
                            method_name = field_tmp.strip().split("(")[0].lower()
                            if method_name in method_name_use_dic:
                                field_list.append(f"{method_name}{method_name_use_dic[method_name]}")
                                method_name_use_dic[method_name] += 1
                            else:
                                field_list.append(f"{method_name}1")
                                method_name_use_dic[method_name] = 2

                            l_bracket_cnt, r_bracket_cnt = 0, 0  # 重置
                        else:
                            field_tmp_str = field_tmp
                else:
                    field_list.append(field_tmp.strip())
        else:
            raise ValueError("SQL编写格式错误！请检查SQL是否编写正确！")

        return model_name, field_list


if __name__ == "__main__":
    # m = MySQLPool()
    sql = """
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
        and c_album_id = 'A202008311642051830029829'
        and c_follow_album_id in ('A202204031323580186300800')
    """
    print(
        Model.data2obj(sql, ((1699, "A202008311642051830029829", "A202204031339405134000129", 0, 1648964381296, 1, 2)))
    )
