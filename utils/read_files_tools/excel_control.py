#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Excel Control Module

This module provides excel control functionality.
"""

"""
Excel数据控制模块
提供Excel格式测试数据的读取和处理功能

主要功能：
- 读取Excel测试数据文件
- 解析Excel中的测试用例
- 转换为标准的测试用例格式
- 支持多Sheet结构
- 数据类型自动转换

@Time   : 2023-12-20
@Author : txl
@Update : 重构为现代化Excel数据驱动支持
"""
import ast
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from common.setting import ensure_path_sep
from utils.logging_tool.log_control import ERROR, INFO
from utils.other_tools.models import TestCase


class ExcelDataReader:
    """
    Excel数据读取器

    负责读取和解析Excel格式的测试数据文件。
    支持标准的Excel测试用例格式，包括公共配置和测试用例数据。

    Excel文件结构：
    - case_common sheet: 公共配置信息
    - test_cases sheet: 测试用例数据
    """

    def __init__(self, file_path: Union[str, Path]):
        """
        初始化Excel数据读取器

        Args:
            file_path: Excel文件路径
        """
        self.file_path = Path(file_path)
        self.data = {}

    def read_excel_data(self) -> Dict[str, Any]:
        """
        读取Excel数据

        Returns:
            包含测试用例数据的字典

        Raises:
            FileNotFoundError: 当Excel文件不存在时抛出
            ValueError: 当Excel文件格式不正确时抛出
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"Excel文件不存在: {self.file_path}")

        try:
            # 读取所有sheet，指定编码处理
            excel_data = pd.read_excel(
                self.file_path,
                sheet_name=None,
                dtype=str,
                engine='openpyxl'  # 使用openpyxl引擎，更好的编码支持
            )

            # 处理公共配置
            if "case_common" in excel_data:
                self.data["case_common"] = self._parse_common_config(excel_data["case_common"])
            else:
                INFO.logger.warning(f"Excel文件中未找到case_common sheet: {self.file_path}")
                self.data["case_common"] = {}

            # 处理测试用例数据
            if "test_cases" in excel_data:
                test_cases = self._parse_test_cases(excel_data["test_cases"])
                self.data.update(test_cases)
            else:
                raise ValueError(f"Excel文件中未找到test_cases sheet: {self.file_path}")

            return self.data

        except Exception as e:
            ERROR.logger.error(f"读取Excel文件失败: {self.file_path}, 错误: {e}")
            raise

    def _parse_common_config(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        解析公共配置数据

        Args:
            df: 公共配置DataFrame

        Returns:
            公共配置字典
        """
        common_config = {}

        # 假设公共配置是键值对格式
        for _, row in df.iterrows():
            if pd.notna(row.iloc[0]) and pd.notna(row.iloc[1]):
                key = str(row.iloc[0]).strip()
                value = str(row.iloc[1]).strip()

                # 尝试解析为Python对象
                try:
                    common_config[key] = ast.literal_eval(value)
                except (ValueError, SyntaxError):
                    common_config[key] = value

        return common_config

    def _parse_test_cases(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        解析测试用例数据

        Args:
            df: 测试用例DataFrame

        Returns:
            测试用例数据字典
        """
        test_cases = {}

        # 清理列名
        df.columns = df.columns.str.strip()

        for _, row in df.iterrows():
            # 跳过空行
            if pd.isna(row.get("case_id")):
                continue

            case_id = str(row["case_id"]).strip()
            case_data = {}

            # 处理每个字段
            for column in df.columns:
                if column == "case_id":
                    continue

                value = row[column]
                if pd.notna(value):
                    case_data[column] = self._parse_cell_value(str(value).strip())
                else:
                    case_data[column] = None

            test_cases[case_id] = case_data

        return test_cases

    def _parse_cell_value(self, value: str) -> Any:
        """
        解析单元格值

        尝试将字符串值转换为适当的Python类型。

        Args:
            value: 单元格字符串值

        Returns:
            转换后的值
        """
        if not value or value.lower() in ["none", "null", ""]:
            return None

        # 尝试解析为布尔值
        if value.lower() in ["true", "false"]:
            return value.lower() == "true"

        # 尝试解析为数字
        try:
            if "." in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass

        # 尝试解析为JSON对象
        if value.startswith(("{", "[")):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass

        # 尝试解析为Python字面量
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            pass

        # 返回原始字符串
        return value


class ExcelDataProcessor:
    """
    Excel数据处理器

    将Excel数据转换为标准的测试用例格式，与YAML数据处理器保持一致的接口。
    """

    def __init__(self, file_path: Union[str, Path]):
        """
        初始化Excel数据处理器

        Args:
            file_path: Excel文件路径
        """
        self.file_path = file_path
        self.reader = ExcelDataReader(file_path)

    def get_excel_data(self) -> Dict[str, Any]:
        """
        获取Excel数据

        Returns:
            标准格式的测试数据字典
        """
        return self.reader.read_excel_data()

    def convert_to_test_cases(self) -> List[Dict[str, Any]]:
        """
        转换为TestCase对象列表

        Returns:
            TestCase对象字典列表
        """
        data = self.get_excel_data()
        test_cases = []

        for case_id, case_data in data.items():
            if case_id == "case_common":
                continue

            try:
                # 确保必要字段存在
                case_data = self._ensure_required_fields(case_data)

                # 直接返回字典格式，与YAML数据格式保持一致
                test_cases.append({case_id: case_data})

            except Exception as e:
                ERROR.logger.error(f"转换测试用例失败 {case_id}: {e}")
                continue

        return test_cases

    def _ensure_required_fields(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        确保必要字段存在

        Args:
            case_data: 原始用例数据

        Returns:
            补充必要字段后的用例数据
        """
        # 必要字段的默认值
        required_fields = {
            "url": "",
            "method": "GET",
            "detail": "",
            "assert_data": {"status_code": 200},
            "headers": {},
            "requestType": "json",
            "is_run": True,
            "data": None,
            "dependence_case": False,
            "dependence_case_data": None,
            "sql": None,
            "setup_sql": None,
            "status_code": None,
            "teardown_sql": None,
            "teardown": None,
            "current_request_set_cache": None,
            "sleep": None,
            "host": None,
        }

        # 补充缺失字段
        for field, default_value in required_fields.items():
            if field not in case_data or case_data[field] is None:
                case_data[field] = default_value

        # 特殊处理assert字段
        if "assert" in case_data:
            case_data["assert_data"] = case_data.pop("assert")

        return case_data


# 兼容旧版本的函数
def get_excel_data(sheet_name: str, case_name: str) -> List[tuple]:
    """
    兼容旧版本的Excel数据读取函数

    Args:
        sheet_name: sheet页名称
        case_name: 测试用例名称

    Returns:
        测试数据列表
    """
    INFO.logger.warning("使用了旧版本的get_excel_data函数，建议使用新的ExcelDataProcessor")
    # 这里可以保留旧的实现或者适配到新的实现
    return []


def get_excel_test_data(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    获取Excel测试数据的便捷函数

    Args:
        file_path: Excel文件路径

    Returns:
        测试用例数据列表
    """
    from utils.read_files_tools.regular_control import regular

    processor = ExcelDataProcessor(file_path)
    test_cases = processor.convert_to_test_cases()

    # 对Excel数据应用动态函数处理，就像YAML一样
    processed_cases = []
    for case in test_cases:
        # 对每个测试用例应用regular处理
        processed_case_str = regular(str(case))
        processed_case = ast.literal_eval(processed_case_str)
        processed_cases.append(processed_case)

    return processed_cases


if __name__ == "__main__":
    # 测试代码
    test_file = "data/excel_data/test_project/Login/login_test_data.xlsx"
    try:
        data = get_excel_test_data(test_file)
        print(f"成功读取 {len(data)} 个测试用例")
        for case in data:
            print(f"用例: {list(case.keys())[0]}")
    except Exception as e:
        print(f"测试失败: {e}")
