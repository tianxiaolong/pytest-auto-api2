#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  Init   Module

This module provides   init   functionality.
"""

"""
工具包初始化模块
"""
from common.config_loader import get_config
from utils.other_tools.models import Config

_data = get_config()
config = Config(**_data)

# 向后兼容的配置访问方式
project_name = config.project_name
env = config.env
tester_name = config.tester_name
host = config.host
app_host = config.app_host
notification_type = config.notification_type
excel_report = config.excel_report
real_time_update_test_cases = config.real_time_update_test_cases

# 新增数据驱动配置的向后兼容访问
data_driver_type = config.data_driver_type
yaml_data_path = config.yaml_data_path
excel_data_path = config.excel_data_path
