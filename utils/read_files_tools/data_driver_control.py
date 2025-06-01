#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data Driver Control Module

This module provides data driver control functionality.
"""

"""
数据驱动控制模块
提供统一的数据驱动接口，支持YAML和Excel两种数据源

主要功能：
- 统一的数据获取接口
- 支持YAML和Excel数据源切换
- 自动路径解析和文件查找
- 数据格式标准化
- 配置化的数据源选择

@Time   : 2023-12-20
@Author : txl
"""
import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Union

from common.setting import ensure_path_sep
from utils import config
from utils.logging_tool.log_control import ERROR, INFO
# 注意：CaseData 是旧的数据加载接口，仅用于向后兼容
# 新项目建议使用当前模块的统一接口
from utils.read_files_tools.get_yaml_data_analysis import CaseData
from utils.read_files_tools.yaml_control import GetYamlData


class DataDriverType(Enum):
    """数据驱动类型枚举"""

    YAML = "yaml"
    EXCEL = "excel"


class DataDriverConfig:
    """
    数据驱动配置类

    管理数据驱动的配置信息，包括数据源类型、路径等。
    """

    def __init__(self):
        """初始化数据驱动配置"""
        self._config = config

    @property
    def driver_type(self):
        """动态获取数据驱动类型"""
        return getattr(self._config, "data_driver_type", "yaml")

    @property
    def project_name(self):
        """动态获取项目名称"""
        return getattr(self._config, "project_name", "default_project")

    @property
    def yaml_data_path(self):
        """动态获取YAML数据路径"""
        return getattr(self._config, "yaml_data_path", "data/yaml_data")

    @property
    def excel_data_path(self):
        """动态获取Excel数据路径"""
        return getattr(self._config, "excel_data_path", "data/excel_data")

    @property
    def current_data_path(self) -> str:
        """
        获取当前数据驱动类型对应的路径

        Returns:
            数据路径字符串
        """
        if self.driver_type == DataDriverType.YAML.value:
            return os.path.join(self.yaml_data_path, self.project_name)
        elif self.driver_type == DataDriverType.EXCEL.value:
            return os.path.join(self.excel_data_path, self.project_name)
        else:
            raise ValueError(f"不支持的数据驱动类型: {self.driver_type}")


class DataDriverManager:
    """
    数据驱动管理器

    提供统一的数据获取接口，根据配置自动选择YAML或Excel数据源。
    """

    def __init__(self):
        """初始化数据驱动管理器"""
        self.config = DataDriverConfig()

    def get_test_data(self, module_name: str, file_name: str = None) -> List[Dict[str, Any]]:
        """
        获取测试数据

        根据配置的数据驱动类型，从相应的数据源获取测试数据。

        Args:
            module_name: 模块名称（如：Login、UserInfo等）
            file_name: 文件名称（可选，如果不提供则自动推断）

        Returns:
            测试用例数据列表

        Raises:
            FileNotFoundError: 当数据文件不存在时抛出
            ValueError: 当数据驱动类型不支持时抛出
        """
        if self.config.driver_type == DataDriverType.YAML.value:
            return self._get_yaml_data(module_name, file_name)
        elif self.config.driver_type == DataDriverType.EXCEL.value:
            return self._get_excel_data(module_name, file_name)
        else:
            raise ValueError(f"不支持的数据驱动类型: {self.config.driver_type}")

    def _get_yaml_data(self, module_name: str, file_name: str = None) -> List[Dict[str, Any]]:
        """
        获取YAML测试数据

        Args:
            module_name: 模块名称
            file_name: 文件名称

        Returns:
            测试用例数据列表
        """
        # 构建文件路径
        module_path = Path(self.config.current_data_path) / module_name

        if file_name:
            # 如果指定了文件名，直接使用
            if not file_name.endswith((".yaml", ".yml")):
                file_name += ".yaml"
            file_path = module_path / file_name
        else:
            # 自动查找YAML文件
            yaml_files = list(module_path.glob("*.yaml")) + list(module_path.glob("*.yml"))
            if not yaml_files:
                raise FileNotFoundError(f"在模块 {module_name} 中未找到YAML文件")
            file_path = yaml_files[0]  # 使用第一个找到的文件

        if not file_path.exists():
            raise FileNotFoundError(f"YAML文件不存在: {file_path}")

        INFO.logger.info(f"读取YAML数据文件: {file_path}")

        # 使用现有的YAML数据处理器
        case_data = CaseData(str(file_path))
        return case_data.case_process()

    def _get_excel_data(self, module_name: str, file_name: str = None) -> List[Dict[str, Any]]:
        """
        获取Excel测试数据

        Args:
            module_name: 模块名称
            file_name: 文件名称

        Returns:
            测试用例数据列表
        """
        try:
            from utils.read_files_tools.excel_control import get_excel_test_data
        except ImportError:
            ERROR.logger.error("Excel数据驱动需要安装pandas库: pip install pandas openpyxl")
            raise ImportError("缺少Excel支持库，请安装: pip install pandas openpyxl")

        # 构建文件路径
        module_path = Path(self.config.current_data_path) / module_name

        if file_name:
            # 如果指定了文件名，需要转换为对应的Excel文件名
            excel_file_name = self._convert_yaml_to_excel_filename(file_name, module_name)
            file_path = module_path / excel_file_name
        else:
            # 自动查找Excel文件
            excel_files = list(module_path.glob("*.xlsx")) + list(module_path.glob("*.xls"))
            if not excel_files:
                raise FileNotFoundError(f"在模块 {module_name} 中未找到Excel文件")
            file_path = excel_files[0]  # 使用第一个找到的文件

        if not file_path.exists():
            raise FileNotFoundError(f"Excel文件不存在: {file_path}")

        INFO.logger.info(f"读取Excel数据文件: {file_path}")

        # 使用Excel数据处理器
        return get_excel_test_data(file_path)

    def _convert_yaml_to_excel_filename(self, yaml_file_name: str, module_name: str) -> str:
        """
        将YAML文件名转换为对应的Excel文件名

        Args:
            yaml_file_name: YAML文件名
            module_name: 模块名称

        Returns:
            对应的Excel文件名
        """
        # 文件名映射表
        file_mapping = {
            'Login': {
                'login.yaml': 'login_test_data.xlsx'
            },
            'UserInfo': {
                'get_user_info.yaml': 'userinfo_test_data.xlsx'
            },
            'Collect': {
                'collect_addtool.yaml': 'collect_test_data.xlsx',
                'collect_delete_tool.yaml': 'collect_test_data.xlsx',
                'collect_tool_list.yaml': 'collect_test_data.xlsx',
                'collect_update_tool.yaml': 'collect_test_data.xlsx'
            }
        }

        # 获取模块的映射
        module_mapping = file_mapping.get(module_name, {})

        # 查找对应的Excel文件名
        excel_file_name = module_mapping.get(yaml_file_name)

        if excel_file_name:
            return excel_file_name

        # 如果没有找到映射，尝试通用转换
        base_name = yaml_file_name.replace('.yaml', '').replace('.yml', '')
        return f"{base_name}_test_data.xlsx"

    def list_available_modules(self) -> List[str]:
        """
        列出可用的模块

        Returns:
            模块名称列表
        """
        data_path = Path(self.config.current_data_path)
        if not data_path.exists():
            return []

        modules = []
        for item in data_path.iterdir():
            if item.is_dir():
                modules.append(item.name)

        return sorted(modules)

    def list_module_files(self, module_name: str) -> List[str]:
        """
        列出模块下的数据文件

        Args:
            module_name: 模块名称

        Returns:
            文件名列表
        """
        module_path = Path(self.config.current_data_path) / module_name
        if not module_path.exists():
            return []

        files = []
        if self.config.driver_type == DataDriverType.YAML.value:
            files.extend([f.name for f in module_path.glob("*.yaml")])
            files.extend([f.name for f in module_path.glob("*.yml")])
        elif self.config.driver_type == DataDriverType.EXCEL.value:
            files.extend([f.name for f in module_path.glob("*.xlsx")])
            files.extend([f.name for f in module_path.glob("*.xls")])

        return sorted(files)


# 全局数据驱动管理器实例
data_driver = DataDriverManager()


def get_test_data(module_name: str, file_name: str = None) -> List[Dict[str, Any]]:
    """
    获取测试数据的便捷函数

    Args:
        module_name: 模块名称
        file_name: 文件名称（可选）

    Returns:
        测试用例数据列表
    """
    return data_driver.get_test_data(module_name, file_name)


def switch_data_driver(driver_type: str) -> None:
    """
    切换数据驱动类型

    Args:
        driver_type: 数据驱动类型（yaml 或 excel）
    """
    if driver_type not in [DataDriverType.YAML.value, DataDriverType.EXCEL.value]:
        raise ValueError(f"不支持的数据驱动类型: {driver_type}")

    # 更新配置 - 直接修改配置对象的属性
    import utils
    utils.config.data_driver_type = driver_type

    # 同时更新模块级别的配置变量
    utils.data_driver_type = driver_type

    # 重新初始化全局管理器
    global data_driver
    data_driver = DataDriverManager()

    INFO.logger.info(f"数据驱动类型已切换为: {driver_type}")


if __name__ == "__main__":
    # 测试代码
    try:
        # 列出可用模块
        modules = data_driver.list_available_modules()
        print(f"可用模块: {modules}")

        # 如果有模块，测试获取数据
        if modules:
            test_module = modules[0]
            files = data_driver.list_module_files(test_module)
            print(f"模块 {test_module} 的文件: {files}")

            # 尝试获取测试数据
            test_data = get_test_data(test_module)
            print(f"成功获取 {len(test_data)} 个测试用例")

    except Exception as e:
        print(f"测试失败: {e}")
