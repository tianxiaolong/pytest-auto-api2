#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Success Rate Diagnostic Tool

This module provides success rate diagnostic functionality.
"""

"""
成功率计算诊断工具
分析和对比不同成功率计算方式的差异
@Author : txl
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.other_tools.allure_data.allure_report_data import AllureFileClean


def analyze_success_rate_calculation():
    """分析成功率计算方式的差异"""
    print("🔍 成功率计算方式诊断工具")
    print("=" * 80)
    
    try:
        # 获取两种计算方式的结果
        print("📊 正在分析Allure报告数据...")
        
        # 方式1：包含跳过用例（原有逻辑）
        metrics_with_skipped = AllureFileClean.get_case_count(include_skipped_in_success=True)
        
        # 方式2：不包含跳过用例（与Allure报告一致）
        metrics_without_skipped = AllureFileClean.get_case_count(include_skipped_in_success=False)
        
        print("\n📋 测试用例统计:")
        print(f"  总用例数: {metrics_with_skipped.total}")
        print(f"  通过用例: {metrics_with_skipped.passed}")
        print(f"  失败用例: {metrics_with_skipped.failed}")
        print(f"  异常用例: {metrics_with_skipped.broken}")
        print(f"  跳过用例: {metrics_with_skipped.skipped}")
        
        print("\n🔄 成功率计算对比:")
        print("-" * 60)
        
        # 方式1结果
        print(f"📈 方式1 (包含跳过用例):")
        print(f"   计算公式: (通过 + 跳过) / 总数 * 100")
        print(f"   计算过程: ({metrics_with_skipped.passed} + {metrics_with_skipped.skipped}) / {metrics_with_skipped.total} * 100")
        print(f"   成功率: {metrics_with_skipped.pass_rate}%")
        print(f"   成功用例数: {metrics_with_skipped.success_count}")
        
        print(f"\n📉 方式2 (仅通过用例，与Allure一致):")
        print(f"   计算公式: 通过 / 总数 * 100")
        print(f"   计算过程: {metrics_without_skipped.passed} / {metrics_without_skipped.total} * 100")
        print(f"   成功率: {metrics_without_skipped.pass_rate}%")
        print(f"   成功用例数: {metrics_without_skipped.success_count}")
        
        # 差异分析
        rate_diff = metrics_with_skipped.pass_rate - metrics_without_skipped.pass_rate
        count_diff = metrics_with_skipped.success_count - metrics_without_skipped.success_count
        
        print(f"\n🔍 差异分析:")
        print(f"   成功率差异: {rate_diff:+.1f}%")
        print(f"   成功用例数差异: {count_diff:+d} 个")
        
        if rate_diff > 0:
            print(f"   📊 通知系统成功率比Allure报告高 {rate_diff:.1f}%")
            print(f"   🔍 原因: 将 {metrics_with_skipped.skipped} 个跳过用例算作成功")
        elif rate_diff < 0:
            print(f"   📊 通知系统成功率比Allure报告低 {abs(rate_diff):.1f}%")
        else:
            print(f"   ✅ 两种计算方式结果一致")
        
        print(f"\n💡 建议:")
        if metrics_with_skipped.skipped > 0:
            print(f"   🎯 当前有 {metrics_with_skipped.skipped} 个跳过用例")
            print(f"   📋 建议在配置中设置 include_skipped_in_success: False")
            print(f"   🔄 这样通知系统的成功率将与Allure报告保持一致")
        else:
            print(f"   ✅ 当前没有跳过用例，两种计算方式结果相同")
        
        return True
        
    except FileNotFoundError as e:
        print(f"❌ 未找到Allure报告文件")
        print(f"   请先运行测试并生成Allure报告")
        print(f"   错误详情: {e}")
        return False
    except Exception as e:
        print(f"❌ 分析过程中发生错误: {e}")
        return False


def show_configuration_guide():
    """显示配置指南"""
    print("\n⚙️ 配置指南")
    print("=" * 80)
    
    print("📝 在 common/config.yaml 中配置成功率计算方式:")
    print()
    print("# 成功率计算方式配置")
    print("include_skipped_in_success: False  # 推荐：与Allure报告一致")
    print("# include_skipped_in_success: True   # 原有逻辑：包含跳过用例")
    print()
    
    print("🌍 或使用环境变量:")
    print("export INCLUDE_SKIPPED_IN_SUCCESS=False")
    print()
    
    print("📊 两种计算方式的区别:")
    print("┌─────────────────────┬──────────────────────┬────────────────────┐")
    print("│ 计算方式            │ 公式                 │ 适用场景           │")
    print("├─────────────────────┼──────────────────────┼────────────────────┤")
    print("│ False (推荐)        │ 通过 / 总数 * 100   │ 与Allure报告一致   │")
    print("│ True (原有逻辑)     │ (通过+跳过)/总数*100 │ 向后兼容           │")
    print("└─────────────────────┴──────────────────────┴────────────────────┘")


def main():
    """主函数"""
    print("🔍 pytest-auto-api2 成功率计算诊断工具")
    print("=" * 80)
    print("解决通知系统与Allure报告成功率不一致的问题")
    print("=" * 80)
    
    # 运行诊断
    success = analyze_success_rate_calculation()
    
    if success:
        show_configuration_guide()
        
        print("\n🎯 总结:")
        print("  1. 通知系统和Allure报告的成功率计算方式不同")
        print("  2. 通知系统默认将跳过用例算作成功，Allure报告不算")
        print("  3. 建议设置 include_skipped_in_success: False 保持一致")
        print("  4. 这样可以确保通知和报告显示相同的成功率")
        
        print("\n🚀 下一步:")
        print("  1. 修改 common/config.yaml 中的配置")
        print("  2. 重新运行测试")
        print("  3. 验证通知和报告的成功率是否一致")
    else:
        print("\n❌ 诊断失败，请检查:")
        print("  1. 是否已生成Allure报告")
        print("  2. 报告文件是否完整")
        print("  3. 路径配置是否正确")


if __name__ == "__main__":
    main()
