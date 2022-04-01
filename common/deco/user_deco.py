# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2022/03/29 14:12
@Desc: 创建用户类方法装饰器，在类方法开始时生成用户，方法结束时删除用户「过程异常也会删除用户」
"""

from functools import wraps
from typing import Dict, List

from api.user import UserManager
from common.logging.logger import Logger

logger = Logger(__name__)


class CreateUserData:
    def __init__(self, user_num: int = None, vip_infos: List[Dict] = None):
        """
        初始化创建用户装饰器, 如果不传入参数，默认会创建一个永久会员用户
        :param user_num: 用户数, 默认值: None
        :param vip_infos: 用户会员信息, 默认值: None, 格式：[{"is_vip": 1, "expire": "2021-01-31"}]
        """
        self.__user_num = user_num or 1
        self.__vip_infos = vip_infos or [{"is_vip": 1, "expire": "2099-12-31"}]

    def __call__(self, func):
        """
        类方法调用
        :param func: 方法名称
        :return: res

        说明：在编写测试用例时，参数化名称统一使用inparam才会去获取里面的信息
        @allure.title("fdsaf")
        @CreateUserData()
        @pytest.mark.parametrize("inparam", [{"data": {"data": {}, "pre": {"user_num": 3, "vip_infos": ['1234']}}}])
        def test_01(self, pytestconfig, inparam):
            # self.user_prepare()
            print("test_ 01", inparam)

        yml格式：
        data:
          pre:
            user_num: 1
            vip_infos: [{"is_vip": 1, "expire": "2021-12-23"}]  # 其中expire为非必填参数，可以不传
        """
        @wraps(func)
        def inner(*args, **kwargs):
            if 'inparam' in kwargs and 'pre' in kwargs['inparam'] and 'user' in kwargs['inparam']['pre']:
                pre_in = kwargs['inparam']['pre']['user']
                assert 'user_num' in pre_in, "创建用户必须包含user_num字段！"
                self.__user_num = pre_in['user_num']
                self.__vip_infos = pre_in.get('vip_infos')
            logger.info(f"本次预计新增用户数：{self.__user_num}，开始创建···")
            users = UserManager.create_multi_users(self.__user_num, self.__vip_infos)
            logger.info(f"✅ 新增用户数：{self.__user_num}")
            if 'inparam' in kwargs:
                kwargs['inparam']['users'] = users
            res = None
            try:
                res = func(*args, **kwargs)
            finally:
                logger.info('用户数据清理···')
                UserManager.do_delete_user(*users)
                logger.info('✅ 用户数据清理DONE！')
            return res

        return inner
