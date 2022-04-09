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
from json.encoder import encode_basestring

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

    black_list = ("SWITCH_ON", "LOGGER_FILE_NAME", "ALLURE_FORMATTER", "FORMATTER")

    FORMATTER = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(threadName)s | %(name)s | %(filename)s:%(lineno)d: %(message)s"
    )
    ALLURE_FORMATTER = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    LOGGER_FILE_NAME = datetime.now().strftime("%Y%m%d%H%M%S.log")
    SWITCH_STATE = Settings.LOG_STATE

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
        if self.SWITCH_STATE == "2":
            # 创建一个handler，用于写入日志文件
            fh = logging.FileHandler(os.path.join(Settings.LOG_DIR, self.LOGGER_FILE_NAME), encoding="utf-8")
            fh.setLevel(logging.INFO)
            fh.setFormatter(self.FORMATTER)
            self.addHandler(fh)

        self.__indent = "&nbsp;" * 2
        self._reset_data()

    def _reset_data(self):
        self.__desc = None
        self.__messages = []
        self.__sep = "\n"

    def log(self, level: int, msg: object, *args: object, desc: str = None, **kwargs) -> None:
        self.__desc = desc
        msg = self._dispatch_msg(msg, **kwargs)
        return super().log(level, msg, *args, **kwargs)

    def debug(self, msg: object, *args: object, desc: str = None, **kwargs) -> None:
        self.__desc = desc
        msg = self._dispatch_msg(msg, **kwargs)
        return super().debug(msg, *args, **kwargs)

    def info(self, msg: object, *args: object, desc: str = None, **kwargs) -> None:
        self.__desc = desc
        msg = self._dispatch_msg(msg, **kwargs)
        return super().info(msg, *args, **kwargs)

    def warning(self, msg: object, *args: object, desc: str = None, **kwargs) -> None:
        self.__desc = desc
        msg = self._dispatch_msg(msg, **kwargs)
        return super().warning(msg, *args, **kwargs)

    def error(self, msg: object, *args: object, desc: str = None, **kwargs) -> None:
        self.__desc = desc
        msg = self._dispatch_msg(msg, **kwargs)
        return super().error(msg, *args, **kwargs)

    def critical(self, msg: object, *args: object, desc: str = None, **kwargs) -> None:
        self.__desc = desc
        msg = self._dispatch_msg(msg, **kwargs)
        return super().critical(msg, *args, **kwargs)

    def _dispatch_msg(self, msg: object, **kwargs):
        if isinstance(msg, (list, tuple)):
            self.__messages.extend(str(i) for i in msg)
            msg = f"{self.__sep}".join(str(i) for i in msg)
        else:
            msg = str(msg)
            self.__messages.append(msg)
        return msg

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
        record = self.makeRecord(
            self.name,
            level,
            fn,
            lno,
            f"{self.__desc}\n{msg}" if self.__desc else msg,
            args,
            exc_info,
            func,
            extra,
            sinfo,
        )
        if self.SWITCH_STATE in ("1", "2"):
            self.handle(record)
        # 添加allure日志信息
        asctime = self.ALLURE_FORMATTER.formatTime(record)
        log_msg = (
            f'<div style="line-height: 1.5em; display: inline-block; width: 98%">{asctime}&nbsp;'
            '<i class="fa fa-file-text-o"></i>'
            f' Log: &nbsp;<span class="log-label {LOG_STYLE_MAP.get(record.levelname)}">{record.levelname}</span>&nbsp;'
            f"{(self.__desc + '<br>') if self.__desc else ''}"
            f"{self.__sep.join(self._assemble_msg(item) for item in self.__messages)}</div>"
        )
        with allure.step(log_msg):
            pass

        # 重置
        self._reset_data()

    def _assemble_msg(self, msg):
        try:
            eval_str = eval(msg)
            assert isinstance(eval_str, dict), "字符串不是JSON格式或Python字典格式！"
            msg = (
                '<br><div style="background-color: #f8f8f9; line-height: 1.3em; font-family:monospace,Courier New; '
                'padding: 5px;margin: 5px 0;border-radius: 10px;">' + self._prettify_html_json(eval_str) + "</div>"
            )
        finally:
            return msg.replace("\n", "<br>").replace("\s", "&nbsp;").replace("\t", "&nbsp;" * 4)

    def _prettify_html_json(self, dic_obj, deepths=1):
        return (
            "{<br>"
            + ",<br>".join(
                self.__indent * deepths
                + f"{self._assemble_html_json_value(k, True)}: {self._assemble_html_json_value(v, deepths=deepths)}"
                for k, v in dic_obj.items()
            )
            + f"<br>{self.__indent * (deepths -1)}}}"
        )

    def _assemble_html_json_value(self, value, is_key=False, deepths=1):
        if isinstance(value, str):
            return f"""<span style="color: {'#ba6bda' if is_key else '#55a4a7'}">{encode_basestring(value)}</span>"""
        elif isinstance(value, bool):
            return f'<span style="color: #ed9b02">{value}</span>'.lower()
        elif isinstance(value, (int, float)):
            return f'<span style="color: #7098ef">{value}</span>'
        elif value is None:
            return '<span style="color: #f1592a">null</span>'
        elif isinstance(value, list):
            return (
                "[<br>"
                + ",<br>".join(
                    f"{self.__indent * (deepths + 1)}" + self._assemble_html_json_value(item, deepths=deepths + 1)
                    for item in value
                )
                + f"<br>{self.__indent * deepths}]"
            )
        elif isinstance(value, dict):
            return self._prettify_html_json(value, deepths + 1)


if __name__ == "__main__":
    logger = Logger(__file__)
    Logger.SWITCH_ON = False
    logger.info("fdsh")
