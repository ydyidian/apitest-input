# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2022/03/25 17:35
@Desc: 用户管理
"""


from typing import List
from db_option.mysql.user import User, UserData
from common.logging.logger import Logger

logger = Logger(__name__)


class UserManager(object):
    @classmethod
    def create_single_user(cls, is_vip: int = 1, expire: str = "9999-12-31"):
        """
        创建单个用户

        :param is_vip: 是否VIP用户: 0 非会员｜ 1 会员 ｜ 2 试用期会员, 默认值: True
        :return:
        """
        user = User(is_vip, expire)
        logger.info(f"开始插入数据: {user.__dict__}")
        cls.do_create_user(user)
        return user

    @classmethod
    def create_multi_users(cls, user_num: int, vip_infos: List[dict] = None):
        """
        批量创建用户

        :param user_num: 用户数
        :param vip_list: 对应用户的VIP信息, 默认值: None, 示例：{"is_vip": 1, "expire": "2022-02-22"}
        :return:
        """
        users = []
        if vip_infos:
            assert user_num == len(vip_infos)
            for vip_info in vip_infos:
                user = User(vip_info["is_vip"], vip_info.get("expire"))
                users.append(user)
                logger.info(f"开始插入数据: {user.__dict__}")
        else:
            for i in range(user_num):
                user = User()
                users.append(user)
                logger.info(f"开始插入数据: {user.__dict__}")
        cls.do_create_user(*users)
        return users

    @staticmethod
    def do_create_user(*users: List[User]):
        UserData.insert_album_info(*users)
        UserData.insert_user_album(*users)
        UserData.insert_user_auth(*users)
        UserData.insert_user_token(*users)
        UserData.insert_user_info(*users)
        UserData.insert_user_vip(*users)
        UserData.insert_album_config(*users)
        UserData.insert_phone_login(*users)
        UserData.insert_album_follows_attention(*users)

    @staticmethod
    def do_delete_user(*users: List[User]):
        UserData.del_album_info(*users)
        UserData.del_user_album(*users)
        UserData.del_user_auth(*users)
        UserData.del_user_token(*users)
        UserData.del_user_info(*users)
        UserData.del_user_vip(*users)
        UserData.del_album_config(*users)
        UserData.del_phone_login(*users)
        UserData.del_album_follows_attention(*users)


if __name__ == "__main__":
    # user = UserManager.create_single_user()
    # UserManager.do_delete_user(user)
    users = UserManager.create_multi_users(1, [{"is_vip": 1, "expire": "2022-03-01"}])
    UserManager.do_delete_user(*users)
