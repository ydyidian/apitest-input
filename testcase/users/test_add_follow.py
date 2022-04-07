# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2022/03/28 14:32
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
from route.input_script.uri import ScriptUsersURI
from common.logging.logger import Logger

logger = Logger(__name__)

yp = YamlParser(FilePath.get_abspath_by_relation(__file__, "add_follow.yml"))


@allure.epic("用户")
@allure.feature("添加关注")
@pytest.mark.user
class TestAddFollow(Assertion):
    @classmethod
    def setup_class(cls):
        cls.base = BaseAPI(role="self")

    @allure.title("添加关注-边界校验")
    @pytest.mark.parametrize("inparam", yp.assemble_case("boundary_validate"))
    def test_boundary_add_follow(self, inparam):
        self.verify_add_follow(inparam["data"], inparam.get("expect_errcode", 0), inparam.get("expect_msg", ""))

    @allure.title("添加关注-常用场景校验")
    @CreateUserData()
    @pytest.mark.parametrize("inparam", yp.assemble_case("normal_validate"))
    def test_add_follow(self, inparam):
        follow_album_ids = []
        try:
            for i in range(inparam["data"]["count"]):
                album_id = inparam["users"][0].album_id
                follow_album_ids.append(album_id)
                self.verify_add_follow(
                    {"followAlbumId": album_id}, inparam.get("expect_errcode", 0), inparam.get("expect_msg", "")
                )
        finally:
            logger.info(f"清理关注数据：当前用户[{self.base.album_id}], 粉丝[{'|'.join(follow_album_ids)}]")
            Follower.del_follow_info(album_ids=[self.base.album_id], follow_album_ids=follow_album_ids)

    @allure.step("校验-添加关注")
    def verify_add_follow(self, data: dict, expect_errcode: int = 0, expect_msg: str = "操作成功"):
        self.base.get(
            ScriptUsersURI.ADD_FOLLOW.value,
            params=data,
            expect_errcode=expect_errcode,
            expect_msg=expect_msg,
        )
        num, _ = Follower.get_script_follower_info(album_id=self.base.album_id, follow_ids=[data["followAlbumId"]])
        self.assertEqual(num, 1 if expect_errcode == 0 else 0)
