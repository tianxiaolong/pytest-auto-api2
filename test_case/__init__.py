#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  Init   Module

This module provides   init   functionality.
"""

"""
__init__ module
Provides functionality for   init
"""
from common.setting import ensure_path_sep
from utils import config
from utils.cache_process.cache_control import CacheHandler, _cache_config
from utils.read_files_tools.get_all_files_path import get_all_files
# 注意：CaseData 是旧的数据加载接口，仅用于向后兼容
# 新项目建议使用 utils.read_files_tools.data_driver_control 模块
from utils.read_files_tools.get_yaml_data_analysis import CaseData


def write_case_process():
    """
    获取所有用例，写入用例池中

    注意：此函数使用旧的数据加载方式，主要用于向后兼容。
    新的数据驱动方式请使用 data_driver_control 模块。
    """

    # 根据配置确定数据路径
    if hasattr(config, "data_driver_type") and config.data_driver_type == "excel":
        # 如果使用Excel数据驱动，跳过此初始化
        return

    # 使用新的YAML数据路径
    yaml_data_path = getattr(config, "yaml_data_path", "data/yaml_data")
    project_name = getattr(config, "project_name", "pytest-auto-api2")
    data_path = ensure_path_sep(f"\\{yaml_data_path}\\{project_name}")

    # 循环拿到所有存放用例的文件路径
    for i in get_all_files(file_path=data_path, yaml_data_switch=True):
        # 循环读取文件中的数据
        case_process = CaseData(i).case_process(case_id_switch=True)
        if case_process is not None:
            # 转换数据类型
            for case in case_process:
                for k, v in case.items():
                    # 判断 case_id 是否已存在
                    case_id_exit = k in _cache_config.keys()
                    # 如果case_id 不存在，则将用例写入缓存池中
                    if case_id_exit is False:
                        CacheHandler.update_cache(cache_name=k, value=v)
                        # case_data[k] = v
                    # 当 case_id 为 True 存在时，则跑出异常
                    elif case_id_exit is True:
                        raise ValueError(f"case_id: {k} 存在重复项, 请修改case_id\n" f"文件路径: {i}")


# 只有在YAML数据驱动模式下才执行初始化
try:
    write_case_process()
except Exception as e:
    # 如果初始化失败，记录警告但不阻止程序运行
    import warnings

    warnings.warn(f"用例池初始化失败: {e}，建议使用新的数据驱动接口", UserWarning)
