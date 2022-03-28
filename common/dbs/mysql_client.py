# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2022/03/25 17:34
@Desc: MySQL数据库查询
"""


import pymysql

from common.support.yaml_parse import get_conn_mapping


class MySQLPool(object):
    CONNECTION_MAP = get_conn_mapping("mysql")  # 加载数据库连接信息字典
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
        k = f'{host}^{port}^{user}^{password}'
        if k in MySQLPool.connection_cache:
            conn = MySQLPool.connection_cache[k]
        else:
            conn = pymysql.Connection(user=user, password=password, host=host, port=port)
            MySQLPool.connection_cache.update({k: conn})
        conn.select_db(database)
        self.conn = conn
        return conn.cursor()

    def execute_many(self, sql, args, dbname='wg_tongs_test'):
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

    def execute(self, sql, args=None, dbname='wg_tongs_test'):
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

    def query(self, sql, args=None, dbname='wg_tongs_test'):
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

    def fetch_one_row(self, sql, args=None, dbname='wg_tongs_test'):
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

    def fetch_one_field(self, sql, args=None, default=None, dbname='wg_tongs_test'):
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


if __name__ == "__main__":
    m = MySQLPool()
