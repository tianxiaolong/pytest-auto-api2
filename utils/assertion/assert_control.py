#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Assert Control Module

This module provides assert control functionality.
"""

"""
断言控制模块
提供接口响应断言和数据库断言功能，支持多种断言类型和数据提取方式

主要功能：
- JSON响应数据断言
- 数据库查询结果断言
- 请求参数断言
- 支持JSONPath数据提取
- 支持多种断言方法（等于、不等于、包含等）

@Time   : 2022/3/28 14:18
@Author : txl
@Update : 2023-12-20 优化注释和类型注解
"""
from jsonpath import jsonpath
import ast
import json

from typing import Any, Dict, List, Text, Union

from utils import config
from utils.assertion import assert_type
from utils.logging_tool.log_control import ERROR, WARNING
from utils.other_tools.exceptions import AssertTypeError, JsonpathExtractionFailed, SqlNotFound
from utils.other_tools.models import AssertMethod, load_module_functions
from utils.read_files_tools.regular_control import cache_regular


class AssertUtil:
    """
    断言工具类

    提供断言数据处理和验证的基础功能，包括：
    - 断言数据解析和验证
    - JSONPath数据提取
    - 数据库断言数据处理
    - 响应数据和请求数据断言
    """

    def __init__(
        self, assert_data: Any, sql_data: Any, request_data: Any, response_data: str, status_code: int
    ) -> None:
        """
        初始化断言工具

        Args:
            assert_data: 断言配置数据，包含断言类型、期望值等
            sql_data: SQL查询结果数据，用于数据库断言
            request_data: 请求参数数据
            response_data: 接口响应数据（JSON字符串）
            status_code: HTTP响应状态码
        """
        self.response_data = response_data
        self.request_data = request_data
        self.sql_data = sql_data
        self.assert_data = assert_data
        self.sql_switch = config.mysql_db.switch  # 数据库开关状态
        self.status_code = status_code

    @staticmethod
    def literal_eval(attr: Any) -> Any:
        """
        安全地解析字符串表达式为Python对象

        Args:
            attr: 要解析的属性值

        Returns:
            解析后的Python对象
        """
        return ast.literal_eval(cache_regular(str(attr)))

    @property
    def get_assert_data(self) -> Dict[str, Any]:
        """
        获取解析后的断言数据

        Returns:
            断言数据字典，包含type、value、jsonpath等字段

        Raises:
            AssertionError: 当断言数据为None时抛出
        """
        assert self.assert_data is not None, f"'{self.__class__.__name__}' 类必须包含 'assert_data' 属性"
        return ast.literal_eval(cache_regular(str(self.assert_data)))

    @property
    def get_type(self) -> str:
        """
        获取断言类型名称

        Returns:
            断言类型名称（如：equals、not_equals、contains等）

        Raises:
            AssertionError: 当断言数据中缺少type字段时抛出
        """
        assert "type" in self.get_assert_data.keys(), f"断言数据 '{self.get_assert_data}' 中缺少 'type' 属性"

        # 获取断言类型对应的枚举值名称
        name = AssertMethod(self.get_assert_data.get("type")).name
        return name

    @property
    def get_value(self) -> Any:
        """
        获取断言期望值

        Returns:
            断言的期望值

        Raises:
            AssertionError: 当断言数据中缺少value字段时抛出
        """
        assert "value" in self.get_assert_data.keys(), f"断言数据 '{self.get_assert_data}' 中缺少 'value' 属性"
        return self.get_assert_data.get("value")

    @property
    def get_jsonpath(self) -> str:
        """
        获取JSONPath表达式

        Returns:
            用于数据提取的JSONPath表达式

        Raises:
            AssertionError: 当断言数据中缺少jsonpath字段时抛出
        """
        assert "jsonpath" in self.get_assert_data.keys(), f"断言数据 '{self.get_assert_data}' 中缺少 'jsonpath' 属性"
        return self.get_assert_data.get("jsonpath")

    @property
    def get_assert_type(self) -> str:
        """
        获取断言类型标识

        Returns:
            断言类型标识字符串（如：SQL、R_SQL、D_SQL等）

        Raises:
            AssertionError: 当断言数据中缺少AssertType字段时抛出
        """
        assert (
            "AssertType" in self.get_assert_data.keys()
        ), f"断言数据 '{self.get_assert_data}' 中缺少 'AssertType' 属性"
        return self.get_assert_data.get("AssertType")

    @property
    def get_message(self):
        """
        获取断言描述，如果未填写，则返回 `None`
        :return:
        """
        return self.get_assert_data.get("message", None)

    @property
    def get_sql_data(self) -> Any:
        """
        获取SQL查询结果数据

        从SQL查询结果中提取用于断言的数据。
        支持数据类型转换和JSONPath数据提取。

        Returns:
            提取的SQL数据，可能是单个值或列表

        Raises:
            AssertionError: 当SQL语句为空或数据提取失败时抛出
        """
        # 判断数据库开关为开启，并需要数据库断言的情况下，未编写sql，则抛异常
        if self.sql_switch_handle:
            assert self.sql_data != {"sql": None}, "请在用例中添加您要查询的SQL语句。"

        # 处理 mysql查询出来的数据类型如果是bytes类型，转换成str类型
        if isinstance(self.sql_data, bytes):
            return self.sql_data.decode("utf=8")

        sql_data = jsonpath(self.sql_data, self.get_value)
        assert sql_data is not False, f"数据库断言数据提取失败，提取对象: {self.sql_data} , 当前语法: {self.get_value}"
        if len(sql_data) > 1:
            return sql_data
        return sql_data[0]

    @staticmethod
    def functions_mapping() -> Dict[str, Any]:
        """
        获取断言方法映射

        从断言类型模块中加载所有可用的断言方法。

        Returns:
            断言方法名称到函数对象的映射字典
        """
        return load_module_functions(assert_type)

    @property
    def get_response_data(self) -> Dict[str, Any]:
        """
        获取解析后的响应数据

        将JSON字符串格式的响应数据解析为Python字典对象。

        Returns:
            解析后的响应数据字典

        Raises:
            JSONDecodeError: 当响应数据不是有效JSON格式时抛出
        """
        return json.loads(self.response_data)

    @property
    def sql_switch_handle(self):
        """
        判断数据库开关，如果未开启，则打印断言部分的数据
        :return:
        """
        if self.sql_switch is False:
            WARNING.logger.warning("检测到数据库状态为关闭状态，程序已为您跳过此断言，断言值:%s" % self.get_assert_data)
        return self.sql_switch

    def _assert(self, check_value: Any, expect_value: Any, message: Text = ""):

        self.functions_mapping()[self.get_type](check_value, expect_value, str(message))

    @property
    def _assert_resp_data(self):
        resp_data = jsonpath(self.get_response_data, self.get_jsonpath)
        assert (
            resp_data is not False
        ), f"jsonpath数据提取失败，提取对象: {self.get_response_data} , 当前语法: {self.get_jsonpath}"
        if len(resp_data) > 1:
            return resp_data
        return resp_data[0]

    @property
    def _assert_request_data(self):
        req_data = jsonpath(self.request_data, self.get_jsonpath)
        assert (
            req_data is not False
        ), f"jsonpath数据提取失败，提取对象: {self.request_data} , 当前语法: {self.get_jsonpath}"
        if len(req_data) > 1:
            return req_data
        return req_data[0]

    def assert_type_handle(self) -> None:
        """
        处理不同类型的断言

        根据断言类型标识执行相应的断言操作：
        - R_SQL: 请求参数与数据库数据断言
        - SQL/D_SQL: 响应数据与数据库数据断言
        - None: 普通响应数据断言

        Raises:
            AssertTypeError: 当断言类型不支持时抛出
        """
        # 判断请求参数数据库断言
        if self.get_assert_type == "R_SQL":
            self._assert(self._assert_request_data, self.get_sql_data, self.get_message)

        # 判断请求参数为响应数据库断言
        elif self.get_assert_type == "SQL" or self.get_assert_type == "D_SQL":
            self._assert(self._assert_resp_data, self.get_sql_data, self.get_message)

        # 判断非数据库断言类型
        elif self.get_assert_type is None:
            self._assert(self._assert_resp_data, self.get_value, self.get_message)
        else:
            raise AssertTypeError("断言失败，目前只支持数据库断言和响应断言")


class Assert(AssertUtil):
    """
    断言执行器

    继承自AssertUtil，负责执行各种类型的断言操作。
    支持批量断言处理和状态码断言。

    特性：
    - 支持多个断言条件的批量处理
    - 自动处理状态码断言
    - 继承所有基础断言功能
    - 提供简化的断言接口
    """

    def assert_data_list(self) -> List[Any]:
        """
        获取断言数据列表

        处理断言配置数据，提取所有需要执行的断言条件。
        特殊处理状态码断言，其他断言条件加入列表返回。

        Returns:
            断言数据列表，包含所有需要执行的断言条件
        """
        assert_list = []
        for k, v in self.assert_data.items():
            if k == "status_code":
                assert self.status_code == v, "响应状态码断言失败"
            else:
                assert_list.append(v)
        return assert_list

    def assert_type_handle(self) -> None:
        """
        批量处理断言

        遍历所有断言条件，逐个执行断言操作。
        每个断言条件都会调用父类的assert_type_handle方法进行处理。
        """
        for i in self.assert_data_list():
            self.assert_data = i
            super().assert_type_handle()
