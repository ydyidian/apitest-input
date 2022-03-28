# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2022/03/25 14:12
@Desc: 设置参数
"""

import os


class Settings(object):

    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    LOG_DIR = os.path.join(BASE_DIR, "logs")

    CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'config.yml')
