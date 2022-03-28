# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2022/03/25 17:37
@Desc:
"""


from _pytest.unittest import UnitTestCase


def pytest_collection(session):
    """
    案例收集session开始
    :param session: 案例收集session对象
    """
    # print(f"收集案例session开始，转码「{session.config.args}」成unicode字符···")
    session.config.args = [item.encode("unicode-escape").decode("utf8") for item in session.config.args]


def pytest_itemcollected(item):
    if not isinstance(item.parent, UnitTestCase):
        item.name = item.name.encode("utf8").decode("unicode-escape")
        item._nodeid = item._nodeid.encode("utf8").decode("unicode-escape")
