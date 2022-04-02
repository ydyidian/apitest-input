# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2022/04/01 16:19
@Desc:
"""


import allure
import pytest
from common.assertion import Assertion
from common.core.base import BaseAPI
from common.deco.user_deco import CreateUserData
from common.path.filepath import FilePath
from common.support.yaml_parse import YamlParser
from db_option.mysql.script_follow import Follower
from db_option.mysql.user_album import UserAlbum
from route.input_script.uri import ScriptUsersURI
from common.logging.logger import Logger

logger = Logger(__name__)

yp = YamlParser(FilePath.get_abspath_by_relation(__file__, "script_statics.yml"))


@pytest.mark.user
class TestScriptStatics(Assertion):
    # @classmethod
    # def setup_class(cls):
    #     cls.base = BaseAPI(role="self")

    @allure.title("话术用户粉丝/关注数统计信息查询")
    @CreateUserData()
    @pytest.mark.parametrize("inparam", yp.assemble_case("normal_validate"))
    def test_query_script_statics(self, inparam):
        follows, fans = [], []
        users = inparam["users"]
        base_user = users[0]
        try:
            upper_num = inparam["pre"]["upper_num"]
            fans_num = inparam["pre"]["fans_num"]
            read_num = inparam["pre"].get("read_num", 0)
            user_num = len(users)
            self.assertLess(upper_num, user_num)
            self.assertLess(fans_num, user_num)
            self.assertLessEqual(read_num, fans_num)  # 未读小于粉丝数
            # 登录
            base = BaseAPI(base_user.tel_no, base_user.login_pwd, client_type=inparam["data"]["client_type"])
            logger.info("- " * 5 + "添加关注信息" + " -" * 5)
            for user in users[1 : upper_num + 1]:
                logger.info(f"[{base_user.album_id}]添加关注：{user.album_id}")
                base.get(
                    ScriptUsersURI.ADD_FOLLOW.value,
                    params={"followAlbumId": user.album_id},
                    expect_errcode=0,
                    expect_msg="操作成功",
                )
                follows.append(user.album_id)

            logger.info("- " * 5 + "添加粉丝信息" + " -" * 5)
            # 反向获取数据
            update_album_ids = []
            for idx, user in enumerate(users[-1 : -(fans_num + 1) : -1], 1):
                fans_base = BaseAPI(user.tel_no, user.login_pwd)
                logger.info(f"[{user.album_id}]添加关注：{base_user.album_id}")
                fans_base.get(
                    ScriptUsersURI.ADD_FOLLOW.value,
                    params={"followAlbumId": base_user.album_id},
                    expect_errcode=0,
                    expect_msg="操作成功",
                )
                fans.append(user.album_id)
                # 更新已读状态
                if idx < read_num:
                    update_album_ids.append(user.album_id)
            if update_album_ids:
                logger.info(f"""更新为已读信息：[{" | ".join(update_album_ids)}]""")
                Follower.update_follow_info(
                    "n_is_read=1", album_ids=base_user.album_id, follow_album_ids=update_album_ids
                )
            logger.info("- " * 5 + "校验关注列表" + " -" * 5)
            self.verify_query_script_statics(base, inparam["data"])
        finally:
            logger.info("数据清理：解除关注关系")
            Follower.del_follow_info(album_ids=[base_user.album_id], follow_album_ids=follows)
            Follower.del_follow_info(album_ids=fans, follow_album_ids=[base_user.album_id])

    @allure.step("校验-话术用户粉丝/关注统计信息查询")
    def verify_query_script_statics(self, base, data: dict, expect_errcode: int = 0, expect_msg: str = "操作成功"):
        api_resp = base.get(
            ScriptUsersURI.USERNUM_QUERY.value,
            params=data,
            expect_errcode=expect_errcode,
            expect_msg=expect_msg,
        )
        new_follow, attend_num, follow_num = (
            api_resp["result"]["addFollowCount"],
            api_resp["result"]["attendNum"],
            api_resp["result"]["followNum"],
        )
        db_new_follow, db_attend_num, db_follow_num = self.query_script_statics(base)
        logger.info(f"接口查询结果：新增粉丝数：{new_follow}; 粉丝数：{attend_num}; 关注数：{follow_num}")
        logger.info(f"数据库查询结果：新增粉丝数：{db_new_follow}; 粉丝数：{db_attend_num}; 关注数：{db_follow_num}")
        self.assertListEqual([new_follow, attend_num, follow_num], [db_new_follow, db_attend_num, db_follow_num])

    @allure.step("数据库-话术用户粉丝/关注统计信息查询")
    def query_script_statics(self, base):
        attend_num, follow_infos = Follower.get_script_follower_info(album_id=base.album_id)
        follow_num, fans_infos = Follower.get_script_follower_info(follow_ids=[base.album_id])
        new_follow_cnt = 0
        if attend_num:
            # 查询关注用户
            album_ids = [i[2] for i in follow_infos]
            user_info_map = self.get_available_user(*album_ids)
            attend_num = len(set(album_ids) & set(user_info_map.keys()))

        if follow_num:
            # 查询粉丝用户
            follow_num = 0
            user_info_map = self.get_available_user(*[i[1] for i in fans_infos])
            if user_info_map:
                album_ids = user_info_map.keys()
                for item in fans_infos:
                    if item[1] in album_ids:
                        follow_num += 1
                    # 未读的新增粉丝数
                    if item[3] == 0:
                        new_follow_cnt += 1

        return new_follow_cnt, attend_num, follow_num

    @allure.step("数据库-获取有效的用户信息")
    def get_available_user(self, *album_ids):
        """
        获取有效的用户信息
        :param album_ids: 相册ID列表
        """
        album_info_map = UserAlbum.get_user_album_infos(*album_ids)
        user_info_map = UserAlbum.get_user_infos(*album_info_map.keys())
        return user_info_map
