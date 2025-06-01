#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Set Current Request Cache Module

This module provides set current request cache functionality.
"""

"""
# @Time    : 2022/6/2 11:30
# @Author : txl
# @Email   : 1603453211@qq.com
# @File    : set_current_request_cache
# @describe:
"""
import json
from typing import Text

from jsonpath import jsonpath

from utils.cache_process.cache_control import CacheHandler
from utils.other_tools.exceptions import ValueNotFoundError


class SetCurrentRequestCache:
    """将用例中的请求或者响应内容存入缓存"""

    def __init__(self, current_request_set_cache, request_data, response_data):
        self.current_request_set_cache = current_request_set_cache
        self.request_data = {"data": request_data}
        self.response_data = response_data.text

    def set_request_cache(self, jsonpath_value: Text, cache_name: Text) -> None:
        """将接口的请求参数存入缓存"""
        _request_data = jsonpath(self.request_data, jsonpath_value)
        if _request_data is not False:
            CacheHandler.update_cache(cache_name=cache_name, value=_request_data[0])
            # Cache(cache_name).set_caches(_request_data[0])
        else:
            raise ValueNotFoundError(
                "缓存设置失败，程序中未检测到需要缓存的数据。"
                f"请求参数: {self.request_data}"
                f"提取的 jsonpath 内容: {jsonpath_value}"
            )

    def set_response_cache(self, jsonpath_value: Text, cache_name):
        """将响应结果存入缓存"""
        try:
            response_json = json.loads(self.response_data)
        except json.JSONDecodeError as e:
            raise ValueNotFoundError(
                f"缓存设置失败，响应数据不是有效的JSON格式。"
                f"响应内容: {self.response_data[:200]}..."
                f"JSON解析错误: {e}"
            )

        _response_data = jsonpath(response_json, jsonpath_value)
        if _response_data is not False and len(_response_data) > 0:
            CacheHandler.update_cache(cache_name=cache_name, value=_response_data[0])
            # Cache(cache_name).set_caches(_response_data[0])
        else:
            # 提供更详细的错误信息
            available_paths = self._get_available_jsonpaths(response_json)
            raise ValueNotFoundError(
                f"缓存设置失败，JSONPath未找到匹配的数据。\n"
                f"目标JSONPath: {jsonpath_value}\n"
                f"缓存名称: {cache_name}\n"
                f"响应数据结构: {json.dumps(response_json, indent=2, ensure_ascii=False)[:500]}...\n"
                f"建议的可用路径: {available_paths[:5]}"  # 只显示前5个建议
            )

    def _get_available_jsonpaths(self, data, prefix="$"):
        """获取可用的JSONPath建议"""
        paths = []
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{prefix}.{key}"
                paths.append(current_path)
                if isinstance(value, (dict, list)) and len(str(value)) < 1000:  # 避免过深递归
                    paths.extend(self._get_available_jsonpaths(value, current_path))
        elif isinstance(data, list) and len(data) > 0:
            paths.append(f"{prefix}[*]")
            if len(data) > 0:
                paths.extend(self._get_available_jsonpaths(data[0], f"{prefix}[0]"))
        return paths[:10]  # 限制返回数量

    def set_caches_main(self):
        """设置缓存"""
        if self.current_request_set_cache is not None:
            for i in self.current_request_set_cache:
                _jsonpath = i.jsonpath
                _cache_name = i.name
                if i.type == "request":
                    self.set_request_cache(jsonpath_value=_jsonpath, cache_name=_cache_name)
                elif i.type == "response":
                    self.set_response_cache(jsonpath_value=_jsonpath, cache_name=_cache_name)
