# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2022/03/25 17:34
@Desc: 时间戳
"""


from datetime import date, datetime, timedelta
from decimal import Decimal
import time

__all__ = "TimeFilterUtil"

_DAYS_IN_MONTH = [-1, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def _is_leap(year):
    "year -> 1 if leap year, else 0."
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _days_in_month(year, month):
    "year, month -> number of days in that month in that year."
    assert 1 <= month <= 12, month
    if month == 2 and _is_leap(year):
        return 29
    return _DAYS_IN_MONTH[month]


class TimeFilterUtil(object):
    @staticmethod
    def get_day_filter_tms(day=0):
        """
        获取单天的过滤时间戳列表「开始以及结束时间戳，单位毫秒」
        :param day: 大于0表示以后的日期，小于0表示以前的日期，比如1表示明天，-1表示昨天, 默认值: 0「当天」
        :return: 开始、结束时间戳
        """
        dt = date.today() + timedelta(days=day)
        format_date = dt.strftime("%Y-%m-%d")
        start_tms = time.strptime(f"{format_date} 00:00:00", "%Y-%m-%d %H:%M:%S")
        end_tms = time.strptime(f"{format_date} 23:59:59", "%Y-%m-%d %H:%M:%S")
        return int(time.mktime(start_tms) * 1000), int(time.mktime(end_tms) * 1000 + 999)

    @staticmethod
    def get_month_filter_tms(month=0):
        """
        获取一个月的过滤时间戳列表「开始以及结束时间戳，单位毫秒」
        :param day: 大于0表示以后的日期，小于0表示以前的日期，比如1表示下月，-1表示上月, 默认值: 0「本月」
        :return: 开始、结束时间戳
        """
        dt = date.today()
        cur_month = dt.month
        cur_year = dt.year
        old_month = cur_month + month
        if old_month > 0:
            month = (old_month - 1) % 12 + 1  # 如果刚好是12那就返回12
            year = cur_year + (old_month - 1) // 12
        elif old_month <= 0:
            month, year = (
                (old_month % 12, cur_year + old_month // 12)
                if old_month % 12
                else (12 + old_month % 12, cur_year + old_month // 12 - 1)
            )
        month_end_day = _days_in_month(year, month)
        start_tms = time.strptime(f"{year}-{month}-01 00:00:00", "%Y-%m-%d %H:%M:%S")
        end_tms = time.strptime(f"{year}-{month}-{month_end_day} 23:59:59", "%Y-%m-%d %H:%M:%S")
        return int(time.mktime(start_tms) * 1000), int(time.mktime(end_tms) * 1000 + 999)

    @staticmethod
    def get_year_filter_tms(year=0):
        """
        获取整年的过滤时间戳列表「开始以及结束时间戳，单位毫秒」
        :param day: 大于0表示以后的日期，小于0表示以前的日期，比如1表示明年，-1表示去年, 默认值: 0
        :return: 开始、结束时间戳
        """
        dt = date.today()
        cur_year = dt.year
        year = cur_year + year
        assert 1970 <= year <= 2038
        start_tms = time.strptime(f"{year}-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
        end_tms = time.strptime(f"{year}-12-31 23:59:59", "%Y-%m-%d %H:%M:%S")
        return int(time.mktime(start_tms) * 1000), int(time.mktime(end_tms) * 1000 + 999)


class TimeUtil(object):
    @staticmethod
    def get_transfered_timestamp(timestamp: float, hours: int = 8, out_sytle: str = "string"):
        """
        获取时区转换后的时间戳
        :param timestamp: 时间戳
        :param hours: 时区差, 默认值: 8「东八」
        :param out_sytle: 输出格式样式, 默认值: string「字符型」
        :return: 转换后的时间戳
        """
        ts, ms = int(timestamp), int((Decimal(timestamp) % 1 * 1000).quantize(Decimal("1")))
        res_ts = (datetime.fromtimestamp(ts) + timedelta(hours=hours)).timestamp()
        return f"{res_ts:.0f}{ms}" if out_sytle == "string" else int(res_ts * 1000 + ms)


if __name__ == "__main__":
    print(TimeFilterUtil.get_day_filter_tms())
    print(TimeFilterUtil.get_month_filter_tms(-24))
    print(TimeFilterUtil.get_year_filter_tms())
    print(TimeUtil.get_transfered_timestamp(1647797092.201))
