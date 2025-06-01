#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Alert Level Manager Module

This module provides alert level management functionality.
"""

"""
告警级别管理模块
根据测试结果自动判断告警级别并提供相应的图标和颜色
@Author : txl
"""

from typing import Dict, Any, Optional
from enum import Enum


class AlertLevel(Enum):
    """告警级别枚举"""
    CRITICAL = "critical"  # 严重 - 大量失败
    HIGH = "high"         # 高级 - 部分失败
    MEDIUM = "medium"     # 中级 - 少量失败
    LOW = "low"          # 低级 - 全部成功
    INFO = "info"        # 信息 - 无测试或跳过


def get_warning_level_info(color: str) -> Dict[str, Any]:
    """
    根据预警颜色获取等级和图标
    
    Args:
        color: 预警颜色 (red/orange/yellow/blue/green)
        
    Returns:
        包含图标和级别信息的字典
    """
    levels = {
        "red": {
            "icon": "🔴", 
            "level": "[I级/特别严重]",
            "color": "#FF0000",
            "priority": 1,
            "description": "严重故障，需要立即处理"
        },
        "orange": {
            "icon": "🟠", 
            "level": "[II级/严重]",
            "color": "#FF8C00", 
            "priority": 2,
            "description": "重要故障，需要尽快处理"
        },
        "yellow": {
            "icon": "🟡", 
            "level": "[III级/较重]",
            "color": "#FFD700",
            "priority": 3, 
            "description": "一般故障，需要关注"
        },
        "blue": {
            "icon": "🔵", 
            "level": "[IV级/一般]",
            "color": "#1E90FF",
            "priority": 4,
            "description": "轻微问题，建议优化"
        },
        "green": {
            "icon": "🟢", 
            "level": "[正常]",
            "color": "#32CD32",
            "priority": 5,
            "description": "运行正常，无需处理"
        }
    }
    
    return levels.get(color, {
        "icon": "⚪", 
        "level": "[未知]",
        "color": "#808080",
        "priority": 0,
        "description": "未知状态"
    })


def calculate_alert_level(success_rate: float, total_cases: int, failed_cases: int) -> Dict[str, Any]:
    """
    根据测试结果计算告警级别
    
    Args:
        success_rate: 成功率 (0-100)
        total_cases: 总用例数
        failed_cases: 失败用例数
        
    Returns:
        告警级别信息
    """
    # 根据成功率和失败用例数判断告警级别
    if success_rate >= 95:
        color = "green"
    elif success_rate >= 80:
        color = "blue" 
    elif success_rate >= 60:
        color = "yellow"
    elif success_rate >= 40:
        color = "orange"
    else:
        color = "red"
    
    # 如果失败用例数过多，提升告警级别
    if failed_cases >= 20:
        color = "red"
    elif failed_cases >= 10 and color not in ["red"]:
        color = "orange"
    elif failed_cases >= 5 and color not in ["red", "orange"]:
        color = "yellow"
    
    level_info = get_warning_level_info(color)
    level_info.update({
        "success_rate": success_rate,
        "total_cases": total_cases,
        "failed_cases": failed_cases,
        "alert_level": color
    })
    
    return level_info


def get_trend_indicator(current_rate: float, previous_rate: Optional[float] = None) -> str:
    """
    获取趋势指示器
    
    Args:
        current_rate: 当前成功率
        previous_rate: 上次成功率
        
    Returns:
        趋势指示器字符串
    """
    if previous_rate is None:
        return "➖"
    
    diff = current_rate - previous_rate
    if diff > 5:
        return "📈"  # 显著上升
    elif diff > 0:
        return "↗️"   # 轻微上升
    elif diff < -5:
        return "📉"  # 显著下降
    elif diff < 0:
        return "↘️"   # 轻微下降
    else:
        return "➖"  # 持平


def get_performance_indicator(avg_response_time: float) -> Dict[str, str]:
    """
    获取性能指示器
    
    Args:
        avg_response_time: 平均响应时间(毫秒)
        
    Returns:
        性能指示器信息
    """
    if avg_response_time <= 200:
        return {"icon": "🚀", "level": "优秀", "color": "green"}
    elif avg_response_time <= 500:
        return {"icon": "✅", "level": "良好", "color": "blue"}
    elif avg_response_time <= 1000:
        return {"icon": "⚠️", "level": "一般", "color": "yellow"}
    elif avg_response_time <= 2000:
        return {"icon": "🐌", "level": "较慢", "color": "orange"}
    else:
        return {"icon": "🔥", "level": "很慢", "color": "red"}


def format_alert_summary(alert_info: Dict[str, Any]) -> str:
    """
    格式化告警摘要信息
    
    Args:
        alert_info: 告警信息字典
        
    Returns:
        格式化的告警摘要
    """
    icon = alert_info.get("icon", "⚪")
    level = alert_info.get("level", "[未知]")
    success_rate = alert_info.get("success_rate", 0)
    description = alert_info.get("description", "")
    
    return f"{icon} {level} 成功率: {success_rate:.1f}% - {description}"


if __name__ == "__main__":
    # 测试示例
    test_cases = [
        (98.5, 100, 1),   # 优秀
        (85.0, 100, 15),  # 良好
        (70.0, 100, 30),  # 一般
        (45.0, 100, 55),  # 较差
        (20.0, 100, 80),  # 很差
    ]
    
    print("📊 告警级别测试:")
    print("=" * 60)
    
    for success_rate, total, failed in test_cases:
        alert_info = calculate_alert_level(success_rate, total, failed)
        summary = format_alert_summary(alert_info)
        print(f"成功率 {success_rate}%, 失败 {failed} 个 -> {summary}")
