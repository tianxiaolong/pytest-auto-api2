#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Exceptions Module

This module provides exceptions functionality.
"""

"""
自定义异常模块
定义项目中使用的各种自定义异常类

@Time   : 2022/8/06 15:44
@Author : txl
@Update : 2023-12-20 优化异常类结构和文档
"""
from typing import Any, Optional


class AutoTestException(Exception):
    """自动化测试基础异常类"""

    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Any] = None):
        """
        初始化异常

        Args:
            message: 异常消息
            error_code: 错误代码
            details: 详细信息
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details

    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


# 向后兼容的基础异常类
class MyBaseFailure(AutoTestException):
    """向后兼容的基础异常类"""

    pass


class JsonpathExtractionFailed(AutoTestException):
    """JSONPath提取失败异常"""

    pass


class NotFoundError(AutoTestException):
    """通用未找到异常"""

    pass


class FileNotFound(AutoTestException):
    """文件未找到异常"""

    pass


class SqlNotFound(AutoTestException):
    """SQL未找到异常"""

    pass


class AssertTypeError(AutoTestException):
    """断言类型错误异常"""

    pass


class DataAcquisitionFailed(AutoTestException):
    """数据获取失败异常"""

    pass


class ValueTypeError(AutoTestException):
    """值类型错误异常"""

    pass


class SendMessageError(AutoTestException):
    """消息发送失败异常"""

    pass


class ValueNotFoundError(AutoTestException):
    """值未找到异常"""

    pass


class ConfigurationError(AutoTestException):
    """配置错误异常"""

    pass


class DatabaseConnectionError(AutoTestException):
    """数据库连接错误异常"""

    pass


class RequestError(AutoTestException):
    """请求错误异常"""

    pass


class ResponseError(AutoTestException):
    """响应错误异常"""

    pass


class TestCaseParameterError(AutoTestException):
    """测试用例参数错误异常"""

    pass


class NotFoundTestCase(AutoTestException):
    """测试用例未找到异常"""

    pass
