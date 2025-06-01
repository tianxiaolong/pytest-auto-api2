#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试数据一致性检查工具

用于检查pytest收集的用例数量与Allure报告中的用例数量是否一致，
确保测试数据驱动配置正确。
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any


class TestDataConsistencyChecker:
    """测试数据一致性检查器"""
    
    def __init__(self):
        """初始化检查器"""
        self.project_root = Path(__file__).parent.parent
        self.report_path = self.project_root / "report"
        
    def get_pytest_collection_count(self) -> int:
        """获取pytest收集的用例数量"""
        print("🔍 检查pytest用例收集...")
        
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', '--collect-only', '-q'],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                # 从输出中提取用例数量
                output_lines = result.stdout.splitlines()
                for line in output_lines:
                    if "tests collected" in line:
                        # 提取数字，例如 "15 tests collected in 1.01s"
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part.isdigit() and i + 1 < len(parts) and parts[i + 1] == "tests":
                                return int(part)
                
                # 如果没有找到标准格式，尝试计算测试用例行数
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
    
    def run_tests_and_generate_report(self) -> bool:
        """运行测试并生成Allure报告"""
        print("🧪 运行测试并生成报告...")
        
        try:
            # 运行测试
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', 'test_case/', 
                 '--alluredir=./report/tmp', '--clean-alluredir', '-q'],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.project_root
            )
            
            if result.returncode not in [0, 1]:  # 0=全部通过, 1=有失败但正常
                print(f"❌ 测试执行异常: {result.stderr}")
                return False
            
            # 生成Allure报告
            result = subprocess.run(
                ['allure', 'generate', './report/tmp', '-o', './report/html', '--clean'],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=self.project_root
            )
            
            if result.returncode != 0:
                print(f"❌ Allure报告生成失败: {result.stderr}")
                return False
                
            print("✅ 测试执行和报告生成完成")
            return True
            
        except Exception as e:
            print(f"❌ 测试执行异常: {e}")
            return False
    
    def get_allure_report_count(self) -> int:
        """获取Allure报告中的用例数量"""
        print("📊 检查Allure报告统计...")
        
        summary_file = self.report_path / "html" / "widgets" / "summary.json"
        
        if not summary_file.exists():
            print(f"❌ Allure报告文件不存在: {summary_file}")
            return -1
        
        try:
            with open(summary_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            total_count = data.get('statistic', {}).get('total', -1)
            print(f"📈 Allure报告统计: {data.get('statistic', {})}")
            return total_count
            
        except Exception as e:
            print(f"❌ 读取Allure报告失败: {e}")
            return -1
    
    def check_consistency(self) -> Dict[str, Any]:
        """检查数据一致性"""
        print("\n" + "=" * 60)
        print("🔍 测试数据一致性检查")
        print("=" * 60)
        
        # 1. 检查pytest收集
        pytest_count = self.get_pytest_collection_count()
        print(f"📋 pytest收集用例数: {pytest_count}")
        
        # 2. 运行测试并生成报告
        if not self.run_tests_and_generate_report():
            return {
                'status': 'error',
                'message': '测试执行或报告生成失败'
            }
        
        # 3. 检查Allure报告
        allure_count = self.get_allure_report_count()
        print(f"📊 Allure报告用例数: {allure_count}")
        
        # 4. 比较结果
        if pytest_count == -1 or allure_count == -1:
            return {
                'status': 'error',
                'message': '无法获取用例数量'
            }
        
        is_consistent = pytest_count == allure_count
        
        result = {
            'status': 'success' if is_consistent else 'inconsistent',
            'pytest_count': pytest_count,
            'allure_count': allure_count,
            'is_consistent': is_consistent,
            'difference': abs(pytest_count - allure_count)
        }
        
        # 5. 输出结果
        print(f"\n📈 一致性检查结果:")
        if is_consistent:
            print(f"✅ 数据一致: {pytest_count} = {allure_count}")
        else:
            print(f"❌ 数据不一致: {pytest_count} ≠ {allure_count}")
            print(f"   差异: {result['difference']} 个用例")
            print(f"\n💡 可能的原因:")
            print(f"   1. 测试文件中的数据驱动配置错误")
            print(f"   2. 重复的测试用例ID")
            print(f"   3. 测试用例在执行时被动态跳过")
            print(f"   4. Allure插件配置问题")
        
        return result
    
    def generate_report(self, result: Dict[str, Any]):
        """生成检查报告"""
        report_file = self.project_root / "test_data_consistency_report.json"
        
        report_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'check_result': result,
            'recommendations': []
        }
        
        if not result.get('is_consistent', False):
            report_data['recommendations'] = [
                "检查测试文件中的get_test_data()调用是否指定了正确的文件名",
                "确认没有重复的测试用例ID",
                "验证Allure插件配置是否正确",
                "检查是否有测试用例在执行时被意外跳过"
            ]
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 检查报告已保存: {report_file}")


def main():
    """主函数"""
    checker = TestDataConsistencyChecker()
    result = checker.check_consistency()
    checker.generate_report(result)
    
    # 返回适当的退出码
    if result['status'] == 'success' and result.get('is_consistent', False):
        print("\n🎉 测试数据一致性检查通过！")
        return 0
    else:
        print("\n⚠️ 测试数据一致性检查失败！")
        return 1


if __name__ == "__main__":
    sys.exit(main())
