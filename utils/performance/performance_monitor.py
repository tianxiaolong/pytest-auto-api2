#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Performance Monitor Module

This module provides performance monitor functionality.
"""

"""
性能监控模块
提供测试执行性能监控和优化功能

@Time   : 2023-12-20
@Author : txl
"""
import json
import threading
import time
from dataclasses import dataclass, field
from functools import wraps
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""

    test_name: str
    start_time: float
    end_time: float
    duration: float
    cpu_usage: float
    memory_usage: float
    success: bool
    error_message: Optional[str] = None


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.system_metrics: List[Dict[str, Any]] = []

    def start_monitoring(self):
        """开始系统监控"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_system)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def stop_monitoring(self):
        """停止系统监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)

    def _monitor_system(self):
        """监控系统资源"""
        while self.monitoring:
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()

                self.system_metrics.append(
                    {
                        "timestamp": time.time(),
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory.percent,
                        "memory_used": memory.used,
                        "memory_available": memory.available,
                    }
                )

                # 保持最近100个数据点
                if len(self.system_metrics) > 100:
                    self.system_metrics.pop(0)

            except Exception:
                pass

            time.sleep(1)

    def record_test_performance(
        self, test_name: str, start_time: float, end_time: float, success: bool, error_message: Optional[str] = None
    ):
        """记录测试性能"""
        duration = end_time - start_time

        # 获取当前系统资源使用情况
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent

        metrics = PerformanceMetrics(
            test_name=test_name,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            success=success,
            error_message=error_message,
        )

        self.metrics.append(metrics)

    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        if not self.metrics:
            return {"message": "暂无性能数据"}

        durations = [m.duration for m in self.metrics]
        cpu_usages = [m.cpu_usage for m in self.metrics]
        memory_usages = [m.memory_usage for m in self.metrics]

        success_count = sum(1 for m in self.metrics if m.success)
        total_count = len(self.metrics)

        return {
            "total_tests": total_count,
            "success_tests": success_count,
            "success_rate": (success_count / total_count) * 100,
            "duration": {
                "total": sum(durations),
                "average": sum(durations) / len(durations),
                "min": min(durations),
                "max": max(durations),
            },
            "cpu_usage": {"average": sum(cpu_usages) / len(cpu_usages), "min": min(cpu_usages), "max": max(cpu_usages)},
            "memory_usage": {
                "average": sum(memory_usages) / len(memory_usages),
                "min": min(memory_usages),
                "max": max(memory_usages),
            },
            "slowest_tests": sorted(
                [(m.test_name, m.duration) for m in self.metrics], key=lambda x: x[1], reverse=True
            )[:5],
        }

    def save_performance_report(self, file_path: str = "performance_report.json"):
        """保存性能报告"""
        summary = self.get_performance_summary()

        report = {
            "summary": summary,
            "detailed_metrics": [
                {
                    "test_name": m.test_name,
                    "duration": m.duration,
                    "cpu_usage": m.cpu_usage,
                    "memory_usage": m.memory_usage,
                    "success": m.success,
                    "error_message": m.error_message,
                }
                for m in self.metrics
            ],
            "system_metrics": self.system_metrics[-50:],  # 最近50个数据点
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)


# 全局性能监控器实例
performance_monitor = PerformanceMonitor()


def monitor_performance(test_name: Optional[str] = None):
    """性能监控装饰器"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = test_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            success = True
            error_message = None

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_message = str(e)
                raise
            finally:
                end_time = time.time()
                performance_monitor.record_test_performance(name, start_time, end_time, success, error_message)

        return wrapper

    return decorator


class TestDataCache:
    """测试数据缓存"""

    def __init__(self, max_size: int = 100):
        self.cache: Dict[str, Any] = {}
        self.access_times: Dict[str, float] = {}
        self.max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        if key in self.cache:
            self.access_times[key] = time.time()
            return self.cache[key]
        return None

    def set(self, key: str, value: Any):
        """设置缓存数据"""
        # 如果缓存已满，删除最久未访问的数据
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            self.remove(oldest_key)

        self.cache[key] = value
        self.access_times[key] = time.time()

    def remove(self, key: str):
        """删除缓存数据"""
        if key in self.cache:
            del self.cache[key]
            del self.access_times[key]

    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.access_times.clear()

    def size(self) -> int:
        """获取缓存大小"""
        return len(self.cache)

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        return {
            "size": self.size(),
            "max_size": self.max_size,
            "keys": list(self.cache.keys()),
            "usage_rate": (self.size() / self.max_size) * 100,
        }


# 全局测试数据缓存实例
test_data_cache = TestDataCache()


def cached_test_data(cache_key: Optional[str] = None, ttl: int = 3600):
    """测试数据缓存装饰器"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            key = cache_key or f"{func.__module__}.{func.__name__}:{hash(str(args) + str(kwargs))}"

            # 尝试从缓存获取
            cached_result = test_data_cache.get(key)
            if cached_result is not None:
                return cached_result

            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            test_data_cache.set(key, result)

            return result

        return wrapper

    return decorator


def optimize_test_execution():
    """优化测试执行"""
    # 启动性能监控
    performance_monitor.start_monitoring()

    # 设置进程优先级（仅在支持的系统上）
    try:
        import os

        if hasattr(os, "nice"):
            os.nice(-5)  # 提高优先级
    except (OSError, AttributeError):
        pass

    # 预热JIT编译器（如果使用PyPy）
    try:
        import __pypy__

        # PyPy特定的优化
        pass
    except ImportError:
        pass


def cleanup_performance_monitoring():
    """清理性能监控"""
    performance_monitor.stop_monitoring()

    # 保存性能报告
    try:
        performance_monitor.save_performance_report()
        print("📊 性能报告已保存到 performance_report.json")
    except Exception as e:
        print(f"⚠️ 保存性能报告失败: {e}")

    # 显示缓存统计
    cache_stats = test_data_cache.get_stats()
    print(f"💾 缓存统计: {cache_stats}")


if __name__ == "__main__":
    # 测试性能监控
    @monitor_performance("test_example")
    def test_function():
        time.sleep(0.1)
        return "test result"

    optimize_test_execution()

    # 运行测试
    for i in range(5):
        test_function()

    # 显示性能摘要
    summary = performance_monitor.get_performance_summary()
    print("性能摘要:", summary)

    cleanup_performance_monitoring()
