#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Conftest Module

This module provides conftest functionality.
"""

"""
conftest module
Provides functionality for conftest
"""
import ast
import time

import allure
import pytest
import requests

from common.setting import ensure_path_sep
from utils.cache_process.cache_control import CacheHandler
from utils.logging_tool.log_control import ERROR, INFO, WARNING
from utils.other_tools.allure_data.allure_tools import allure_step, allure_step_no
from utils.other_tools.models import TestCase
from utils.read_files_tools.clean_files import del_file
from utils.requests_tool.request_control import cache_regular

try:
    from utils.logging_tool.encoding_fix import setup_utf8_encoding

    setup_utf8_encoding()
except ImportError:
    pass


@pytest.fixture(scope="session", autouse=False)
def clear_report():
    """如clean命名无法删除报告，这里手动删除"""
    del_file(ensure_path_sep("\\report"))


@pytest.fixture(scope="session", autouse=True)
def work_login_init():
    """
    获取登录的cookie
    :return:
    """

    url = "https://www.wanandroid.com/user/login"
    data = {"username": 18800000001, "password": 123456}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    # 请求登录接口

    res = requests.post(url=url, data=data, verify=True, headers=headers)
    response_cookie = res.cookies

    cookies = ""
    for k, v in response_cookie.items():
        _cookie = k + "=" + v + ";"
        # 拿到登录的cookie内容，cookie拿到的是字典类型，转换成对应的格式
        cookies += _cookie
        # 将登录接口中的cookie写入缓存中，其中login_cookie是缓存名称
    CacheHandler.update_cache(cache_name="login_cookie", value=cookies)


def pytest_collection_modifyitems(items):
    """
    测试用例收集完成时，将收集到的 item 的 name 和 node_id 的中文显示在控制台上
    :return:
    """
    for item in items:
        try:
            # 修复中文编码显示问题
            item.name = item.name.encode("utf-8").decode("unicode_escape")
            item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")
        except (UnicodeDecodeError, UnicodeEncodeError):
            # 如果编码转换失败，保持原样
            pass

    # 期望用例顺序
    # print("收集到的测试用例:%s" % items)
    appoint_items = [
        "test_get_user_info",
        "test_collect_addtool",
        "test_Cart_List",
        "test_ADD",
        "test_Guest_ADD",
        "test_Clear_Cart_Item",
    ]

    # 指定运行顺序
    run_items = []
    for i in appoint_items:
        for item in items:
            module_item = item.name.split("[")[0]
            if i == module_item:
                run_items.append(item)

    for i in run_items:
        run_index = run_items.index(i)
        items_index = items.index(i)

        if run_index != items_index:
            n_data = items[run_index]
            run_index = items.index(n_data)
            items[items_index], items[run_index] = items[run_index], items[items_index]


def pytest_configure(config):
    """
    pytest配置钩子函数

    在pytest启动时执行，用于添加自定义标记。

    Args:
        config: pytest配置对象
    """
    config.addinivalue_line("markers", "smoke")
    config.addinivalue_line("markers", "回归测试")


@pytest.fixture(scope="function", autouse=True)
def case_skip(in_data):
    """处理跳过用例"""
    in_data = TestCase(**in_data)
    if ast.literal_eval(cache_regular(str(in_data.is_run))) is False:
        allure.dynamic.title(in_data.detail)
        allure_step_no(f"请求URL: {in_data.is_run}")
        allure_step_no(f"请求方式: {in_data.method}")
        allure_step("请求头: ", in_data.headers)
        allure_step("请求数据: ", in_data.data)
        allure_step("依赖数据: ", in_data.dependence_case_data)
        allure_step("预期数据: ", in_data.assert_data)
        pytest.skip()


def pytest_terminal_summary(terminalreporter):
    """
    收集测试结果
    """

    _PASSED = len([i for i in terminalreporter.stats.get("passed", []) if i.when != "teardown"])
    _ERROR = len([i for i in terminalreporter.stats.get("error", []) if i.when != "teardown"])
    _FAILED = len([i for i in terminalreporter.stats.get("failed", []) if i.when != "teardown"])
    _SKIPPED = len([i for i in terminalreporter.stats.get("skipped", []) if i.when != "teardown"])
    _TOTAL = terminalreporter._numcollected
    _TIMES = time.time() - terminalreporter._sessionstarttime

    # 使用英文日志避免编码问题，或者确保UTF-8编码
    try:
        INFO.logger.info(f"Total cases: {_TOTAL}")
        INFO.logger.info(f"Passed cases: {_PASSED}")
        INFO.logger.error(f"Error cases: {_ERROR}")
        ERROR.logger.error(f"Failed cases: {_FAILED}")
        WARNING.logger.warning(f"Skipped cases: {_SKIPPED}")
        INFO.logger.info("Execution time: %.2f s" % _TIMES)

        try:
            _RATE = _PASSED / _TOTAL * 100
            INFO.logger.info("Success rate: %.2f %%" % _RATE)
        except ZeroDivisionError:
            INFO.logger.info("Success rate: 0.00 %")
    except UnicodeEncodeError:
        # 如果仍有编码问题，使用基本信息
        INFO.logger.info(f"Cases: {_PASSED}/{_TOTAL} passed, {_FAILED} failed, {_ERROR} error, {_SKIPPED} skipped")
