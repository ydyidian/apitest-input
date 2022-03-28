# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2022/03/25 17:36
@Desc: 定义URI统一枚举类
"""


from enum import Enum
from collections import namedtuple
from types import DynamicClassAttribute


WegoURI = namedtuple("WegoURI", ["uri", "desc"])


class URIEnum(Enum):
    @DynamicClassAttribute
    def uri(self):
        return self._value_.uri

    @DynamicClassAttribute
    def value(self):
        return self._value_.uri

    @DynamicClassAttribute
    def desc(self):
        return self._value_.desc

    @classmethod
    def by(cls, value):
        for field, enum in cls._value2member_map_.items():
            if value == field.value:
                return enum
        raise ValueError(f"{cls.__name__}(uri={value}):没有对应的枚举")

    @classmethod
    def by_desc(cls, text):
        for field, enum in cls._value2member_map_.items():
            if text == field.desc:
                return enum
        raise ValueError(f"{cls.__name__}(desc={text}):没有对应的枚举")

    @DynamicClassAttribute
    def field(self):
        return self._value_
