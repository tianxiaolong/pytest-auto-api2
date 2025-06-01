#!/usr/bin/env python
# -*- coding: utf-8 -*-
import types
from dataclasses import dataclass
from enum import Enum, unique
from typing import Any, Callable, Dict, List, Optional, Text, Union

from pydantic import BaseModel, Field

"""
models module
Provides functionality for models
"""


class NotificationType(Enum):
    """自动化通知方式"""

    DEFAULT = "0"
    DING_TALK = "1"
    WECHAT = "2"
    EMAIL = "3"
    FEI_SHU = "4"


@dataclass
class TestMetrics:
    """用例执行数据"""

    passed: int
    failed: int
    broken: int
    skipped: int
    total: int
    pass_rate: float
    time: Text
    calculation_method: Text = "passed only"  # 成功率计算方式
    success_count: int = 0  # 成功用例数（用于调试）


class RequestType(Enum):
    """
    request请求发送，请求参数的数据类型
    """

    JSON = "JSON"
    PARAMS = "PARAMS"
    DATA = "DATA"
    FILE = "FILE"
    EXPORT = "EXPORT"
    NONE = "NONE"


class TestCaseEnum(Enum):
    """
    测试用例字段枚举

    定义测试用例YAML配置文件中所有可用的字段名称和是否必填。
    每个枚举值包含两个元素：(字段名, 是否必填)

    字段说明：
    - URL: 接口地址 (必填)
    - HOST: 主机地址 (必填)
    - METHOD: 请求方法 (必填)
    - DETAIL: 用例描述 (必填)
    - HEADERS: 请求头 (必填)
    - REQUEST_TYPE: 请求类型 (必填)
    - DATA: 请求数据 (必填)
    - DE_CASE: 依赖用例标识 (必填)
    - ASSERT_DATA: 断言配置 (必填)
    - 其他字段为可选字段
    """

    URL = ("url", True)
    HOST = ("host", True)
    METHOD = ("method", True)
    DETAIL = ("detail", True)
    IS_RUN = ("is_run", True)
    HEADERS = ("headers", True)
    REQUEST_TYPE = ("requestType", True)
    DATA = ("data", True)
    DE_CASE = ("dependence_case", True)
    DE_CASE_DATA = ("dependence_case_data", False)
    CURRENT_RE_SET_CACHE = ("current_request_set_cache", False)
    SQL = ("sql", False)
    ASSERT_DATA = ("assert", True)
    SETUP_SQL = ("setup_sql", False)
    TEARDOWN = ("teardown", False)
    TEARDOWN_SQL = ("teardown_sql", False)
    SLEEP = ("sleep", False)


class Method(Enum):
    """
    HTTP请求方法枚举

    定义支持的HTTP请求方法类型。
    用于测试用例中指定接口的请求方式。

    支持的方法：
    - GET: 获取资源
    - POST: 创建资源
    - PUT: 更新资源（完整更新）
    - PATCH: 更新资源（部分更新）
    - DELETE: 删除资源
    - HEAD: 获取资源头信息
    - OPTION: 获取资源支持的方法
    """

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTION = "OPTION"


def load_module_functions(module) -> Dict[Text, Callable]:
    """获取 module中方法的名称和所在的内存地址"""
    module_functions = {}

    for name, item in vars(module).items():
        if isinstance(item, types.FunctionType):
            module_functions[name] = item
    return module_functions


@unique
class DependentType(Enum):
    """
    数据依赖相关枚举
    """

    RESPONSE = "response"
    REQUEST = "request"
    SQL_DATA = "sqlData"
    CACHE = "cache"


class Assert(BaseModel):
    """
    断言配置数据模型

    定义单个断言条件的配置结构。
    用于验证接口响应或数据库查询结果。

    字段说明：
    - jsonpath: JSONPath表达式，用于提取数据
    - type: 断言类型（如：==、!=、contains等）
    - value: 期望值
    - AssertType: 断言类型标识（可选）
    """

    jsonpath: Text
    type: Text
    value: Any
    AssertType: Union[None, Text] = None


class DependentData(BaseModel):
    """
    依赖数据配置模型

    定义测试用例间数据依赖的配置结构。
    用于从前置用例中提取数据并传递给当前用例。

    字段说明：
    - dependent_type: 依赖类型（response/request/sqlData/cache）
    - jsonpath: 数据提取路径
    - set_cache: 缓存名称（可选）
    - replace_key: 替换的键名（可选）
    """

    dependent_type: Text
    jsonpath: Text
    set_cache: Optional[Text]
    replace_key: Optional[Text]


class DependentCaseData(BaseModel):
    """
    依赖用例数据模型

    定义依赖用例的配置结构，包含用例ID和依赖数据列表。

    字段说明：
    - case_id: 依赖的用例ID
    - dependent_data: 依赖数据配置列表
    """

    case_id: Text
    dependent_data: Union[None, List[DependentData]] = None


class ParamPrepare(BaseModel):
    """
    参数准备配置模型

    定义测试前置参数准备的配置结构。
    用于在测试执行前准备必要的参数数据。

    字段说明：
    - dependent_type: 依赖类型
    - jsonpath: 数据提取路径
    - set_cache: 缓存名称
    """

    dependent_type: Text
    jsonpath: Text
    set_cache: Text


class SendRequest(BaseModel):
    """
    发送请求配置模型

    定义测试后置处理中发送请求的配置结构。
    用于在测试完成后执行清理或验证操作。

    字段说明：
    - dependent_type: 依赖类型
    - jsonpath: 数据提取路径（可选）
    - cache_data: 缓存数据名称（可选）
    - set_cache: 设置缓存名称（可选）
    - replace_key: 替换的键名（可选）
    """

    dependent_type: Text
    jsonpath: Optional[Text]
    cache_data: Optional[Text]
    set_cache: Optional[Text]
    replace_key: Optional[Text]


class TearDown(BaseModel):
    """
    测试后置处理配置模型

    定义测试用例执行完成后的清理操作配置。
    用于数据清理、状态重置等后置处理。

    字段说明：
    - case_id: 关联的用例ID
    - param_prepare: 参数准备配置列表（可选）
    - send_request: 发送请求配置列表（可选）
    """

    case_id: Text
    param_prepare: Optional[List["ParamPrepare"]]
    send_request: Optional[List["SendRequest"]]


class CurrentRequestSetCache(BaseModel):
    """
    当前请求缓存设置模型

    定义当前请求响应数据的缓存配置。
    用于将请求响应中的特定数据缓存起来供后续用例使用。

    字段说明：
    - type: 缓存类型
    - jsonpath: 数据提取路径
    - name: 缓存名称
    """

    type: Text
    jsonpath: Text
    name: Text


class TestCase(BaseModel):
    """
    测试用例数据模型

    定义单个测试用例的完整配置结构。
    这是框架的核心数据模型，包含了执行一个接口测试所需的所有信息。

    必填字段：
    - url: 接口地址
    - method: 请求方法（GET/POST/PUT/DELETE等）
    - detail: 用例描述
    - assert_data: 断言配置
    - requestType: 请求类型（json/data/params/file等）

    可选字段：
    - headers: 请求头
    - data: 请求数据
    - dependence_case: 是否有依赖用例
    - sql: SQL查询配置
    - teardown: 后置处理配置
    - 等等...
    """

    url: Text
    method: Text
    detail: Text
    assert_data: Union[Dict, Text]
    headers: Union[None, Dict, Text] = {}
    requestType: Text
    is_run: Union[None, bool, Text] = None
    data: Any = None
    dependence_case: Union[None, bool] = False
    dependence_case_data: Optional[Union[None, List["DependentCaseData"], Text]] = None
    sql: List = None
    setup_sql: List = None
    status_code: Optional[int] = None
    teardown_sql: Optional[List] = None
    teardown: Union[List["TearDown"], None] = None
    current_request_set_cache: Optional[List["CurrentRequestSetCache"]]
    sleep: Optional[Union[int, float]]


class ResponseData(BaseModel):
    """
    响应数据模型

    封装接口测试执行后的完整响应信息。
    包含请求信息、响应信息、断言数据、SQL数据等所有相关信息。

    主要字段：
    - url: 实际请求的URL
    - response_data: 接口响应数据
    - request_body: 请求体数据
    - method: 请求方法
    - sql_data: SQL查询结果
    - assert_data: 断言配置
    - res_time: 响应时间
    - status_code: HTTP状态码
    - 其他辅助字段...
    """

    url: Text
    is_run: Union[None, bool, Text]
    detail: Text
    response_data: Text
    request_body: Any
    method: Text
    sql_data: Dict
    yaml_data: "TestCase"
    headers: Dict
    cookie: Dict
    assert_data: Dict
    res_time: Union[int, float]
    status_code: int
    teardown: List["TearDown"] = None
    teardown_sql: Union[None, List]
    body: Any


class DingTalk(BaseModel):
    """
    钉钉通知配置模型

    定义钉钉机器人通知的配置信息。
    用于测试完成后发送钉钉通知。

    字段说明：
    - webhook: 钉钉机器人webhook地址
    - secret: 钉钉机器人密钥（用于签名验证）
    """

    webhook: Union[Text, None]
    secret: Union[Text, None]


class MySqlDB(BaseModel):
    """
    MySQL数据库配置模型

    定义数据库连接的配置信息。
    用于数据库断言和数据准备。

    字段说明：
    - switch: 数据库功能开关
    - host: 数据库主机地址
    - user: 数据库用户名
    - password: 数据库密码
    - port: 数据库端口（默认3306）
    """

    switch: bool = False
    host: Union[Text, None] = None
    user: Union[Text, None] = None
    password: Union[Text, None] = None
    port: Union[int, None] = 3306


class Webhook(BaseModel):
    """
    通用Webhook配置模型

    定义通用的webhook通知配置。
    适用于企业微信、飞书等支持webhook的通知平台。

    字段说明：
    - webhook: webhook地址URL
    """

    webhook: Union[Text, None]


class Email(BaseModel):
    """
    邮件通知配置模型

    定义邮件发送的配置信息。
    用于测试完成后发送邮件通知。

    字段说明：
    - send_user: 发送者邮箱地址
    - email_host: 邮件服务器地址
    - stamp_key: 邮箱授权码或密码
    - send_list: 收件人邮箱列表（逗号分隔）
    """

    send_user: Union[Text, None]
    email_host: Union[Text, None]
    stamp_key: Union[Text, None]
    # 收件人邮箱列表
    send_list: Union[Text, None]


class Config(BaseModel):
    """
    主配置模型

    定义整个测试框架的配置结构。
    这是框架的核心配置模型，包含了所有功能模块的配置信息。

    核心配置：
    - project_name: 项目名称
    - env: 测试环境标识
    - tester_name: 测试人员姓名
    - host: 主要测试地址

    功能配置：
    - notification_type: 通知类型（0=无通知，1=钉钉，2=微信等）
    - excel_report: 是否生成Excel报告
    - real_time_update_test_cases: 是否实时更新测试用例

    数据驱动配置：
    - data_driver_type: 数据驱动类型（yaml/excel）
    - yaml_data_path: YAML数据文件路径
    - excel_data_path: Excel数据文件路径

    集成配置：
    - ding_talk: 钉钉通知配置
    - mysql_db: 数据库配置
    - email: 邮件通知配置
    - wechat: 企业微信配置
    - lark: 飞书配置
    """

    project_name: Text
    env: Text
    tester_name: Text
    notification_type: Text = "0"
    excel_report: bool
    ding_talk: "DingTalk"
    mysql_db: "MySqlDB"
    mirror_source: Text
    wechat: "Webhook"
    email: "Email"
    lark: "Webhook"
    real_time_update_test_cases: bool = False
    host: Text
    app_host: Union[Text, None]

    # 新增数据驱动配置字段
    data_driver_type: Text = "yaml"
    yaml_data_path: Text = "data/yaml_data"
    excel_data_path: Text = "data/excel_data"


@unique
class AllureAttachmentType(Enum):
    """
    allure 报告的文件类型枚举
    """

    TEXT = "txt"
    CSV = "csv"
    TSV = "tsv"
    URI_LIST = "uri"

    HTML = "html"
    XML = "xml"
    JSON = "json"
    YAML = "yaml"
    PCAP = "pcap"

    PNG = "png"
    JPG = "jpg"
    SVG = "svg"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"

    MP4 = "mp4"
    OGG = "ogg"
    WEBM = "webm"

    PDF = "pdf"


@unique
class AssertMethod(Enum):
    """断言类型"""

    equals = "=="
    less_than = "lt"
    less_than_or_equals = "le"
    greater_than = "gt"
    greater_than_or_equals = "ge"
    not_equals = "not_eq"
    string_equals = "str_eq"
    length_equals = "len_eq"
    length_greater_than = "len_gt"
    length_greater_than_or_equals = "len_ge"
    length_less_than = "len_lt"
    length_less_than_or_equals = "len_le"
    contains = "contains"
    contained_by = "contained_by"
    startswith = "startswith"
    endswith = "endswith"
