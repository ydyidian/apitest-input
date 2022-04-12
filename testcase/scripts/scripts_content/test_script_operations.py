# coding=utf8

# ＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊
#
# @Author: yiciu
# @Version: 1.0
# @Date: 2022/04/11 09:43 | 周一
# @Desc:
#
# ＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊＊


import allure
import pytest
from common.assertion import Assertion
from common.core.base import BaseAPI, RequestContentType
from common.dbs.es_client import ElasticIndex, ElasticPool
from common.logging.logger import Logger
from common.path.filepath import FilePath
from common.support.yaml_parse import YamlParser
from db_option.mysql.script_tag import ScriptTag
from db_option.mysql.user_album import UserAlbum
from route.input_script.uri import ScriptInfoURI

logger = Logger(__name__)

yp = YamlParser(FilePath.get_abspath_by_relation(__file__, "script_option.yml"))


@allure.epic("话术")
@allure.feature("话术内容操作[增删改|转存]")
@pytest.mark.script
class TestScriptOpterations(Assertion):
    @classmethod
    def setup_class(cls):
        cls.es_client = ElasticPool.get_client()
        cls.base = BaseAPI(role="self")
        cls.base_upper = BaseAPI(role="parent")
        cls.scs = []

    def teardown_method(self):
        if self.scs:
            for album_id, script_id in self.scs:
                _, res = ElasticPool.get_hits_info_from_result(
                    self.es_client.search(
                        body={
                            "query": {
                                "bool": {
                                    "must": [
                                        {"term": {"albumId": {"value": album_id}}},
                                        {"term": {"scriptId": {"value": script_id}}},
                                    ]
                                }
                            }
                        },
                        index=ElasticIndex.SCRIPT_INFO.value,
                    )
                )
                for i in res:
                    self.es_client.delete(index=ElasticIndex.SCRIPT_INFO.value, id=i["_id"])
            self.scs = []  # 重置

    @allure.title("话术操作-边界校验")
    @pytest.mark.parametrize("inparam", yp.assemble_case("boundary_validate"))
    def test_script_operation_boundary(self, inparam):
        self.verify_script_operation(self.base, inparam["data"], inparam["expect_errcode"], inparam["expect_msg"])

    @allure.title("话术操作-新增场景校验")
    @pytest.mark.parametrize("inparam", yp.assemble_case("add_validate"))
    def test_script_operation_add(self, inparam):
        self.verify_script_operation(self.base, inparam["data"])

    @allure.title("话术操作-修改场景校验")
    @pytest.mark.parametrize("inparam", yp.assemble_case("modify_validate"))
    def test_script_operation_modify(self, inparam):
        api_resp = self.base.post(
            ScriptInfoURI.SCRIPT_OPERATION.value,
            json=inparam["data"]["pre"],
            content_type=RequestContentType.JSON.value,
        )
        script_id = api_resp["result"]["scriptId"]
        self.verify_script_operation(self.base, eval(inparam["data"]["data"] % script_id))

    @allure.title("话术操作-转存场景校验")
    @pytest.mark.parametrize("inparam", yp.assemble_case("share_validate"))
    def test_script_operation_share(self, inparam):
        api_resp = self.base_upper.post(
            ScriptInfoURI.SCRIPT_OPERATION.value,
            json=inparam["data"]["pre"],
            content_type=RequestContentType.JSON.value,
        )
        script_id = api_resp["result"]["scriptId"]
        self.scs.append((self.base_upper.album_id, script_id))
        self.verify_script_operation(self.base, eval(inparam["data"]["data"] % (self.base_upper.album_id, script_id)))

    @allure.title("话术操作-删除场景校验")
    @pytest.mark.parametrize("inparam", yp.assemble_case("del_validate"))
    def test_script_operation_del(self, inparam):
        api_resp = self.base.post(
            ScriptInfoURI.SCRIPT_OPERATION.value,
            json=inparam["data"]["pre"],
            content_type=RequestContentType.JSON.value,
        )
        script_id = api_resp["result"]["scriptId"]
        self.verify_script_operation(self.base, eval(inparam["data"]["data"] % script_id))

    @allure.step("校验-话术内容操作[增删改|转存]")
    def verify_script_operation(self, base, data: dict, expect_errcode: int = 0, expect_msg: str = "操作成功"):
        api_resp = base.post(
            ScriptInfoURI.SCRIPT_OPERATION.value,
            json=data,
            content_type=RequestContentType.JSON.value,
            expect_errcode=expect_errcode,
            expect_msg=expect_msg,
        )
        if expect_errcode != 0:
            return
        api_sc_info = api_resp["result"]
        self.scs.append((base.album_id, api_sc_info["scriptId"]))
        opt_type = data["operateType"]
        body = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"albumId": {"value": base.album_id}}},
                        {"term": {"scriptId": {"value": data.get("scriptId") or api_sc_info["scriptId"]}}},
                    ]
                }
            }
        }
        # 确保查到修改后的话术
        if opt_type == "2":
            body["query"]["bool"]["must"].append(
                {"multi_match": {"query": data["scriptValue"], "type": "phrase", "fields": ["scriptValue"]}}
            )
        logger.info(body, desc="es查询话术信息语句")
        if opt_type in ("1", "2", "3"):
            hits, res = ElasticPool.wait_for_exist(body=body, index=ElasticIndex.SCRIPT_INFO.value)
            album = UserAlbum.get_user_album_infos(base.album_id)[base.album_id]
            source = res[0]["_source"]
            tag_info = [
                {"tagId": i, "tagName": ScriptTag.get_script_tag_info(base.album_id, i)[1][0].c_name}
                for i in source.get("tags") or []
            ]
            db_script_info = {
                "albumIcon": album.c_album_icon,
                "albumId": album.c_album_id,
                "albumName": album.c_album_name,
                "imageUrl": data.get("imageUrl", ""),
                "isMySript": True,
                "lastUseTime": source["lastUseTime"],
                "openStatus": source["openStatus"],
                "scriptId": source["scriptId"],
                "scriptValue": source["scriptValue"],
                "tags": tag_info,
            }
            self.assertEqual(hits, 1)
            logger.info(api_sc_info, desc="接口查询结果")
            logger.info(db_script_info, desc="ES查询结果")
            self.assertDictEqual(api_sc_info, db_script_info)  # 校验接口下发数据与数据库一致
            # 预期结果构造
            expect_data = {
                "albumIcon": album.c_album_icon,
                "albumId": album.c_album_id,
                "albumName": album.c_album_name,
                "imageUrl": data.get("imageUrl", ""),
                "isMySript": True,
                "openStatus": data.get("openStatus", 0),
            }
            if "scriptId" in data:
                expect_data.update(scriptId=data["scriptId"])
            if "scriptValue" in data:
                expect_data.update(scriptValue=data["scriptValue"])
            if "tags" in data:
                tags = data["tags"]
                for tag in tags:
                    # 验证标签不重复
                    self.assertEqual(
                        ScriptTag.get_script_tag_info(base.album_id, name=tag["tagName"], search_mode="equal")[0], 1
                    )
            # 校验数据保存正常
            self.assertDictContainsSubset(expect_data, db_script_info)
        else:
            hits, res = ElasticPool.wait_for_not_exist(body=body, index=ElasticIndex.SCRIPT_INFO.value, timeout=2000)
            # delete
            self.assertEqual(hits, 0)
            self.assertEqual(res, [])
