#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Common Utils Module

This module provides common utils functionality.
"""

"""
通用工具模块
提供项目中常用的工具函数

@Time   : 2023-12-20
@Author : txl
"""
from datetime import datetime
from pathlib import Path
import json
import re
import time

from typing import Any, Dict, List, Optional, Union


class FileUtils:
    """文件操作工具类"""

    @staticmethod
    def ensure_dir(path: Union[str, Path]) -> Path:
        """
        确保目录存在，如果不存在则创建

        Args:
            path: 目录路径

        Returns:
            Path对象
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def read_file(file_path: Union[str, Path], encoding: str = "utf-8") -> str:
        """
        读取文件内容

        Args:
            file_path: 文件路径
            encoding: 编码格式

        Returns:
            文件内容
        """
        with open(file_path, "r", encoding=encoding) as f:
            return f.read()

    @staticmethod
    def write_file(file_path: Union[str, Path], content: str, encoding: str = "utf-8") -> None:
        """
        写入文件内容

        Args:
            file_path: 文件路径
            content: 文件内容
            encoding: 编码格式
        """
        file_path = Path(file_path)
        FileUtils.ensure_dir(file_path.parent)

        with open(file_path, "w", encoding=encoding) as f:
            f.write(content)

    @staticmethod
    def get_files_by_pattern(directory: Union[str, Path], pattern: str = "*") -> List[Path]:
        """
        根据模式获取文件列表

        Args:
            directory: 目录路径
            pattern: 文件模式

        Returns:
            文件路径列表
        """
        directory = Path(directory)
        return list(directory.glob(pattern))


class StringUtils:
    """字符串处理工具类"""

    @staticmethod
    def snake_to_camel(snake_str: str) -> str:
        """
        将下划线命名转换为驼峰命名

        Args:
            snake_str: 下划线命名字符串

        Returns:
            驼峰命名字符串
        """
        components = snake_str.split("_")
        return components[0] + "".join(word.capitalize() for word in components[1:])

    @staticmethod
    def camel_to_snake(camel_str: str) -> str:
        """
        将驼峰命名转换为下划线命名

        Args:
            camel_str: 驼峰命名字符串

        Returns:
            下划线命名字符串
        """
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", camel_str)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        验证邮箱格式

        Args:
            email: 邮箱地址

        Returns:
            是否有效
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def mask_sensitive_data(data: str, mask_char: str = "*", keep_start: int = 2, keep_end: int = 2) -> str:
        """
        遮蔽敏感数据

        Args:
            data: 原始数据
            mask_char: 遮蔽字符
            keep_start: 保留开头字符数
            keep_end: 保留结尾字符数

        Returns:
            遮蔽后的数据
        """
        if len(data) <= keep_start + keep_end:
            return mask_char * len(data)

        return data[:keep_start] + mask_char * (len(data) - keep_start - keep_end) + data[-keep_end:]


class TimeUtils:
    """时间处理工具类"""

    @staticmethod
    def get_current_timestamp() -> int:
        """获取当前时间戳（毫秒）"""
        return int(time.time() * 1000)

    @staticmethod
    def get_current_time_str(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        获取当前时间字符串

        Args:
            fmt: 时间格式

        Returns:
            时间字符串
        """
        return datetime.now().strftime(fmt)

    @staticmethod
    def timestamp_to_str(timestamp: int, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        时间戳转字符串

        Args:
            timestamp: 时间戳（毫秒）
            fmt: 时间格式

        Returns:
            时间字符串
        """
        return datetime.fromtimestamp(timestamp / 1000).strftime(fmt)


class JsonUtils:
    """JSON处理工具类"""

    @staticmethod
    def safe_loads(json_str: str, default: Any = None) -> Any:
        """
        安全的JSON解析

        Args:
            json_str: JSON字符串
            default: 解析失败时的默认值

        Returns:
            解析结果
        """
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, TypeError):
            return default

    @staticmethod
    def safe_dumps(obj: Any, default: Any = None, **kwargs) -> str:
        """
        安全的JSON序列化

        Args:
            obj: 要序列化的对象
            default: 序列化失败时的默认值
            **kwargs: json.dumps的其他参数

        Returns:
            JSON字符串
        """
        try:
            return json.dumps(obj, ensure_ascii=False, **kwargs)
        except (TypeError, ValueError):
            return str(default) if default is not None else "{}"

    @staticmethod
    def pretty_print(obj: Any, indent: int = 2) -> str:
        """
        格式化打印JSON

        Args:
            obj: 要打印的对象
            indent: 缩进空格数

        Returns:
            格式化的JSON字符串
        """
        return json.dumps(obj, ensure_ascii=False, indent=indent)


class ValidationUtils:
    """数据验证工具类"""

    @staticmethod
    def is_not_empty(value: Any) -> bool:
        """检查值是否非空"""
        if value is None:
            return False
        if isinstance(value, (str, list, dict, tuple)):
            return len(value) > 0
        return True

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """验证URL格式"""
        pattern = r"^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$"
        return bool(re.match(pattern, url))

    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """验证手机号格式（中国大陆）"""
        pattern = r"^1[3-9]\d{9}$"
        return bool(re.match(pattern, phone))


# 便捷的全局实例
file_utils = FileUtils()
string_utils = StringUtils()
time_utils = TimeUtils()
json_utils = JsonUtils()
validation_utils = ValidationUtils()
