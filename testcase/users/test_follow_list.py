# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2022/03/30 15:53
@Desc:
"""


from collections import OrderedDict
from operator import index
import time

import allure
import pytest
from common.assertion import Assertion
from common.core.base import BaseAPI, RequestContentType
from common.deco.user_deco import CreateUserData
from common.logging.logger import Logger
from common.path.filepath import FilePath
from common.support.yaml_parse import YamlParser
from db_option.mysql.script_follow import Follower
from db_option.mysql.script_statics import ScriptStatics
from db_option.mysql.user_album import UserAlbum
from route.input_script.uri import SriptUsersURI

logger = Logger(__name__)

yp = YamlParser(FilePath.get_abspath_by_relation(__file__, "follow_list.yml"))


@pytest.mark.user
class TestFollowList(Assertion):
    @classmethod
    def setup_class(cls):
        cls.base = BaseAPI(role="self")

    @allure.title("查询关注/粉丝列表")
    @pytest.mark.parametrize("inparam", yp.assemble_case("boundary_validate"))
    def test_boundary_query_follow_list(self, inparam):
        self.verify_follow_list(
            self.base, inparam["data"], inparam.get("expect_errcode", 0), inparam.get("expect_msg", "")
        )

    @allure.title("添加关注-常用场景校验")
    @CreateUserData()
    @pytest.mark.parametrize("inparam", yp.assemble_case("normal_validate"))
    def test_query_follow_list(self, inparam):
        follows, fans = [], []
        users = inparam["users"]
        base_user = users[0]
        try:
            upper_num = inparam["pre"]["upper_num"]
            fans_num = inparam["pre"]["fans_num"]
            delay = inparam['pre'].get('delay', 0)
            user_num = len(users)
            self.assertLess(upper_num, user_num)
            self.assertLess(fans_num, user_num)
            # 登录
            base = BaseAPI(base_user.tel_no, base_user.login_pwd)
            logger.info("- " * 5 + "添加关注信息" + " -" * 5)
            for user in users[1 : upper_num + 1]:
                logger.info(f"[{base_user.album_id}]添加关注：{user.album_id}")
                base.get(
                    SriptUsersURI.ADD_FOLLOW.value,
                    params={"followAlbumId": user.album_id},
                    expect_errcode=0,
                    expect_msg="操作成功",
                )
                follows.append(user.album_id)
                if delay:
                    time.sleep(delay)

            logger.info("- " * 5 + "添加粉丝信息" + " -" * 5)
            # 反向获取数据
            for user in users[-1 : -(fans_num + 1) : -1]:
                fans_base = BaseAPI(user.tel_no, user.login_pwd)
                logger.info(f"[{user.album_id}]添加关注：{base_user.album_id}")
                fans_base.get(
                    SriptUsersURI.ADD_FOLLOW.value,
                    params={"followAlbumId": base_user.album_id},
                    expect_errcode=0,
                    expect_msg="操作成功",
                )
                fans.append(user.album_id)
                if delay:
                    time.sleep(delay)
            logger.info("- " * 5 + "校验关注列表" + " -" * 5)
            self.verify_follow_list(base, inparam["data"]['follow'])
            logger.info("- " * 5 + "校验粉丝列表" + " -" * 5)
            self.verify_follow_list(base, inparam["data"]['fans'])
        finally:
            logger.info("数据清理：解除关注关系")
            Follower.del_follow_info(album_ids=[base_user.album_id], follow_album_ids=follows)
            Follower.del_follow_info(album_ids=fans, follow_album_ids=[base_user.album_id])

    @allure.step("校验-查询关注/粉丝列表")
    def verify_follow_list(self, base, data: dict, expect_errcode: int = 0, expect_msg: str = "操作成功"):
        api_resp = base.post(
            SriptUsersURI.FOLLOW_LIST_QUERY.value,
            json=data,
            content_type=RequestContentType.JSON.value,
            expect_errcode=expect_errcode,
            expect_msg=expect_msg,
        )
        if expect_errcode == 0:
            album_info, data_list = api_resp["result"]["albumInfo"], api_resp["result"]["dataList"]
            db_album_info, db_data_list = self.get_db_follow_info(
                base.album_id, data["queryType"], data.get("slipType", "1"), data.get("timestamp")
            )
            logger.info(f"接口查询结果：\n相册信息：{album_info}\n列表信息：{data_list}")
            logger.info(f"数据库查询结果：\n相册信息：{db_album_info}\n列表信息：{db_data_list}")
            self.assertEqual(album_info, db_album_info)
            self.assertListEqual(data_list, db_data_list)

    @allure.step("数据库-查询关注/粉丝列表")
    def get_db_follow_info(self, album_id, query_type: str, slip_type: str = "1", ts=None):
        """
        数据库中查询粉丝/关注信息
        :param album_id: 登录用户相册ID
        :param query_type: 查询类型 1：关注 | 2：粉丝
        :param slip_type: 滑动查询类型, 默认值: None
        :param ts: 时间戳, 默认值: None
        """
        album_ids = []
        if query_type == "1":
            _, infos = Follower.get_script_follower_info(
                album_id=album_id,
                sort_field="n_id",
                slip_type=slip_type,
                ts=ts,
                sort_mode="desc" if slip_type == "1" else "asc",
            )
            album_ids = OrderedDict([(i[2], [i[0], i[4]]) for i in infos])
        elif query_type == "2":
            _, infos = Follower.get_script_follower_info(
                follow_ids=[album_id],
                sort_field="n_id",
                slip_type=slip_type,
                ts=ts,
                sort_mode="desc" if slip_type == "1" else "asc",
                num=10 if ts else None
            )
            album_ids = OrderedDict([(i[1], [i[0], i[5]]) for i in infos])
        album_info_map = UserAlbum.get_user_album_infos(album_id, *album_ids.keys())
        user_info_map = UserAlbum.get_user_infos(album_id, *album_ids.keys())
        user_statics_map = ScriptStatics.get_user_statics(*album_ids.keys())
        album_info = album_info_map.get(album_id)
        user_info = user_info_map.get(album_id)
        db_album_info = {
            "albumId": album_info[0],
            "albumName": album_info[1],
            "albumIcon": album_info[2],
            "userId": user_info[1],
        }
        db_data_list = []
        for i_album_id, (n_id, sort_time) in album_ids.items():
            album_info = album_info_map.get(i_album_id)
            user_info = user_info_map.get(i_album_id)
            if album_info and user_info:
                info = user_statics_map.get(album_info[0])
                db_data_list.append(
                    {
                        "albumId": album_info[0],
                        "albumName": album_info[1],
                        "albumIcon": album_info[2],
                        "attendId": n_id,
                        "followAlbumId": album_id,
                        "scriptCount": "",
                        "scriptLastUpdateTime": int(info[2].timestamp() * 1000) if info else None,
                        "timestamp": int(sort_time.timestamp() * 1000) if query_type == "2" else sort_time,
                    }
                )
        return db_album_info, db_data_list
