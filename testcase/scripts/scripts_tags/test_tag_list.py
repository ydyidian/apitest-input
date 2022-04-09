# coding=utf8

# ＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊
#
# @Author: yiciu
# @Version: 1.0
# @Date: 2022/04/08 10:23 | 周五
# @Desc: queryListForScriptInfoList[获取标签集合 - 话术列表使用]
#
# ＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊


from datetime import datetime

import allure
import pytest
from common.assertion import Assertion
from common.core.base import BaseAPI, RequestContentType
from common.deco.user_deco import CreateUserData
from common.logging.logger import Logger
from common.path.filepath import FilePath
from common.support.yaml_parse import YamlParser
from db_option.mysql.script_tag import ScriptTag
from route.input_script.uri import ScriptTagURI

logger = Logger(__name__)

yp = YamlParser(FilePath.get_abspath_by_relation(__file__, "tag_list.yml"))


@allure.epic("话术")
@allure.feature("查询话术标签集合-话术列表使用")
@pytest.mark.script
class TestScriptTagList(Assertion):
    def teardown_method(self):
        base = getattr(self, "base", None)
        if base:
            ScriptTag.del_script_tag_info(base.album_id)

    @allure.title("查询标签列表-场景校验")
    @CreateUserData()
    @pytest.mark.parametrize("inparam", yp.assemble_case("normal_validate"))
    def test_query_tag_list_major(self, inparam):
        user = inparam["users"][0]
        base = BaseAPI(user.tel_no, user.login_pwd)
        scripts = inparam["pre"].get("script")
        if scripts:
            now = datetime.now().strftime("%F %X")
            self.base = base
            logger.info(scripts, desc="数据准备：")
            # 新建标签修改时间为2000-01-01 00:00:00
            ScriptTag.insert_script_tag_info(
                (base.album_id, *s, "2000-01-01 00:00:00", now, now) if len(s) == 3 else (base.album_id, *s, now, now)
                for s in scripts
            )
        self.verify_query_tag_list(base, inparam["data"])

    @allure.step("校验-查询标签列表")
    def verify_query_tag_list(self, base, data):
        api_resp = base.post(
            ScriptTagURI.QUERY_TAGLIST4SCRIPT.value, json=data, content_type=RequestContentType.JSON.value
        )
        api_tags = api_resp["result"]["tagList"]
        _, tags = ScriptTag.get_script_tag_info(
            base.album_id, status=0, order_by="t_script_last_operation_time", order="desc"
        )
        # 如果有标签的话，那就在首部返回一个全部的标签
        db_tags = (
            [{"tagId": -1, "tagName": "全部"}] + [{"tagId": tag.n_id, "tagName": tag.c_name} for tag in tags]
            if tags
            else []
        )
        logger.info(f"{api_tags}", desc="接口查询结果")
        logger.info(f"{db_tags}", desc="数据库查询结果")
        self.assertListEqual(db_tags, api_tags)
