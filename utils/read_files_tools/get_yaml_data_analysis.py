#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Get Yaml Data Analysis Module

This module provides get yaml data analysis functionality.
"""

"""
# @Time   : 2022/3/22 13:45
# @Author : txl
"""
import os
from enum import Enum
from typing import Dict, List, Text, Union

from utils import config
from utils.cache_process.cache_control import CacheHandler
from utils.other_tools.exceptions import ValueNotFoundError
from utils.other_tools.models import Method, RequestType, TestCase, TestCaseEnum
from utils.read_files_tools.yaml_control import GetYamlData


class CaseDataCheck:
    """
    yaml 数据解析, 判断数据填写是否符合规范
    """

    def __init__(self, file_path):
        self.file_path = file_path
        if os.path.exists(self.file_path) is False:
            raise FileNotFoundError("用例地址未找到")

        self.case_data = None
        self.case_id = None

    def _assert(self, attr: Text):
        assert attr in self.case_data.keys(), (
            f"用例ID为 {self.case_id} 的用例中缺少 {attr} 参数，请确认用例内容是否编写规范."
            f"当前用例文件路径：{self.file_path}"
        )

    def check_params_exit(self) -> None:
        """
        检查必填参数是否存在

        遍历TestCaseEnum中所有必填字段，检查当前用例数据中是否包含这些字段。
        """
        for enum in list(TestCaseEnum._value2member_map_.keys()):
            if enum[1]:
                self._assert(enum[0])

    def check_params_right(self, enum_name, attr) -> str:
        """
        检查参数值是否正确

        验证参数值是否在枚举类型的允许范围内。

        Args:
            enum_name: 枚举类型
            attr: 要检查的属性值

        Returns:
            转换为大写的属性值

        Raises:
            AssertionError: 当属性值不在允许范围内时抛出
        """
        _member_names_ = enum_name._member_names_
        assert attr.upper() in _member_names_, (
            f"用例ID为 {self.case_id} 的用例中 {attr} 填写不正确，"
            f"当前框架中只支持 {_member_names_} 类型."
            "如需新增 method 类型，请联系管理员."
            f"当前用例文件路径：{self.file_path}"
        )
        return attr.upper()

    @property
    def get_method(self) -> Text:
        """
        获取请求方法

        从用例数据中获取HTTP请求方法，并验证其有效性。

        Returns:
            验证后的请求方法（大写）
        """
        return self.check_params_right(Method, self.case_data.get(TestCaseEnum.METHOD.value[0]))

    @property
    def get_host(self) -> Text:
        """
        获取完整的请求URL

        将主机地址和接口路径拼接成完整的请求URL。

        Returns:
            完整的请求URL
        """
        host = self.case_data.get(TestCaseEnum.HOST.value[0]) + self.case_data.get(TestCaseEnum.URL.value[0])
        return host

    @property
    def get_request_type(self) -> str:
        """
        获取请求类型

        从用例数据中获取请求类型，并验证其有效性。

        Returns:
            验证后的请求类型（如：json、data、params等）
        """
        return self.check_params_right(RequestType, self.case_data.get(TestCaseEnum.REQUEST_TYPE.value[0]))

    @property
    def get_dependence_case_data(self) -> Union[None, list]:
        """
        获取依赖用例数据

        如果用例存在依赖关系，获取依赖用例的数据配置。

        Returns:
            依赖用例数据列表，如果无依赖则返回None

        Raises:
            AssertionError: 当存在依赖但缺少依赖数据时抛出
        """
        _dep_data = self.case_data.get(TestCaseEnum.DE_CASE.value[0])
        if _dep_data:
            assert self.case_data.get(TestCaseEnum.DE_CASE_DATA.value[0]) is not None, (
                f"程序中检测到您的 case_id 为 {self.case_id} 的用例存在依赖，但是 {_dep_data} 缺少依赖数据."
                f"如已填写，请检查缩进是否正确， 用例路径: {self.file_path}"
            )
        return self.case_data.get(TestCaseEnum.DE_CASE_DATA.value[0])

    @property
    def get_assert(self) -> dict:
        """
        获取断言数据

        从用例数据中获取断言配置，断言是必填项。

        Returns:
            断言配置字典

        Raises:
            AssertionError: 当用例缺少断言配置时抛出
        """
        _assert_data = self.case_data.get(TestCaseEnum.ASSERT_DATA.value[0])
        assert _assert_data is not None, f"用例ID 为 {self.case_id} 未添加断言，用例路径: {self.file_path}"
        return _assert_data

    @property
    def get_sql(self) -> Union[None, list]:
        """
        获取SQL查询配置

        从用例数据中获取SQL查询配置，用于数据库断言。

        Returns:
            SQL查询配置列表，如果数据库开关关闭或无SQL配置则返回None
        """
        _sql = self.case_data.get(TestCaseEnum.SQL.value[0])
        # 判断数据库开关为开启状态，并且sql不为空
        if config.mysql_db.switch and _sql is None:
            return None
        return _sql


class CaseData(CaseDataCheck):
    """
    用例数据处理器

    继承自CaseDataCheck，负责处理和转换YAML测试用例数据。
    将YAML格式的测试用例转换为标准的TestCase对象。

    主要功能：
    - 解析YAML测试用例数据
    - 验证用例数据完整性
    - 转换为TestCase标准格式
    - 支持批量处理多个用例
    - 处理用例间的依赖关系
    """

    def case_process(self, case_id_switch: Union[None, bool] = None) -> list:
        """
        处理测试用例数据

        从YAML文件中读取测试用例数据，进行验证和转换，生成标准的TestCase对象列表。

        Args:
            case_id_switch: 是否保留用例ID作为键名
                - True: 返回 [{case_id: TestCase}, ...]
                - False/None: 返回 [TestCase, ...]

        Returns:
            处理后的测试用例数据列表
        """
        data = GetYamlData(self.file_path).get_yaml_data()
        case_list = []
        for key, values in data.items():
            # 公共配置中的数据，与用例数据不同，需要单独处理
            if key != "case_common":
                self.case_data = values
                self.case_id = key
                super().check_params_exit()
                case_date = {
                    "method": self.get_method,
                    "is_run": self.case_data.get(TestCaseEnum.IS_RUN.value[0]),
                    "url": self.get_host,
                    "detail": self.case_data.get(TestCaseEnum.DETAIL.value[0]),
                    "headers": self.case_data.get(TestCaseEnum.HEADERS.value[0]),
                    "requestType": super().get_request_type,
                    "data": self.case_data.get(TestCaseEnum.DATA.value[0]),
                    "dependence_case": self.case_data.get(TestCaseEnum.DE_CASE.value[0]),
                    "dependence_case_data": self.get_dependence_case_data,
                    "current_request_set_cache": self.case_data.get(TestCaseEnum.CURRENT_RE_SET_CACHE.value[0]),
                    "sql": self.get_sql,
                    "assert_data": self.get_assert,
                    "setup_sql": self.case_data.get(TestCaseEnum.SETUP_SQL.value[0]),
                    "teardown": self.case_data.get(TestCaseEnum.TEARDOWN.value[0]),
                    "teardown_sql": self.case_data.get(TestCaseEnum.TEARDOWN_SQL.value[0]),
                    "sleep": self.case_data.get(TestCaseEnum.SLEEP.value[0]),
                }
                if case_id_switch is True:
                    case_list.append({key: TestCase(**case_date).dict()})
                else:
                    case_list.append(TestCase(**case_date).dict())

        return case_list


class GetTestCase:
    """
    测试用例获取器

    提供从缓存中获取测试用例数据的功能。
    用于获取已处理的测试用例数据，支持批量获取。

    主要功能：
    - 从缓存中获取测试用例数据
    - 支持批量获取多个用例
    - 处理用例ID列表
    - 返回标准格式的用例数据
    """

    @staticmethod
    def case_data(case_id_lists: List) -> List:
        """
        根据用例ID列表获取测试用例数据

        从缓存中批量获取指定ID的测试用例数据。

        Args:
            case_id_lists: 用例ID列表

        Returns:
            测试用例数据列表
        """
        case_lists = []
        for i in case_id_lists:
            _data = CacheHandler.get_cache(i)
            case_lists.append(_data)

        return case_lists
