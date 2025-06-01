#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Enhanced Notification Formatter Module

This module provides enhanced notification formatting functionality.
"""

"""
增强通知格式化模块
将测试信息格式化为美观的企业微信通知
@Author : txl
"""

import datetime
from typing import Dict, Any, List, Optional
from utils.notify.alert_level_manager import calculate_alert_level, get_trend_indicator, get_performance_indicator
from utils.other_tools.get_local_ip import get_host_ip


def format_alarm_notification(alarm_data: Dict[str, Any]) -> str:
    """
    将预警信息格式化为美观的企业微信通知

    Args:
        alarm_data: 包含测试结果的告警数据

    Returns:
        格式化后的markdown通知内容
    """
    # 提取日期和时间
    alarm_date = alarm_data.get('alarmDate', '')
    alarm_time = alarm_data.get('alarmTime', '')

    if alarm_date:
        try:
            # 解析日期时间
            if alarm_time:
                dt = datetime.datetime.strptime(f"{alarm_date} {alarm_time}", '%Y-%m-%d %H:%M:%S')
            else:
                dt = datetime.datetime.strptime(alarm_date, '%Y-%m-%d')
            alarm_time = dt.strftime('%H:%M:%S')
            alarm_date = dt.strftime('%Y年%m月%d日')
        except ValueError:
            # 如果解析失败，使用当前时间
            now = datetime.datetime.now()
            alarm_date = now.strftime('%Y年%m月%d日')
            alarm_time = now.strftime('%H:%M:%S')
    else:
        # 使用当前时间
        now = datetime.datetime.now()
        alarm_date = now.strftime('%Y年%m月%d日')
        alarm_time = now.strftime('%H:%M:%S')

    # 计算告警级别
    success_rate = alarm_data.get('success_rate', 0)
    total_cases = alarm_data.get('total_cases', 0)
    failed_cases = alarm_data.get('failed_cases', 0)

    alert_info = calculate_alert_level(success_rate, total_cases, failed_cases)

    # 获取性能指标
    avg_response_time = alarm_data.get('avg_response_time', 0)
    perf_info = get_performance_indicator(avg_response_time)

    # 获取趋势指标
    previous_rate = alarm_data.get('previous_success_rate')
    trend = get_trend_indicator(success_rate, previous_rate)

    # 构建通知内容
    notification = f"""# 🔔 接口自动化测试告警通知

## {alert_info['icon']} 告警级别: {alert_info['level']}

**⏰ 告警时间:** {alarm_date} {alarm_time}
**🎯 项目名称:** {alarm_data.get('project_name', '未知项目')}
**👤 测试人员:** {alarm_data.get('tester_name', '未知')}
**🌍 测试环境:** {alarm_data.get('environment', '未知环境')}

---

## 📊 测试结果概览

| 指标 | 数值 | 状态 |
|------|------|------|
| **总用例数** | {total_cases} | 📝 |
| **成功用例** | {alarm_data.get('success_cases', 0)} | ✅ |
| **失败用例** | {failed_cases} | ❌ |
| **跳过用例** | {alarm_data.get('skipped_cases', 0)} | ⏭️ |
| **成功率** | {success_rate:.1f}% | {trend} |

## ⚡ 性能指标

**{perf_info['icon']} 平均响应时间:** {avg_response_time:.0f}ms ({perf_info['level']})

## 🔍 详细分析

**📈 趋势分析:** {_get_trend_analysis(success_rate, previous_rate)}

**⚠️ 风险评估:** {alert_info['description']}

**🎯 建议措施:** {_get_suggestions(alert_info, failed_cases)}

---

## 📋 报告链接

{_format_report_links(alarm_data.get('timestamp'))}

---

> 📞 如有疑问，请联系测试团队
> ⏰ 通知时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

    return notification


def _get_trend_analysis(current_rate: float, previous_rate: Optional[float]) -> str:
    """获取趋势分析文本"""
    if previous_rate is None:
        return "首次执行，无历史数据对比"

    diff = current_rate - previous_rate
    if diff > 5:
        return f"成功率较上次提升 {diff:.1f}%，测试质量显著改善 📈"
    elif diff > 0:
        return f"成功率较上次提升 {diff:.1f}%，测试质量有所改善 ↗️"
    elif diff < -5:
        return f"成功率较上次下降 {abs(diff):.1f}%，需要重点关注 📉"
    elif diff < 0:
        return f"成功率较上次下降 {abs(diff):.1f}%，建议排查原因 ↘️"
    else:
        return "成功率与上次持平，保持稳定 ➖"


def _get_suggestions(alert_info: Dict[str, Any], failed_cases: int) -> str:
    """获取建议措施"""
    alert_level = alert_info.get('alert_level', 'green')

    suggestions = {
        'red': f"🚨 立即排查 {failed_cases} 个失败用例，优先修复核心功能问题",
        'orange': f"⚠️ 尽快处理 {failed_cases} 个失败用例，检查环境和数据配置",
        'yellow': f"🔍 关注 {failed_cases} 个失败用例，分析失败原因并优化",
        'blue': f"💡 少量失败用例，建议定期回归测试保持质量",
        'green': "🎉 测试全部通过，继续保持高质量标准"
    }

    return suggestions.get(alert_level, "建议联系测试团队进行详细分析")


def _format_report_links(timestamp: str = None) -> str:
    """
    格式化报告链接

    Args:
        timestamp: 时间戳，用于生成带时间戳的报告链接
    """
    local_ip = get_host_ip()

    # 基础报告链接
    report_links = f"""**🌐 Allure报告:**
- [本地访问](http://localhost:9999/index.html)
- [局域网访问](http://{local_ip}:9999/index.html)"""

    # 如果有时间戳，添加带时间戳的报告链接
    if timestamp:
        report_links += f"""
- [⏰ 带时间戳报告](./report/html_{timestamp}/index.html)"""

    report_links += f"""

**📋 详细报告:** 请查看Allure报告获取完整的测试执行详情"""

    return report_links


def format_simple_notification(test_metrics: Any) -> str:
    """
    格式化简单通知（兼容现有接口）

    Args:
        test_metrics: 测试指标对象

    Returns:
        格式化的通知内容
    """
    # 从test_metrics提取数据，兼容不同的属性名
    total_cases = getattr(test_metrics, 'case_count', None) or getattr(test_metrics, 'total', 0)
    success_cases = getattr(test_metrics, 'success_count', None) or getattr(test_metrics, 'passed', 0)
    failed_cases = getattr(test_metrics, 'failed_count', None) or (getattr(test_metrics, 'failed', 0) + getattr(test_metrics, 'broken', 0))
    skipped_cases = getattr(test_metrics, 'skipped_count', None) or getattr(test_metrics, 'skipped', 0)
    success_rate = getattr(test_metrics, 'success_rate', None) or getattr(test_metrics, 'pass_rate', 0)

    # 导入配置
    try:
        from utils import config
        project_name = config.project_name
        tester_name = config.tester_name
        environment = getattr(config, 'env', '测试环境')
    except:
        project_name = getattr(test_metrics, 'project_name', '接口自动化测试')
        tester_name = getattr(test_metrics, 'tester_name', 'txl')
        environment = getattr(test_metrics, 'environment', '测试环境')

    # 获取历史数据进行趋势分析
    previous_success_rate = None
    try:
        from utils.notify.history_data_manager import get_history_manager

        # 获取历史数据管理器
        history_manager = get_history_manager(project_name)

        # 获取上次成功率
        previous_success_rate = history_manager.get_previous_success_rate()

        # 保存当前测试结果到历史记录
        history_manager.save_test_result(test_metrics)

        print(f"📊 历史数据处理:")
        print(f"   当前成功率: {success_rate}%")
        print(f"   上次成功率: {previous_success_rate}%" if previous_success_rate else "   上次成功率: 无历史数据")

    except Exception as e:
        print(f"⚠️ 历史数据处理失败: {e}")
        import traceback
        print(f"   详细错误: {traceback.format_exc()}")

    alarm_data = {
        'project_name': project_name,
        'tester_name': tester_name,
        'environment': environment,
        'total_cases': total_cases,
        'success_cases': success_cases,
        'failed_cases': failed_cases,
        'skipped_cases': skipped_cases,
        'success_rate': success_rate,
        'previous_success_rate': previous_success_rate,  # 添加历史成功率
        'avg_response_time': getattr(test_metrics, 'avg_response_time', 500),
        'timestamp': getattr(test_metrics, 'timestamp', None),  # 添加时间戳
    }

    return format_alarm_notification(alarm_data)


if __name__ == "__main__":
    # 测试示例
    test_alarm_data = {
        'alarmDate': '2025-01-15',
        'alarmTime': '14:30:25',
        'project_name': 'pytest-auto-api2',
        'tester_name': 'txl',
        'environment': '测试环境',
        'total_cases': 100,
        'success_cases': 85,
        'failed_cases': 15,
        'skipped_cases': 0,
        'success_rate': 85.0,
        'previous_success_rate': 90.0,
        'avg_response_time': 350
    }

    notification = format_alarm_notification(test_alarm_data)
    print("📱 企业微信通知预览:")
    print("=" * 80)
    print(notification)
