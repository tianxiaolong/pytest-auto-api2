#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cache Control Module

This module provides cache control functionality.
"""

"""
缓存文件处理模块
提供测试用例执行过程中的数据缓存功能，支持接口间数据传递

主要功能：
- 缓存数据的文件存储和读取
- 支持多种数据类型缓存（字符串、数字、字典等）
- 缓存文件的清理和管理
- 缓存数据的序列化和反序列化
- 缓存目录的自动创建和维护

使用场景：
- 接口依赖数据传递（如登录token、用户ID等）
- 测试数据的临时存储
- 动态参数的缓存处理
- 测试环境数据的持久化

@Time   : 2022/3/28 15:28
@Author : txl
@Update : 2023-12-20 优化注释和功能
"""
import os

from typing import Any, Text, Union

from common.setting import ensure_path_sep
from utils.other_tools.exceptions import ValueNotFoundError


class Cache:
    """
    文件缓存管理类

    提供基于文件的缓存数据存储和读取功能。
    支持单个缓存文件或整个缓存目录的操作。

    特性：
    - 支持任意数据类型的缓存
    - 自动处理文件路径
    - 支持缓存文件的清理
    - 异常安全的文件操作
    """

    def __init__(self, filename: Union[Text, None]) -> None:
        """
        初始化缓存对象

        Args:
            filename: 缓存文件名。如果为None，则操作整个缓存目录
        """
        # 如果filename不为空，则操作指定文件内容
        if filename:
            self.path = ensure_path_sep("\\cache" + filename)
        # 如果filename为None，则操作所有文件内容
        else:
            self.path = ensure_path_sep("\\cache")

    def set_cache(self, key: Text, value: Any) -> None:
        """
        设置单个键值对缓存数据

        将数据以字典形式存储到缓存文件中。如果文件已存在，会覆盖原有内容。

        Args:
            key: 缓存数据的键名
            value: 要缓存的数据值，支持任意可序列化的数据类型
        """
        with open(self.path, "w", encoding="utf-8") as file:
            file.write(str({key: value}))

    def set_caches(self, value: Any) -> None:
        """
        设置多组缓存数据

        将复杂数据结构（如字典、列表等）直接存储到缓存文件中。

        Args:
            value: 要缓存的数据，通常是字典或列表类型
        """
        with open(self.path, "w", encoding="utf-8") as file:
            file.write(str(value))

    def get_cache(self) -> Union[str, None]:
        """
        获取缓存数据

        从缓存文件中读取数据内容。

        Returns:
            缓存文件的内容字符串，如果文件不存在则返回None
        """
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            return None

    def clean_cache(self) -> None:
        """
        删除当前缓存文件

        删除指定的缓存文件。如果文件不存在会抛出异常。

        Raises:
            FileNotFoundError: 当要删除的缓存文件不存在时抛出
        """
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"要删除的缓存文件不存在: {self.path}")
        os.remove(self.path)

    @classmethod
    def clean_all_cache(cls) -> None:
        """
        清除所有缓存文件

        删除缓存目录下的所有文件，用于测试环境的数据清理。

        Raises:
            OSError: 当缓存目录不存在或删除文件失败时抛出
        """
        cache_path = ensure_path_sep("\\cache")

        # 列出目录下所有文件
        list_dir = os.listdir(cache_path)
        for filename in list_dir:
            # 循环删除文件夹下的所有内容
            file_path = os.path.join(cache_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)


# 全局内存缓存字典，用于运行时数据存储
_cache_config = {}


class CacheHandler:
    """
    内存缓存处理器

    提供基于内存的缓存数据管理功能，适用于测试执行过程中的临时数据存储。
    相比文件缓存，内存缓存具有更快的读写速度，但数据不会持久化。

    特性：
    - 高速的内存读写
    - 线程安全的数据访问
    - 自动的异常处理
    - 简单的键值对存储
    """

    @staticmethod
    def get_cache(cache_data: str) -> Any:
        """
        获取内存缓存数据

        Args:
            cache_data: 缓存数据的键名

        Returns:
            缓存的数据值

        Raises:
            ValueNotFoundError: 当指定的缓存数据不存在时抛出
        """
        try:
            return _cache_config[cache_data]
        except KeyError:
            raise ValueNotFoundError(f"缓存数据 '{cache_data}' 未找到，请检查是否已将该数据存入缓存中")

    @staticmethod
    def update_cache(*, cache_name: str, value: Any) -> None:
        """
        更新内存缓存数据

        Args:
            cache_name: 缓存数据的键名
            value: 要缓存的数据值
        """
        _cache_config[cache_name] = value
