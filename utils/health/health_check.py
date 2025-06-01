#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Health Check Module

This module provides health check functionality.
"""

"""
健康检查模块
提供系统健康状态检查和监控功能

@Time   : 2023-12-20
@Author : txl
"""
from pathlib import Path
import json
import os
import requests
import sys
import threading
import time

from typing import Any, Dict, List
import psutil

from http.server import BaseHTTPRequestHandler, HTTPServer


class HealthChecker:
    """健康检查器"""

    def __init__(self):
        self.checks = {}
        self.last_check_time = None
        self.check_interval = 30  # 30秒检查一次

    def register_check(self, name: str, check_func, critical: bool = False):
        """注册健康检查项"""
        self.checks[name] = {"func": check_func, "critical": critical, "last_result": None, "last_check": None}

    def check_system_resources(self) -> Dict[str, Any]:
        """检查系统资源"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return {
                "status": "healthy",
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "warnings": self._get_resource_warnings(cpu_percent, memory.percent, disk.percent),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _get_resource_warnings(self, cpu: float, memory: float, disk: float) -> List[str]:
        """获取资源警告"""
        warnings = []
        if cpu > 80:
            warnings.append(f"CPU使用率过高: {cpu}%")
        if memory > 85:
            warnings.append(f"内存使用率过高: {memory}%")
        if disk > 90:
            warnings.append(f"磁盘使用率过高: {disk}%")
        return warnings

    def check_dependencies(self) -> Dict[str, Any]:
        """检查依赖项"""
        try:
            dependencies = {
                "pytest": self._check_module("pytest"),
                "requests": self._check_module("requests"),
                "allure": self._check_module("allure"),
                "yaml": self._check_module("yaml"),
                "openpyxl": self._check_module("openpyxl"),
            }

            failed_deps = [name for name, status in dependencies.items() if not status]

            return {
                "status": "healthy" if not failed_deps else "error",
                "dependencies": dependencies,
                "failed_dependencies": failed_deps,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _check_module(self, module_name: str) -> bool:
        """检查模块是否可用"""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False

    def check_file_system(self) -> Dict[str, Any]:
        """检查文件系统"""
        try:
            required_dirs = ["data", "logs", "report", "test_case", "utils"]
            missing_dirs = []

            for dir_name in required_dirs:
                if not Path(dir_name).exists():
                    missing_dirs.append(dir_name)

            # 检查关键文件
            required_files = ["requirements.txt", "pytest.ini", "common/config.yaml"]
            missing_files = []

            for file_name in required_files:
                if not Path(file_name).exists():
                    missing_files.append(file_name)

            return {
                "status": "healthy" if not missing_dirs and not missing_files else "warning",
                "missing_directories": missing_dirs,
                "missing_files": missing_files,
                "writable": os.access(".", os.W_OK),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def check_network_connectivity(self) -> Dict[str, Any]:
        """检查网络连接"""
        try:
            # 检查外网连接
            test_urls = ["https://www.baidu.com", "https://www.google.com", "https://httpbin.org/get"]

            connectivity_results = {}
            for url in test_urls:
                try:
                    response = requests.get(url, timeout=5)
                    connectivity_results[url] = {
                        "status": "ok",
                        "status_code": response.status_code,
                        "response_time": response.elapsed.total_seconds(),
                    }
                except Exception as e:
                    connectivity_results[url] = {"status": "error", "error": str(e)}

            successful_connections = sum(1 for result in connectivity_results.values() if result["status"] == "ok")

            return {
                "status": "healthy" if successful_connections > 0 else "error",
                "connectivity_results": connectivity_results,
                "successful_connections": successful_connections,
                "total_tests": len(test_urls),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def check_configuration(self) -> Dict[str, Any]:
        """检查配置"""
        try:
            config_file = Path("common/config.yaml")
            if not config_file.exists():
                return {"status": "error", "error": "Configuration file not found"}

            # 检查环境变量
            required_env_vars = ["PROJECT_NAME", "HOST"]
            missing_env_vars = []

            for var in required_env_vars:
                if not os.getenv(var):
                    missing_env_vars.append(var)

            return {
                "status": "healthy" if not missing_env_vars else "warning",
                "config_file_exists": True,
                "missing_env_vars": missing_env_vars,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def run_all_checks(self) -> Dict[str, Any]:
        """运行所有健康检查"""
        self.last_check_time = time.time()

        # 注册默认检查项
        if not self.checks:
            self.register_check("system_resources", self.check_system_resources, critical=True)
            self.register_check("dependencies", self.check_dependencies, critical=True)
            self.register_check("file_system", self.check_file_system, critical=False)
            self.register_check("network", self.check_network_connectivity, critical=False)
            self.register_check("configuration", self.check_configuration, critical=True)

        results = {}
        overall_status = "healthy"
        critical_failures = []

        for name, check_info in self.checks.items():
            try:
                result = check_info["func"]()
                check_info["last_result"] = result
                check_info["last_check"] = time.time()
                results[name] = result

                # 检查关键项目的状态
                if check_info["critical"] and result.get("status") == "error":
                    critical_failures.append(name)
                    overall_status = "unhealthy"
                elif result.get("status") == "warning" and overall_status == "healthy":
                    overall_status = "warning"

            except Exception as e:
                error_result = {"status": "error", "error": str(e)}
                check_info["last_result"] = error_result
                check_info["last_check"] = time.time()
                results[name] = error_result

                if check_info["critical"]:
                    critical_failures.append(name)
                    overall_status = "unhealthy"

        return {
            "overall_status": overall_status,
            "timestamp": self.last_check_time,
            "critical_failures": critical_failures,
            "checks": results,
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform,
                "pid": os.getpid(),
                "uptime": time.time() - psutil.Process().create_time(),
            },
        }


class HealthCheckHandler(BaseHTTPRequestHandler):
    """健康检查HTTP处理器"""

    def __init__(self, health_checker: HealthChecker, *args, **kwargs):
        self.health_checker = health_checker
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """处理GET请求"""
        if self.path == "/health":
            self.handle_health_check()
        elif self.path == "/health/detailed":
            self.handle_detailed_health_check()
        elif self.path == "/health/live":
            self.handle_liveness_check()
        elif self.path == "/health/ready":
            self.handle_readiness_check()
        else:
            self.send_error(404, "Not Found")

    def handle_health_check(self):
        """处理基础健康检查"""
        try:
            health_status = self.health_checker.run_all_checks()
            status_code = 200 if health_status["overall_status"] in ["healthy", "warning"] else 503

            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            response = {
                "status": health_status["overall_status"],
                "timestamp": health_status["timestamp"],
                "message": self._get_status_message(health_status["overall_status"]),
            }

            self.wfile.write(json.dumps(response, ensure_ascii=False).encode())
        except Exception as e:
            self.send_error(500, str(e))

    def handle_detailed_health_check(self):
        """处理详细健康检查"""
        try:
            health_status = self.health_checker.run_all_checks()
            status_code = 200 if health_status["overall_status"] in ["healthy", "warning"] else 503

            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(json.dumps(health_status, ensure_ascii=False, indent=2).encode())
        except Exception as e:
            self.send_error(500, str(e))

    def handle_liveness_check(self):
        """处理存活检查"""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        response = {"status": "alive", "timestamp": time.time(), "pid": os.getpid()}

        self.wfile.write(json.dumps(response).encode())

    def handle_readiness_check(self):
        """处理就绪检查"""
        try:
            # 简单的就绪检查
            critical_checks = ["dependencies", "configuration"]
            ready = True

            for check_name in critical_checks:
                if check_name in self.health_checker.checks:
                    check_info = self.health_checker.checks[check_name]
                    if check_info["last_result"] and check_info["last_result"].get("status") == "error":
                        ready = False
                        break

            status_code = 200 if ready else 503
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            response = {"status": "ready" if ready else "not_ready", "timestamp": time.time()}

            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            self.send_error(500, str(e))

    def _get_status_message(self, status: str) -> str:
        """获取状态消息"""
        messages = {"healthy": "系统运行正常", "warning": "系统运行正常，但有警告", "unhealthy": "系统存在严重问题"}
        return messages.get(status, "未知状态")

    def log_message(self, format, *args):
        """禁用默认日志"""
        pass


def start_health_server(port: int = 8080):
    """启动健康检查服务器"""
    health_checker = HealthChecker()

    def handler(*args, **kwargs):
        HealthCheckHandler(health_checker, *args, **kwargs)

    server = HTTPServer(("0.0.0.0", port), handler)

    print(f"🏥 健康检查服务器启动在端口 {port}")
    print(f"   健康检查: http://localhost:{port}/health")
    print(f"   详细检查: http://localhost:{port}/health/detailed")
    print(f"   存活检查: http://localhost:{port}/health/live")
    print(f"   就绪检查: http://localhost:{port}/health/ready")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 健康检查服务器已停止")
        server.shutdown()


def main():
    """主函数"""
    health_checker = HealthChecker()

    print("🏥 运行健康检查...")
    health_status = health_checker.run_all_checks()

    print("\n📊 健康检查结果:")
    print(f"   总体状态: {health_status['overall_status']}")
    print(f"   检查时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(health_status['timestamp']))}")

    if health_status["critical_failures"]:
        print(f"   关键失败: {health_status['critical_failures']}")

    for check_name, result in health_status["checks"].items():
        status_icon = "✅" if result["status"] == "healthy" else "⚠️" if result["status"] == "warning" else "❌"
        print(f"   {status_icon} {check_name}: {result['status']}")

    # 启动HTTP服务器（可选）
    import sys

    if "--server" in sys.argv:
        port = 8080
        if "--port" in sys.argv:
            port_index = sys.argv.index("--port") + 1
            if port_index < len(sys.argv):
                port = int(sys.argv[port_index])

        start_health_server(port)


if __name__ == "__main__":
    main()
