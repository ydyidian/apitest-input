# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2022/03/25 17:34
@Desc: 添加allure日志信息「默认不存储到文件」
"""


import logging
import os
import sys
from datetime import datetime

import allure
from common.meta.metaclass import ForbidClassFieldMeta

from common.settings import Settings

LOG_STYLE_MAP = {
    "CRITICAL": "log_status_failed",
    "FATAL": "log_status_failed",
    "ERROR": "log_status_failed",
    "WARNING": "log_status_warning",
    "WARN": "log_status_warning",
    "INFO": "log_status_passed",
    "DEBUG": "log_status_debug",
    "NOTSET": "log_status_verbose",
}


class Logger(logging.Logger, metaclass=ForbidClassFieldMeta):  # 日志类

    black_list = ('SWITCH_ON', 'LOGGER_FILE_NAME', 'ALLURE_FORMATTER', 'FORMATTER')

    FORMATTER = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(threadName)s | %(name)s | %(filename)s:%(lineno)d: %(message)s"
    )
    ALLURE_FORMATTER = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    LOGGER_FILE_NAME = datetime.now().strftime("%Y%m%d%H%M%S.log")
    SWITCH_ON = False

    def __init__(self, logger, log_level=logging.DEBUG):
        """
        logger类初始化
        :param logger_name: logger名称
        :param file_stream: 文件流，用于保存日志文件, defaults to None
        """

        super().__init__(logger, log_level)
        # self.logger.setLevel(level=log_level)

        # 创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(log_level)

        # 定义handler的输出格式

        ch.setFormatter(self.FORMATTER)

        # 给logger添加handler
        self.addHandler(ch)

        if self.SWITCH_ON:
            # 创建一个handler，用于写入日志文件
            fh = logging.FileHandler(os.path.join(Settings.LOG_DIR, self.LOGGER_FILE_NAME), encoding="utf-8")
            fh.setLevel(logging.INFO)
            fh.setFormatter(self.FORMATTER)
            self.addHandler(fh)

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False):
        """
        重写Logger的_log方法，添加allure日志处理逻辑
        :param level: 日志级别
        :param msg: 日志信息
        :param args: 参数
        :param exc_info: , 默认值: None
        :param extra: , 默认值: None
        :param stack_info: , 默认值: False
        """
        sinfo = None
        if logging._srcfile:
            try:
                fn, lno, func, sinfo = self.findCaller(stack_info)
            except ValueError:
                fn, lno, func = "(unknown file)", 0, "(unknown function)"
        else:
            fn, lno, func = "(unknown file)", 0, "(unknown function)"
        if exc_info:
            if isinstance(exc_info, BaseException):
                exc_info = (type(exc_info), exc_info, exc_info.__traceback__)
            elif not isinstance(exc_info, tuple):
                exc_info = sys.exc_info()
        record = self.makeRecord(self.name, level, fn, lno, msg, args, exc_info, func, extra, sinfo)
        if self.SWITCH_ON:
            self.handle(record)
        # 添加allure日志信息
        log_msg = self.ALLURE_FORMATTER.format(record)
        log_msg = '&nbsp;<i class="fa fa-file-text-o"></i> Log: ' + log_msg.replace(
            record.levelname,
            f'&nbsp;<span class="log-label {LOG_STYLE_MAP.get(record.levelname)}">{record.levelname}</span>&nbsp;',
        )
        with allure.step(log_msg):
            pass


if __name__ == "__main__":
    logger = Logger(__file__)
    Logger.SWITCH_ON = False
    logger.info("fdsh")
