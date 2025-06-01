#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Notification Format Tester Module

This module provides notification format testing functionality.
"""

"""
通知格式测试工具
用于预览和对比原始格式与增强格式的通知效果
@Author : txl
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.other_tools.allure_data.allure_report_data import AllureFileClean
from utils.notify.enhanced_notification_formatter import format_simple_notification, format_alarm_notification
from utils.notify.alert_level_manager import calculate_alert_level, format_alert_summary


class MockTestMetrics:
    """模拟测试指标类"""
    
    def __init__(self, scenario: str = "normal"):
        """
        初始化模拟数据
        
        Args:
            scenario: 测试场景 (excellent/good/normal/poor/critical)
        """
        scenarios = {
            "excellent": {
                "total": 100, "passed": 98, "failed": 1, "broken": 0, "skipped": 1,
                "pass_rate": 98.0, "time": "120.5", "avg_response_time": 150
            },
            "good": {
                "total": 100, "passed": 85, "failed": 10, "broken": 3, "skipped": 2,
                "pass_rate": 85.0, "time": "180.3", "avg_response_time": 350
            },
            "normal": {
                "total": 100, "passed": 70, "failed": 25, "broken": 3, "skipped": 2,
                "pass_rate": 70.0, "time": "220.8", "avg_response_time": 650
            },
            "poor": {
                "total": 100, "passed": 45, "failed": 40, "broken": 10, "skipped": 5,
                "pass_rate": 45.0, "time": "300.2", "avg_response_time": 1200
            },
            "critical": {
                "total": 100, "passed": 20, "failed": 65, "broken": 15, "skipped": 0,
                "pass_rate": 20.0, "time": "450.7", "avg_response_time": 2500
            }
        }
        
        data = scenarios.get(scenario, scenarios["normal"])
        
        # 设置属性
        self.total = data["total"]
        self.passed = data["passed"] 
        self.failed = data["failed"]
        self.broken = data["broken"]
        self.skipped = data["skipped"]
        self.pass_rate = data["pass_rate"]
        self.time = data["time"]
        
        # 增强格式需要的额外属性
        self.case_count = self.total
        self.success_count = self.passed
        self.failed_count = self.failed + self.broken
        self.skipped_count = self.skipped
        self.success_rate = self.pass_rate
        self.avg_response_time = data["avg_response_time"]
        self.project_name = "pytest-auto-api2"
        self.tester_name = "txl"
        self.environment = "测试环境"


def preview_enhanced_format(scenario: str = "normal"):
    """预览增强格式通知"""
    print(f"\n🎨 增强格式通知预览 - {scenario.upper()}场景")
    print("=" * 80)
    
    # 创建模拟数据
    mock_metrics = MockTestMetrics(scenario)
    
    # 生成增强格式通知
    enhanced_content = format_simple_notification(mock_metrics)
    
    print(enhanced_content)
    print("\n" + "=" * 80)


def preview_legacy_format(scenario: str = "normal"):
    """预览原始格式通知"""
    print(f"\n📝 原始格式通知预览 - {scenario.upper()}场景")
    print("=" * 80)
    
    # 创建模拟数据
    mock_metrics = MockTestMetrics(scenario)
    
    # 模拟原始格式（企业微信）
    legacy_content = f"""【{mock_metrics.project_name}自动化通知】
>测试环境：<font color="info">TEST</font>
>测试负责人：@{mock_metrics.tester_name}
>
> **执行结果**
><font color="info">成  功  率  : {mock_metrics.pass_rate}%</font>
>用例  总数：<font color="info">{mock_metrics.total}</font>
>成功用例数：<font color="info">{mock_metrics.passed}</font>
>失败用例数：`{mock_metrics.failed}个`
>异常用例数：`{mock_metrics.broken}个`
>跳过用例数：<font color="warning">{mock_metrics.skipped}个</font>
>用例执行时长：<font color="warning">{mock_metrics.time} s</font>
>
>非相关负责人员可忽略此消息。
>📊 [测试报告链接1](http://localhost:9999/index.html)
>📊 [测试报告链接2](http://127.0.0.1:9999/index.html)
>
>💡 **报告访问说明**：
>- 如果链接1无法访问，可以尝试链接2或链接3
>- 或复制链接到浏览器中打开
>- 报告文件位置：./report/html/index.html"""
    
    print(legacy_content)
    print("\n" + "=" * 80)


def compare_formats(scenario: str = "normal"):
    """对比两种格式"""
    print(f"\n🔄 格式对比 - {scenario.upper()}场景")
    print("=" * 100)
    
    preview_legacy_format(scenario)
    preview_enhanced_format(scenario)
    
    # 显示告警级别分析
    mock_metrics = MockTestMetrics(scenario)
    alert_info = calculate_alert_level(
        mock_metrics.success_rate, 
        mock_metrics.total, 
        mock_metrics.failed_count
    )
    
    print(f"\n📊 告警级别分析:")
    print(f"   {format_alert_summary(alert_info)}")
    print("=" * 100)


def test_all_scenarios():
    """测试所有场景"""
    scenarios = ["excellent", "good", "normal", "poor", "critical"]
    
    print("🧪 通知格式全场景测试")
    print("=" * 120)
    
    for scenario in scenarios:
        compare_formats(scenario)
        input(f"\n按回车键继续查看下一个场景...")


def show_alert_level_demo():
    """展示告警级别演示"""
    print("\n🚨 告警级别演示")
    print("=" * 60)
    
    scenarios = {
        "excellent": "优秀场景",
        "good": "良好场景", 
        "normal": "一般场景",
        "poor": "较差场景",
        "critical": "严重场景"
    }
    
    for scenario, desc in scenarios.items():
        mock_metrics = MockTestMetrics(scenario)
        alert_info = calculate_alert_level(
            mock_metrics.success_rate,
            mock_metrics.total, 
            mock_metrics.failed_count
        )
        
        summary = format_alert_summary(alert_info)
        print(f"{desc:8} -> {summary}")
    
    print("=" * 60)


def main():
    """主函数"""
    print("🎨 通知格式测试工具")
    print("=" * 80)
    
    while True:
        print("\n请选择要执行的操作:")
        print("1. 📱 预览增强格式通知")
        print("2. 📝 预览原始格式通知") 
        print("3. 🔄 对比两种格式")
        print("4. 🧪 测试所有场景")
        print("5. 🚨 告警级别演示")
        print("6. 🎯 自定义场景测试")
        print("0. 退出")
        
        try:
            choice = input("\n请输入选择 (0-6): ").strip()
            
            if choice == '0':
                print("\n👋 再见！")
                break
            elif choice == '1':
                scenario = input("请输入场景 (excellent/good/normal/poor/critical) [默认:normal]: ").strip() or "normal"
                preview_enhanced_format(scenario)
            elif choice == '2':
                scenario = input("请输入场景 (excellent/good/normal/poor/critical) [默认:normal]: ").strip() or "normal"
                preview_legacy_format(scenario)
            elif choice == '3':
                scenario = input("请输入场景 (excellent/good/normal/poor/critical) [默认:normal]: ").strip() or "normal"
                compare_formats(scenario)
            elif choice == '4':
                test_all_scenarios()
            elif choice == '5':
                show_alert_level_demo()
            elif choice == '6':
                print("\n自定义场景测试:")
                total = int(input("总用例数: ") or "100")
                passed = int(input("成功用例数: ") or "70")
                failed = int(input("失败用例数: ") or "25")
                broken = int(input("异常用例数: ") or "3")
                skipped = int(input("跳过用例数: ") or "2")
                
                # 创建自定义场景
                custom_metrics = MockTestMetrics()
                custom_metrics.total = total
                custom_metrics.passed = passed
                custom_metrics.failed = failed
                custom_metrics.broken = broken
                custom_metrics.skipped = skipped
                custom_metrics.pass_rate = (passed / total * 100) if total > 0 else 0
                custom_metrics.success_rate = custom_metrics.pass_rate
                custom_metrics.failed_count = failed + broken
                
                enhanced_content = format_simple_notification(custom_metrics)
                print("\n🎨 自定义场景增强格式预览:")
                print("=" * 80)
                print(enhanced_content)
            else:
                print("\n❌ 无效选择，请重新输入")
                continue
                
            input("\n按回车键继续...")
            
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            input("按回车键继续...")


if __name__ == "__main__":
    main()
