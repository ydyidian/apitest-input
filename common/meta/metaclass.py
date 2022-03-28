# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2022/03/26 17:41
@Desc: 通过black_list禁用修改类属性
"""

from typing import Any


class ForbidClassFieldMeta(type):
    """
    禁用类属性修改
    :param type:
    """

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name == "black_list":
            raise ValueError("类属性[black_list]属性不允许修改")
        elif hasattr(self, "black_list") and __name in self.black_list:
            raise ValueError(f"类属性[{__name}]不允许修改")
        else:
            super().__setattr__(__name, __value)
