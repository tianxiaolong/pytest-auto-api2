#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
增强版 Mitmproxy 控制模块

本模块为API测试用例生成提供高级mitmproxy控制功能。
支持将HTTP请求自动转换为YAML测试用例，具备智能过滤和数据处理能力。

功能特性:
- 智能URL过滤和请求拦截
- 自动YAML测试用例生成
- 智能数据类型转换
- 请求头提取和处理
- 响应断言生成
- URL参数处理

@Author: txl
@Version: 2.0.0
@Updated: 2025-05-31
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Text, Tuple
from urllib.parse import parse_qs, urlparse

import mitmproxy.http
from mitmproxy import ctx
from ruamel import yaml


class EnhancedMitmproxyRecorder:
    """
    增强版 Mitmproxy 录制器，用于API测试用例生成

    本类提供高级功能，用于通过mitmproxy拦截HTTP请求
    并自动将其转换为结构化的YAML测试用例。

    功能特性:
    - 智能URL过滤，支持可配置的模式匹配
    - 自动测试用例生成，具备合适的命名规则
    - 智能数据类型转换和验证
    - 请求头提取和清理
    - 响应断言生成
    - URL参数处理和提取
    - 错误处理和日志记录

    参考资料: https://blog.wolfogre.com/posts/usage-of-mitmproxy/
    """

    # 默认过滤的文件类型
    DEFAULT_FILTER_EXTENSIONS = [
        ".css", ".js", ".map", ".ico", ".png", ".jpg", ".jpeg", ".gif",
        ".svg", ".woff", ".woff2", ".ttf", ".eot", ".mp4", ".mp3", ".pdf"
    ]

    # 敏感请求头（需要过滤或脱敏）
    SENSITIVE_HEADERS = [
        "authorization", "cookie", "x-auth-token", "x-api-key",
        "x-csrf-token", "x-session-id"
    ]

    def __init__(
        self,
        filter_urls: List[str],
        output_file: str = "./data/yaml_data/proxy_generated_cases.yaml",
        max_cases: int = 100,
        enable_logging: bool = True
    ):
        """
        初始化增强版 Mitmproxy 录制器

        Args:
            filter_urls: 需要过滤和录制的URL模式列表
            output_file: 生成测试用例的输出YAML文件路径
            max_cases: 最大录制用例数量（防止文件过大）
            enable_logging: 是否启用详细日志记录
        """
        # 统一的属性命名
        self.filter_urls = filter_urls
        self.output_file = Path(output_file)
        self.max_cases = max_cases
        self.enable_logging = enable_logging

        # 计数器和状态
        self.case_counter = 1
        self.recorded_cases = 0
        self.session_start_time = datetime.now()

        # 确保输出目录存在
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        # 初始化日志
        if self.enable_logging:
            self._log_session_start()

    def _log_session_start(self) -> None:
        """记录会话开始信息"""
        try:
            ctx.log.info("=" * 80)
            ctx.log.info("🚀 增强版 Mitmproxy 录制器已启动")
            ctx.log.info(f"📁 输出文件: {self.output_file}")
            ctx.log.info(f"🔍 过滤URL: {self.filter_urls}")
            ctx.log.info(f"📊 最大用例数: {self.max_cases}")
            ctx.log.info(f"⏰ 会话开始时间: {self.session_start_time}")
            ctx.log.info("=" * 80)
        except Exception as e:
            print(f"⚠️ 日志初始化失败: {e}")

    def response(self, flow: mitmproxy.http.HTTPFlow) -> None:
        """
        增强版 mitmproxy 响应处理器

        处理HTTP响应并将其转换为结构化的YAML测试用例，
        具备智能过滤和数据验证功能。

        Args:
            flow: 包含请求和响应数据的 mitmproxy HTTP flow 对象
        """
        try:
            # 检查是否达到最大录制数量
            if self.recorded_cases >= self.max_cases:
                if self.enable_logging:
                    ctx.log.info(f"🛑 已达到最大用例数 ({self.max_cases})，停止录制。")
                return

            url = flow.request.url

            # 智能过滤：跳过静态资源和不相关的请求
            if not self._should_record_request(url, flow.request.method):
                return

            # 检查URL是否匹配过滤条件
            if not self._is_url_filtered(url):
                return

            # 生成测试用例
            test_case = self._generate_test_case(flow)
            if test_case:
                self._save_test_case(test_case)
                self.recorded_cases += 1

                if self.enable_logging:
                    ctx.log.info(f"✅ 已录制用例 {self.recorded_cases}/{self.max_cases}: {list(test_case.keys())[0]}")

        except Exception as e:
            if self.enable_logging:
                ctx.log.error(f"❌ 处理请求时出错: {e}")
            print(f"❌ 响应处理器错误: {e}")

    def _should_record_request(self, url: str, method: str) -> bool:
        """
        智能请求过滤

        Args:
            url: 请求URL
            method: HTTP方法

        Returns:
            bool: 如果请求应该被录制则返回True
        """
        # 过滤静态资源
        if any(ext in url.lower() for ext in self.DEFAULT_FILTER_EXTENSIONS):
            return False

        # 过滤非API请求方法
        if method not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
            return False

        # 过滤明显的非API路径
        non_api_patterns = [
            "/static/", "/assets/", "/public/", "/images/", "/css/", "/js/",
            "/fonts/", "/favicon", "/robots.txt", "/sitemap"
        ]

        if any(pattern in url.lower() for pattern in non_api_patterns):
            return False

        return True

    def _is_url_filtered(self, url: str) -> bool:
        """
        检查URL是否匹配任何过滤模式

        Args:
            url: 要检查的请求URL

        Returns:
            bool: 如果URL应该被处理则返回True
        """
        return any(filter_url in url for filter_url in self.filter_urls)

    def _generate_test_case(self, flow: mitmproxy.http.HTTPFlow) -> Optional[Dict[str, Any]]:
        """
        从HTTP流生成结构化测试用例

        Args:
            flow: mitmproxy HTTP流对象

        Returns:
            包含生成的测试用例的字典，如果生成失败则返回None
        """
        try:
            url = flow.request.url
            method = flow.request.method

            # 生成用例ID
            case_id = self._generate_case_id(url)

            # 处理请求数据
            request_data = self._process_request_data(flow.request)

            # 处理请求头
            headers = self._process_headers(flow.request.headers)

            # 处理响应断言
            assertions = self._generate_assertions(flow.response)

            # 处理URL参数
            url_path, url_params = self._process_url_parameters(url)

            # 构建测试用例
            test_case = {
                case_id: {
                    "url": url_path,
                    "method": method,
                    "detail": self._generate_case_description(url, method),
                    "headers": headers,
                    "requestType": self._determine_request_type(method, flow.request),
                    "is_run": True,
                    "data": url_params if url_params else request_data,
                    "dependence_case": None,
                    "dependence_case_data": None,
                    "assert": assertions,
                    "sql": None,
                    "setup_sql": None,
                    "teardown_sql": None,
                    # 添加元数据
                    "_metadata": {
                        "generated_at": datetime.now().isoformat(),
                        "source_url": url,
                        "response_status": flow.response.status_code if flow.response else None,
                        "content_type": flow.response.headers.get("content-type", "") if flow.response else ""
                    }
                }
            }

            return test_case

        except Exception as e:
            if self.enable_logging:
                ctx.log.error(f"❌ 生成测试用例失败: {e}")
            return None

    def _generate_case_id(self, url: str) -> str:
        """
        从URL生成唯一的用例ID

        Args:
            url: 请求URL

        Returns:
            str: 生成的用例ID
        """
        # 提取URL路径的最后一部分作为基础名称
        url_path = urlparse(url).path
        path_parts = [part for part in url_path.split('/') if part]

        if path_parts:
            base_name = path_parts[-1]
            # 清理特殊字符
            base_name = re.sub(r'[^\w\-_]', '_', base_name)
        else:
            base_name = "api_request"

        # 添加计数器确保唯一性
        case_id = f"{base_name}_{self.case_counter:03d}"
        self.case_counter += 1

        return case_id

    def _process_request_data(self, request: mitmproxy.http.Request) -> Optional[Any]:
        """
        处理和转换请求数据

        Args:
            request: mitmproxy请求对象

        Returns:
            处理后的请求数据或None
        """
        try:
            if not request.text:
                return None

            # 尝试解析JSON数据
            try:
                return json.loads(request.text)
            except json.JSONDecodeError:
                pass

            # 尝试解析表单数据
            if request.headers.get("content-type", "").startswith("application/x-www-form-urlencoded"):
                return dict(parse_qs(request.text))

            # 返回原始文本
            return request.text

        except Exception as e:
            if self.enable_logging:
                ctx.log.warning(f"⚠️ 处理请求数据失败: {e}")
            return None

    def _process_headers(self, headers) -> Dict[str, str]:
        """
        处理和清理请求头

        Args:
            headers: mitmproxy请求头对象

        Returns:
            处理后的请求头字典
        """
        processed_headers = {}

        for key, value in headers.items():
            key_lower = key.lower()

            # 过滤敏感头信息
            if key_lower in self.SENSITIVE_HEADERS:
                processed_headers[key] = "***已过滤***"
            # 保留重要的API头信息
            elif key_lower in ["content-type", "accept", "user-agent", "x-requested-with"]:
                processed_headers[key] = value
            # 保留自定义API头（通常以x-开头）
            elif key_lower.startswith("x-") and key_lower not in self.SENSITIVE_HEADERS:
                processed_headers[key] = value

        return processed_headers

    def _generate_assertions(self, response: Optional[mitmproxy.http.Response]) -> Optional[Dict[str, Any]]:
        """
        基于响应生成智能断言

        Args:
            response: mitmproxy响应对象

        Returns:
            包含断言配置的字典或None
        """
        if not response:
            return None

        try:
            assertions = {}

            # 状态码断言
            assertions["status_code"] = response.status_code

            # 尝试解析响应JSON并生成断言
            if response.text:
                try:
                    response_data = json.loads(response.text)

                    # 常见的响应字段断言
                    if isinstance(response_data, dict):
                        # code字段断言
                        if "code" in response_data:
                            assertions["response_data"] = {
                                "jsonpath": "$.code",
                                "type": "==",
                                "value": response_data["code"],
                                "message": "响应code码验证失败"
                            }
                        # status字段断言
                        elif "status" in response_data:
                            assertions["response_data"] = {
                                "jsonpath": "$.status",
                                "type": "==",
                                "value": response_data["status"],
                                "message": "响应status验证失败"
                            }
                        # success字段断言
                        elif "success" in response_data:
                            assertions["response_data"] = {
                                "jsonpath": "$.success",
                                "type": "==",
                                "value": response_data["success"],
                                "message": "响应success验证失败"
                            }

                except json.JSONDecodeError:
                    # 非JSON响应，只验证状态码
                    pass

            return assertions

        except Exception as e:
            if self.enable_logging:
                ctx.log.warning(f"⚠️ 生成断言失败: {e}")
            return {"status_code": 200}  # 默认断言

    def _process_url_parameters(self, url: str) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        处理URL参数并提取查询字符串

        Args:
            url: 包含潜在查询参数的完整URL

        Returns:
            (干净的URL路径, 查询参数字典)的元组
        """
        try:
            parsed_url = urlparse(url)

            # 构建干净的URL路径（不包含查询参数）
            clean_url = f"{parsed_url.path}"

            # 解析查询参数
            if parsed_url.query:
                query_params = {}
                for key, values in parse_qs(parsed_url.query).items():
                    # 如果只有一个值，直接使用字符串；否则使用列表
                    query_params[key] = values[0] if len(values) == 1 else values
                return clean_url, query_params

            return clean_url, None

        except Exception as e:
            if self.enable_logging:
                ctx.log.warning(f"⚠️ 处理URL参数失败: {e}")
            return url, None

    def _generate_case_description(self, url: str, method: str) -> str:
        """
        为测试用例生成描述性名称

        Args:
            url: 请求URL
            method: HTTP方法

        Returns:
            str: 生成的描述
        """
        try:
            parsed_url = urlparse(url)
            path_parts = [part for part in parsed_url.path.split('/') if part]

            if path_parts:
                # 使用路径的最后两部分构建描述
                if len(path_parts) >= 2:
                    description = f"{method} {path_parts[-2]}/{path_parts[-1]}"
                else:
                    description = f"{method} {path_parts[-1]}"
            else:
                description = f"{method} API请求"

            return description

        except Exception:
            return f"{method} API请求"

    def _determine_request_type(self, method: str, request: mitmproxy.http.Request) -> str:
        """
        基于方法和内容确定请求类型

        Args:
            method: HTTP方法
            request: mitmproxy请求对象

        Returns:
            str: 请求类型 (json, form, params, 等)
        """
        if method.upper() == "GET":
            return "params"

        content_type = request.headers.get("content-type", "").lower()

        if "application/json" in content_type:
            return "json"
        elif "application/x-www-form-urlencoded" in content_type:
            return "form"
        elif "multipart/form-data" in content_type:
            return "form"
        else:
            return "json"  # 默认使用json

    def _save_test_case(self, test_case: Dict[str, Any]) -> None:
        """
        保存测试用例到YAML文件

        Args:
            test_case: 要保存的测试用例字典
        """
        try:
            # 读取现有数据
            existing_data = {}
            if self.output_file.exists():
                try:
                    with open(self.output_file, 'r', encoding='utf-8') as f:
                        existing_data = yaml.safe_load(f) or {}
                except Exception as e:
                    if self.enable_logging:
                        ctx.log.warning(f"⚠️ 读取现有文件失败: {e}")

            # 合并新数据
            existing_data.update(test_case)

            # 写入文件
            with open(self.output_file, 'w', encoding='utf-8') as f:
                yaml.dump(existing_data, f, default_flow_style=False,
                         allow_unicode=True, sort_keys=False)

        except Exception as e:
            if self.enable_logging:
                ctx.log.error(f"❌ 保存测试用例失败: {e}")
            print(f"❌ 保存测试用例失败: {e}")


# ============================================================================
# Mitmproxy 配置和使用说明
# ============================================================================

def create_recorder(
        filter_urls: Optional[List[str]] = None,
        output_file: Optional[str] = None,
        max_cases: int = 100
) -> EnhancedMitmproxyRecorder:
    """
    工厂函数，用于创建配置好的录制器实例

    Args:
        filter_urls: 需要过滤的URL模式列表
        output_file: 输出YAML文件路径
        max_cases: 最大录制用例数量

    Returns:
        EnhancedMitmproxyRecorder: 配置好的录制器实例
    """
    if filter_urls is None:
        filter_urls = ["https://www.wanandroid.com"]

    if output_file is None:
        output_file = "./data/yaml_data/proxy_generated_cases.yaml"

    return EnhancedMitmproxyRecorder(
        filter_urls=filter_urls,
        output_file=output_file,
        max_cases=max_cases
    )


# ============================================================================
# 使用说明:
# ============================================================================
#
# 1. 配置过滤URL:
#    在下面的 addons 列表中修改 filter_urls 参数
#
# 2. 启动代理录制:
#    控制台输入以下命令开启代理模式进行录制:
#
#    基础命令:
#    mitmweb -s .\utils\recording\mitmproxy_control_optimized.py -p 8888
#
#    高级命令 (指定监听地址):
#    mitmweb -s .\utils\recording\mitmproxy_control_optimized.py -p 8888 --listen-host 0.0.0.0
#
#    命令行模式:
#    mitmdump -s .\utils\recording\mitmproxy_control_optimized.py -p 8888
#
# 3. 配置浏览器代理:
#    HTTP代理: 127.0.0.1:8888
#    HTTPS代理: 127.0.0.1:8888
#
# 4. 访问目标网站进行操作，系统会自动录制API请求
#
# 5. 生成的测试用例保存在: ./data/yaml_data/proxy_generated_cases.yaml
#
# ============================================================================

# 默认配置 - 可以根据需要修改
addons = [
    create_recorder(
        filter_urls=[
            "https://www.wanandroid.com",
            # 添加更多需要录制的URL模式
            # "https://api.example.com",
            # "https://test.example.com/api",
        ],
        output_file="./data/yaml_data/proxy_generated_cases.yaml",
        max_cases=100
    )
]

# 向后兼容性支持
Counter = EnhancedMitmproxyRecorder
