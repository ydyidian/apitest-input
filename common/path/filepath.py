# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2022/03/25 16:20
@Desc: FilePath
"""


import os

class FilePath(object):  # 文件路径类FilePath

    sep = os.path.altsep if os.name == "nt" else os.path.sep

    @staticmethod
    def get_abspath_by_relation(abspath, relative_path):
        """
        根据参考文件的绝对路径 + 相对路径获取指定文件的绝对路径
            ➤ 主要解决yaml文件写入相对路径导致查询不到文件的问题「abspath传入__file__即可」
        :param abspath: 参考文件的绝对路径
        :param relative_path: 相对路径
        :return: 指定文件的绝对路径
        """
        return os.path.abspath(os.path.join(os.path.dirname(abspath), relative_path))
