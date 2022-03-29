# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2022/03/25 14:12
@Desc: 设置参数
"""

import os

from common.meta.metaclass import ForbidClassFieldMeta
from common.path.filepath import FilePath
from common.support.yaml_parse import get_yaml_data


class Settings(object, metaclass=ForbidClassFieldMeta):
    black_list = ("ENV_MAP", "ENV_NAME", "ENV_SERIAL", "BASE_DIR", "LOG_DIR", "DOMAIN", "CONFIG")

    ENV_MAP = {
        "1": "https://www.wegoab.com",
        "2": "https://www.wegobiz.cn",
        "3": "https://www.microboss.me",
        "3a": "https://3a.wegoab.com",
        "3b": "https://3b.wegoab.com",
        "3c": "https://3c.wegoab.com",
        "3d": "https://3d.wegoab.com",
        "4": "https://www.tapbiz.cn",
    }

    ENV_NAME, ENV_SERIAL = os.environ.get("auto_env", "test_3d").split("_")
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    LOG_DIR = os.path.join(BASE_DIR, "logs")
    LOG_STATE = os.environ.get("log_state", "0")
    DOMAIN = ENV_MAP.get(ENV_SERIAL)
    CONFIG = get_yaml_data(FilePath.get_abspath_by_relation(__file__, f"../config/test_{ENV_SERIAL[0]}_config.yml"))
