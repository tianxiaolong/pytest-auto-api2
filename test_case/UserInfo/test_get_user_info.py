#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2025-05-29 14:18:03


import allure
import pytest
from utils.read_files_tools.data_driver_control import get_test_data
from utils.assertion.assert_control import Assert
from utils.requests_tool.request_control import RequestControl
from utils.read_files_tools.regular_control import regular
from utils.requests_tool.teardown_control import TearDownHandler


# 使用新的数据驱动接口获取测试数据
# 注意：需要根据实际情况指定具体的文件名
TestData = get_test_data('UserInfo', 'get_user_info.yaml')
re_data = regular(str(TestData))


@allure.epic("pytest-auto-api2")
@allure.feature("UserInfo")
class TestGetUserInfo:

    @allure.story("UserInfo模块测试")
    @pytest.mark.parametrize('in_data', eval(re_data), ids=[i['detail'] for i in TestData])
    def test_get_user_info(self, in_data, case_skip):
        """
        :param :
        :return:
        """
        res = RequestControl(in_data).http_request()
        TearDownHandler(res).teardown_handle()
        Assert(assert_data=in_data['assert_data'],
               sql_data=res.sql_data,
               request_data=res.body,
               response_data=res.response_data,
               status_code=res.status_code).assert_type_handle()


if __name__ == '__main__':
    pytest.main(['get_user_info.yaml', '-s', '-W', 'ignore:Module already imported:pytest.PytestWarning'])
