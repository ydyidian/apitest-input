# coding=utf8

# ＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊
#
# @Author: yiciu
# @Version: 1.0
# @Date: 2022/04/07 10:09 | 周四
# @Desc:
#
# ＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊


import allure
import pytest
from common.assertion import Assertion
from common.core.base import BaseAPI, RequestContentType
from common.path.filepath import FilePath
from common.support.yaml_parse import YamlParser
from db_option.mysql.script_tag import ScriptTag
from route.input_script.uri import ScriptTagURI
from common.logging.logger import Logger

logger = Logger(__name__)

yp = YamlParser(FilePath.get_abspath_by_relation(__file__, "del_tag.yml"))


@allure.epic("话术")
@allure.feature("话术标签")
@pytest.mark.script
class TestDelScriptTag(Assertion):
    @classmethod
    def setup_class(cls):
        cls.base = BaseAPI(role="self")

    def teardown_method(self):
        if getattr(self, "del_inf", None):
            for item in self.del_inf:
                ScriptTag.del_script_tag_info(*item)

    @allure.title("保存标签-边界校验")
    @pytest.mark.parametrize("inparam", yp.assemble_case("boundary_validate"))
    def test_del_tag_boundary(self, inparam):
        self.verify_del_tag(inparam["data"], inparam["expect_errcode"], inparam["expect_msg"])

    @allure.title("保存标签-常规校验")
    @pytest.mark.parametrize("inparam", yp.assemble_case("normal_validate"))
    def test_del_tag_normal(self, inparam):
        api_resp = self.base.post(
            ScriptTagURI.SAVE_TAG.value, json=inparam["data"], content_type=RequestContentType.JSON.value
        )
        tag_id = api_resp["result"]["tagId"]
        self.del_inf = [(self.base.album_id, tag_id)]
        cnt = inparam['data'].get('del_count') or 1
        for _ in range(cnt):
            self.verify_del_tag(eval(inparam["data"] % tag_id), inparam["expect_errcode"], inparam["expect_msg"])

    @allure.step("校验-删除话术标签")
    def verify_del_tag(self, data: dict, expect_errcode: int = 0, expect_msg: str = "操作成功"):
        self.base.post(
            ScriptTagURI.DEL_TAG.value,
            json=data,
            content_type=RequestContentType.JSON.value,
            expect_errcode=expect_errcode,
            expect_msg=expect_msg,
        )
        tag_id = data.get("tagId")
        if tag_id:
            num, infos = ScriptTag.get_script_tag_info(self.base.album_id, id_=tag_id, status=-1)
            logger.info(f"数据库查询结果：{infos}")
            self.assertIn(num, (0, 1))
