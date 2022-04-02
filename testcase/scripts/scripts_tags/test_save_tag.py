# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2022/04/02 14:56
@Desc:
"""

import allure
import pytest
from common.assertion import Assertion
from common.core.base import BaseAPI, RequestContentType
from common.deco.user_deco import CreateUserData
from common.path.filepath import FilePath
from common.support.yaml_parse import YamlParser
from db_option.mysql.script_follow import Follower
from db_option.mysql.user_album import UserAlbum
from route.input_script.uri import ScriptTagURI
from common.logging.logger import Logger

logger = Logger(__name__)

yp = YamlParser(FilePath.get_abspath_by_relation(__file__, "save_tag.yml"))


@pytest.mark.user
class TestScriptStatics(Assertion):
    @classmethod
    def setup_class(cls):
        cls.base = BaseAPI(role="self")

    @pytest.mark.parametrize("inparam", yp.assemble_case("boundary_validate"))
    def test_save_tag(self, inparam):
        self.verify_save_tag(inparam['data'], inparam.get('expect_errcode'), inparam.get("expect_msg", "操作成功"))

    @allure.step("校验-保存话术标签")
    def verify_save_tag(self, data: dict, expect_errcode: int = 0, expect_msg: str = "操作成功"):
        api_resp = self.base.get(
            ScriptTagURI.SAVE_TAG.value,
            json=data,
            content_type=RequestContentType.JSON.value,
            expect_errcode=expect_errcode,
            expect_msg=expect_msg,
        )
        tag_id, tag_name = api_resp["result"]["tagId"], api_resp["result"]["tagName"]
        # logger.info(f"接口查询结果：)
        # logger.info(f"数据库查询结果：)
