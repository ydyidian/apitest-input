# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2022/03/25 17:37
@Desc:
"""

import os
from _pytest.unittest import UnitTestCase


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        dest="env",
        action="store",
        choices=["test_1", "test_2", "test_3", "test_3a", "test_3b", "test_3c", "test_3d", "test_4"],
        default="test_3d",
        help="自动化运行环境",
    )
    parser.addoption(
        "--log-state",
        dest="log_state",
        action="store",
        choices=["0", "1", "2"],
        default="0",
        help="日志状态，0-只在allure报告中打印，1-在控制台和allure报告中打印，2-控制台、文件、allure报告中打印",
    )


def pytest_collection(session):
    """
    案例收集session开始
    :param session: 案例收集session对象
    """
    # print(f"收集案例session开始，转码「{session.config.args}」成unicode字符···")
    session.config.args = [item.encode("unicode-escape").decode("utf8") for item in session.config.args]
    os.environ["auto_env"] = session.config.option.env
    os.environ["log_state"] = session.config.option.log_state


def pytest_itemcollected(item):
    if not isinstance(item.parent, UnitTestCase):
        item.name = item.name.encode("utf8").decode("unicode-escape")
        item._nodeid = item._nodeid.encode("utf8").decode("unicode-escape")
