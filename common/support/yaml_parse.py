# coding=utf8

"""
@Author: yiciu
@Version: 1.0
@Date: 2022/03/25 17:35
@Desc: ymal文件转换案例以及添加标签操作
支持以下功能：
    - 在yaml文件中添加案例标签「需要写入markers字段！！！名字别写错了」
    - 可以在yaml中使用python表达式，yaml格式：{% random.random() %}
    - 支持传入自定义变量或者对象属性「通过字典传入」，yaml格式：{{name}}或者{{person.name}}
    - id和data字段是必填项！其他字段可以自定义添加

注意格式：
不管是{{}}或者是{%%}，如果变量或者表达式左侧加入空格，变量或者表达式右侧也需要对应匹配
如: {{name}} {{ name }} 但是{{name }}或者{{ name}}则匹配不到，请注意格式！！！;  {%%}同理

yaml格式示例：

# 分区1用例
kps:
  - id: '测试用例用例1'
    markers:
      - nice
      - smoke
    data: {age: {% random.randint(5, 20) %}, name: {{person.name}}}
    expect_errmsg: "商品内容与商品图片必须录入一项"
  # 无标签
  - id: '测试用例用例2'
    data: {age: {% random.randint(5, 20) %}, name: {{name}}}
    expect_errmsg: "商品内容与商品图片必须录入一项"

# 分区2用例
bps：
  # 没有错误信息
  - id: '测试用例用例3'
    markers: [smoke]
    data: {age: {%random.randint(5, 20)%}}
"""


import os
import re

import pytest
import yaml
from yaml.parser import ParserError


expression_pattern = "{%(?P<pre>\s)?(?P<expression>.+)(?(pre)\s)%}"
variable_pattern = "{{(?P<pre>\s)?(?P<variable>\w+(\.\w+)*)(?(pre)\s)}}"


def get_yaml_data(file_path):
    """
    获取yaml_data数据
    :param file_path: 文件路径「包括文件名」
    :return: data
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        return data


class YamlParser(object):
    def __init__(self, path, **kwargs) -> None:
        if os.path.splitext(path)[1] not in (".yaml", ".yml"):
            raise NameError("请确认文件后缀以yaml或yml结尾！")
        self._path = path
        self._data = self._get_yaml_data(path, **kwargs)

    def _get_yaml_data(self, path, **kwargs):
        """
        解析yaml文件并格式化

        :param path: yaml文件路径
        :return: yaml数据
        """
        with open(path, "r", encoding="utf-8") as f:
            fs = f.read()

        # 新检索变量方式
        def fill_variable(match):
            matched_str = match.group("variable")
            fields = matched_str.split(".", 1)
            if len(fields) == 1:
                return str(kwargs[fields[0]])
            else:
                # 加载变量
                locals()[fields[0]] = kwargs[fields[0]]
                return f"{eval(matched_str)}"

        def fill_expression(match):
            expression = match.group("expression")
            local_modules = set()
            for i in re.findall("(\w+)(\.\w+)+\(", expression):
                module_name = i[0]
                if module_name not in local_modules:
                    locals()[module_name] = __import__(module_name)
                    local_modules.add(module_name)
            return str(eval(expression))

        # 填充变量
        if "{{" in fs and "}}" in fs:
            fs = re.sub(variable_pattern, fill_variable, fs)
        # 填充表达式
        if "{%" in fs and "%}" in fs:
            fs = re.sub(expression_pattern, fill_expression, fs)
        try:
            data = yaml.load(fs, Loader=yaml.FullLoader)
        except ParserError as e:
            raise ValueError("yaml文件格式错误！请检查！")
        return data

    def assemble_case(self, node_name):
        """
        处理案例数据，添加id以及标签信息

        :param node_name: 根节点名称
        :return: 处理后的案例列表
        """
        case_datas = self._data[node_name]
        if len(case_datas) == 0:
            raise ValueError("获取案例列表失败，请确认yaml文件以及jsonpath输入正确！")
        elif not isinstance(case_datas, list):
            raise TypeError("案例列表类型错误！")
        case_list = []
        id_prefix = 1
        for data in case_datas:
            kw = {}
            if "id" not in data:
                raise ValueError("测试案例中需要id「测试内容」参数，请指定id名称！")
            if "data" not in data:
                raise ValueError("测试案例中需要data「测试入参」参数，请传入data！")
            # ID添加前缀，保证案例自上而下的执行「方法级」
            kw.update(id=f'{id_prefix:03d}-{data.pop("id")}')
            id_prefix += 1
            if "markers" in data:
                markers = data.pop("markers")
                if not isinstance(markers, list):
                    raise ValueError("markers传入类型错误！请确认传入的是列表类型！")
                kw.update(marks=[getattr(pytest.mark, marker) for marker in markers])
            case_list.append(pytest.param(data, **kw))
        return case_list


if __name__ == "__main__":
    yp = YamlParser("xxx.yaml")
    yp.assemble_case("Nodename")
