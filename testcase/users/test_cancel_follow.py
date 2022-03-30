# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2022/03/29 15:49
@Desc:
"""


import allure
import pytest
from api.user import UserManager
from common.assertion import Assertion
from common.core.base import BaseAPI, RequestContentType
from common.deco.user_deco import CreateUserData
from common.path.filepath import FilePath
from common.support.yaml_parse import YamlParser
from db_option.mysql.script_follow import Follower
from route.input_script.uri import SriptUsersURI

yp = YamlParser(FilePath.get_abspath_by_relation(__file__, "cancel_follow.yml"))


class TestCancelFollow(Assertion):
    @classmethod
    def setup_class(cls):
        cls.base = BaseAPI(role="self")

    @allure.title("取消关注-边界校验")
    @pytest.mark.parametrize("inparam", yp.assemble_case("boundary_validate"))
    def test_boundary_cancel_follow(self, inparam):
        self.verify_cancel_follow(inparam["data"], inparam.get("expect_errcode", 0), inparam.get("expect_msg", ""))

    @allure.title("取消关注-常用场景校验")
    @pytest.mark.parametrize("inparam", yp.assemble_case("normal_validate"))
    def test_cancel_follow(self, inparam):
        users = UserManager.create_multi_users(
            inparam["data"]["pre"]["user_num"], inparam["data"]["pre"].get("vip_infos")
        )
        try:
            uppers_album_id = users[0].album_id
            # 添加关注
            self.base.get(SriptUsersURI.ADD_FOLLOW.value, params={"followAlbumId": uppers_album_id})
            _, infos = Follower.get_script_follower_info(album_id=self.base.album_id, follow_ids=[uppers_album_id])
            self.verify_cancel_follow({"attendId": infos[0][0]})
        finally:
            UserManager.do_delete_user(*users)

    def verify_cancel_follow(self, data: dict, expect_errcode: int = 0, expect_msg: str = "操作成功"):
        self.base.post(
            SriptUsersURI.CANCEL_FOLLOW.value,
            json=data,
            content_type=RequestContentType.JSON.value,
            expect_errcode=expect_errcode,
            expect_msg=expect_msg,
        )
        num, _ = Follower.get_script_follower_info(n_id=[data["attendId"]])
        self.assertEqual(num, 0)
