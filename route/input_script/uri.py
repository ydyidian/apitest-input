# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2021/12/12 17:34
@Desc:
"""

from route.uri import URIEnum, WegoURI


class SriptUsersURI(URIEnum):
    USERNUM_QUERY = WegoURI("/script/api/v1/sriptConfig/queryConfig", desc="话术用户数查询")
    FOLLOW_LIST_QUERY = WegoURI("/script/api/v1/followInfo/queryFollowInfoList", desc="话术粉丝列表")
    CANCEL_FOLLOW = WegoURI("/script/api/v1/followInfo/cancelFollow", desc="取消关注/删除粉丝")
    ADD_FOLLOW = WegoURI("/script/api/v1/followInfo/addFollow", desc="关注相册")
    SORT_FOLLOW = WegoURI("/script/api/v1/followInfo/sortFollow", desc="粉丝排序")


class ScriptTagURI(URIEnum):
    SAVE_TAG = WegoURI("/script/api/v1/scriptTag/saveTag", desc="保存标签")
    DEL_TAG = WegoURI("/script/api/v1/scriptTag/deleteTag", desc="删除标签")
    QEURY_TAGLIST = WegoURI("/script/api/v1/scriptTag/queryList", desc="获取所有标签集合")
    QUERY_TAGLIST4SCRIPT = WegoURI("/script/api/v1/scriptTag/queryListForScriptInfoList", desc="获取标签集合「话术列表使用」")


class ScriptInfoURI(URIEnum):
    QUERY_SCRIPT_INFO = WegoURI("/script/api/v1/sriptInfo/queryScriptInfo", desc="话术信息查询")
    QUERY_SCRIPT_LIST = WegoURI("/script/api/v1/sriptInfo/queryScriptInfoList", desc="话术列表查询")
    SCRIPT_OPERATION = WegoURI("/script/api/v1/sriptInfo/upsertScriptInfo", desc="话术增、删、改、转发")
    SCRIPT_SEARCH = WegoURI("/script/api/v1/sriptInfo/queryScriptInfoListByTag", desc="话术查询")
    SCRIPT_IMPORT = WegoURI("/script/api/v1/sriptInfo/importScriptInfo", desc="话术批量导入")
