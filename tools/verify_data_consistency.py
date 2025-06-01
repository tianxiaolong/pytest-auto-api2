#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化的测试数据一致性验证工具

快速验证pytest收集的用例数量与Allure报告中的用例数量是否一致。
"""

import json
import subprocess
import sys
from pathlib import Path


def get_pytest_collection_count() -> int:
    """获取pytest收集的用例数量"""
    print("🔍 检查pytest用例收集...")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', '--collect-only', '-q'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            # 从输出中提取用例数量
            output_lines = result.stdout.splitlines()
            for line in output_lines:
                if "tests collected" in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part.isdigit() and i + 1 < len(parts) and parts[i + 1] == "tests":
                            return int(part)
            
            # 备用方法：计算测试用例行数
            test_count = 0
            for line in output_lines:
                if '::' in line and 'test_' in line:
                    test_count += 1
            return test_count
        else:
            print(f"❌ pytest收集失败: {result.stderr}")
            return -1
            
    except Exception as e:
        print(f"❌ pytest收集异常: {e}")
        return -1


def get_allure_report_count() -> int:
    """获取Allure报告中的用例数量"""
    print("📊 检查Allure报告统计...")
    
    summary_file = Path("report/html/widgets/summary.json")
    
    if not summary_file.exists():
        print(f"❌ Allure报告文件不存在: {summary_file}")
        return -1
    
    try:
        with open(summary_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        statistic = data.get('statistic', {})
        total_count = statistic.get('total', -1)
        
        print(f"📈 Allure报告统计:")
        print(f"   总计: {statistic.get('total', 0)}")
        print(f"   通过: {statistic.get('passed', 0)}")
        print(f"   失败: {statistic.get('failed', 0)}")
        print(f"   异常: {statistic.get('broken', 0)}")
        print(f"   跳过: {statistic.get('skipped', 0)}")
        
        return total_count
        
    except Exception as e:
        print(f"❌ 读取Allure报告失败: {e}")
        return -1


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🔍 测试数据一致性验证")
    print("=" * 60)
    
    # 1. 检查pytest收集
    pytest_count = get_pytest_collection_count()
    print(f"📋 pytest收集用例数: {pytest_count}")
    
    # 2. 检查Allure报告
    allure_count = get_allure_report_count()
    print(f"📊 Allure报告用例数: {allure_count}")
    
    # 3. 比较结果
    print(f"\n📈 一致性检查结果:")
    
    if pytest_count == -1 or allure_count == -1:
        print("❌ 无法获取完整的用例数量信息")
        return 1
    
    if pytest_count == allure_count:
        print(f"✅ 数据一致: {pytest_count} = {allure_count}")
        print("🎉 测试数据一致性验证通过！")
        return 0
    else:
        print(f"❌ 数据不一致: {pytest_count} ≠ {allure_count}")
        print(f"   差异: {abs(pytest_count - allure_count)} 个用例")
        print(f"\n💡 可能的原因:")
        print(f"   1. 测试文件中的数据驱动配置错误")
        print(f"   2. 重复的测试用例ID")
        print(f"   3. 测试用例在执行时被动态跳过")
        print(f"   4. Allure插件配置问题")
        print(f"\n🔧 建议的修复步骤:")
        print(f"   1. 检查每个测试文件的get_test_data()调用")
        print(f"   2. 确保每个测试文件使用对应的数据文件")
        print(f"   3. 验证没有重复的测试用例ID")
        return 1


if __name__ == "__main__":
    sys.exit(main())
