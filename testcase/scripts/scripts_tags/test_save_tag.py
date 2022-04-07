# coding=utf8

# ＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊
#
# @Author: yiciu
# @Version: 1.0
# @Date: 2022/04/06 10:19 | 周三
# @Desc:
#
# ＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊


import allure
import pytest
from common.assertion import Assertion
from common.core.base import BaseAPI, RequestContentType
from common.deco.user_deco import CreateUserData
from common.path.filepath import FilePath
from common.support.yaml_parse import YamlParser
from db_option.mysql.script_tag import ScriptTag
from route.input_script.uri import ScriptTagURI
from common.logging.logger import Logger

logger = Logger(__name__)

yp = YamlParser(FilePath.get_abspath_by_relation(__file__, "save_tag.yml"))


@allure.epic("话术")
@allure.feature("保存话术标签")
@pytest.mark.script
class TestAddScriptTag(Assertion):
    @classmethod
    def setup_class(cls):
        cls.base = BaseAPI(role="self")

    def teardown_method(self):
        if getattr(self, "del_inf", None):
            for item in self.del_inf:
                ScriptTag.del_script_tag_info(*item)

    @allure.step("保存标签-边界校验")
    @pytest.mark.parametrize("inparam", yp.assemble_case("boundary_validate"))
    def test_save_tag_boundary(self, inparam):
        self.verify_save_tag(self.base, inparam["data"], inparam["expect_errcode"], inparam["expect_msg"])

    @allure.step("保存标签-新增/编辑校验")
    @pytest.mark.parametrize("inparam", yp.assemble_case("edit_validate"))
    def test_save_tag_edit(self, inparam):
        send_cnt = inparam["data"].get("send_cnt", 1)
        data = inparam["data"]["data"]
        update = inparam["data"].get("udpate")
        if update:
            api_resp = self.base.post(
                ScriptTagURI.SAVE_TAG.value, json=data, content_type=RequestContentType.JSON.value
            )
            data.update(tagId=api_resp["result"]["tagId"], **update)
        for _ in range(send_cnt):
            self.verify_save_tag(self.base, data)

    @allure.step("保存标签-标签覆盖校验")
    @pytest.mark.parametrize("inparam", yp.assemble_case("mix_validate"))
    def test_save_tag_mix(self, inparam):
        data_lst = inparam["data"]["data"]
        self.assertTrue(isinstance(data_lst, list) and len(data_lst) > 1)
        data1, data2 = data_lst[0], data_lst[1]
        api_resp = self.base.post(ScriptTagURI.SAVE_TAG.value, json=data1, content_type=RequestContentType.JSON.value)
        api_resp2 = self.base.post(ScriptTagURI.SAVE_TAG.value, json=data2, content_type=RequestContentType.JSON.value)
        self.del_inf = [
            (self.base.album_id, api_resp["result"]["tagId"]),
            (self.base.album_id, api_resp2["result"]["tagId"]),
        ]
        data = {"tagId": api_resp["result"]["tagId"], "tagName": api_resp2["result"]["tagName"]}
        self.verify_save_tag(self.base, data, inparam["expect_errcode"], inparam["expect_msg"])

    @allure.step("保存标签-修改已删除校验")
    @pytest.mark.parametrize("inparam", yp.assemble_case("mix2_validate"))
    def test_save_tag_mix2(self, inparam):
        data = inparam["data"]
        self.assertTrue("tagId" not in data and "tagName" in data)
        api_resp = self.base.post(ScriptTagURI.SAVE_TAG.value, json=data, content_type=RequestContentType.JSON.value)
        tag_id = api_resp["result"]["tagId"]
        # 修改标签状态为已删除
        ScriptTag.update_script_tag_info("n_status=-1", self.base.album_id, id_=tag_id)
        self.del_inf = [(self.base.album_id, tag_id)]
        data = {"tagId": tag_id, "tagName": data["tagName"] + "edit"}
        self.verify_save_tag(self.base, data, inparam["expect_errcode"], inparam["expect_msg"])

    @allure.step("校验-保存话术标签")
    def verify_save_tag(self, base, data: dict, expect_errcode: int = 0, expect_msg: str = "操作成功"):
        api_resp = base.post(
            ScriptTagURI.SAVE_TAG.value,
            json=data,
            content_type=RequestContentType.JSON.value,
            expect_errcode=expect_errcode,
            expect_msg=expect_msg,
        )
        if expect_errcode == 0:
            tag_id, tag_name = api_resp["result"]["tagId"], api_resp["result"]["tagName"]
            in_tag_id, in_tag_name = data.get("tagId"), data["tagName"]
            self.del_inf = [(base.album_id, tag_id)]
            if in_tag_id:
                self.assertEqual(tag_id, in_tag_id)
                num, infos = ScriptTag.get_script_tag_info(base.album_id, id_=in_tag_id, name=in_tag_name, status=0)
            else:
                num, infos = ScriptTag.get_script_tag_info(base.album_id, name=in_tag_name, status=0)
            self.assertEqual(num, 1)
            db_tag_name = infos[0][2]
            logger.info(f"接口查询结果：{tag_name}")
            logger.info(f"数据库查询结果：{db_tag_name}")
            self.assertMultiEqual(tag_name, db_tag_name, in_tag_name)
