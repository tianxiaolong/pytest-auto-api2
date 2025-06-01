#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Config Loader Module

This module provides config loader functionality.
"""

"""
配置加载器，支持环境变量替换
@Time   : 2023-12-20
@Author : 测试工程师
"""
import os
import re
from pathlib import Path
from typing import Any, Dict, Union

import yaml


class ConfigLoader:
    """配置加载器，支持环境变量替换"""

    def __init__(self, config_path: str = None):
        """
        初始化配置加载器

        Args:
            config_path: 配置文件路径，默认为 common/config.yaml
        """
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        self.config_path = Path(config_path)
        self._config_data = None

    def _load_env_file(self, env_file: str = ".env") -> None:
        """
        加载 .env 文件中的环境变量

        Args:
            env_file: .env 文件路径
        """
        env_path = Path(env_file)
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ.setdefault(key.strip(), value.strip())

    def _replace_env_vars(self, value: Any) -> Any:
        """
        递归替换配置中的环境变量

        Args:
            value: 配置值

        Returns:
            替换后的配置值
        """
        if isinstance(value, str):
            # 匹配 ${VAR_NAME:default_value} 格式
            pattern = r"\$\{([^:}]+):([^}]*)\}"

            def replace_match(match) -> str:
                """
                替换匹配的环境变量

                Args:
                    match: 正则匹配对象

                Returns:
                    环境变量值或默认值
                """
                var_name = match.group(1)
                default_value = match.group(2)
                return os.environ.get(var_name, default_value)

            return re.sub(pattern, replace_match, value)

        elif isinstance(value, dict):
            return {k: self._replace_env_vars(v) for k, v in value.items()}

        elif isinstance(value, list):
            return [self._replace_env_vars(item) for item in value]

        else:
            return value

    def _convert_types(self, value: Any) -> Any:
        """
        转换配置值的类型

        Args:
            value: 配置值

        Returns:
            转换后的配置值
        """
        if isinstance(value, str):
            # 转换布尔值
            if value.lower() in ("true", "false"):
                return value.lower() == "true"

            # 转换数字
            if value.isdigit():
                return int(value)

            # 尝试转换浮点数
            try:
                if "." in value:
                    return float(value)
            except ValueError:
                pass

        elif isinstance(value, dict):
            return {k: self._convert_types(v) for k, v in value.items()}

        elif isinstance(value, list):
            return [self._convert_types(item) for item in value]

        return value

    def load_config(self, reload: bool = False) -> Dict[str, Any]:
        """
        加载配置文件

        Args:
            reload: 是否重新加载配置

        Returns:
            配置字典
        """
        if self._config_data is None or reload:
            # 加载 .env 文件
            self._load_env_file()

            # 读取配置文件
            with open(self.config_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)

            # 替换环境变量
            config_data = self._replace_env_vars(config_data)

            # 转换类型
            config_data = self._convert_types(config_data)

            self._config_data = config_data

        return self._config_data

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            key: 配置键，支持点号分隔的嵌套键，如 'mysql_db.host'
            default: 默认值

        Returns:
            配置值
        """
        config = self.load_config()

        # 支持嵌套键访问
        keys = key.split(".")
        value = config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default


# 全局配置实例
config_loader = ConfigLoader()


# 为了向后兼容，保持原有的访问方式
def get_config() -> Dict[str, Any]:
    """获取完整配置"""
    return config_loader.load_config()


# 常用配置的快捷访问
project_name = config_loader.get("project_name", "pytest-auto-api2")
env = config_loader.get("env", "测试环境")
tester_name = config_loader.get("tester_name", "测试工程师")
host = config_loader.get("host", "https://www.wanandroid.com")
app_host = config_loader.get("app_host", "")
notification_type = config_loader.get("notification_type", "0")
excel_report = config_loader.get("excel_report", False)
real_time_update_test_cases = config_loader.get("real_time_update_test_cases", False)
