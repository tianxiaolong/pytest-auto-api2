#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

"""
测试执行检查工具

用于检查测试用例的执行状态和结果
"""

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestExecutionChecker:
    """测试执行检查器"""

    def __init__(self, project_root: str = None):
        """
        初始化检查器

        Args:
            project_root: 项目根目录，默认为当前目录
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.results = {}

    def check_all_tests(self) -> Dict[str, Any]:
        """检查所有测试"""
        print("🧪 测试执行全面检查")
        print("=" * 50)

        self.results['test_discovery'] = self.check_test_discovery()
        self.results['test_collection'] = self.check_test_collection()
        self.results['sample_execution'] = self.check_sample_execution()
        self.results['yaml_tests'] = self.check_yaml_tests()
        self.results['excel_tests'] = self.check_excel_tests()

        self.generate_execution_report()

        return self.results

    def check_test_discovery(self) -> Dict[str, Any]:
        """检查测试发现"""
        print("\n🔍 测试发现检查:")

        discovery_result = {
            'status': 'success',
            'test_files': [],
            'total_files': 0,
            'modules': {}
        }

        test_dir = self.project_root / 'test_case'

        if not test_dir.exists():
            discovery_result['status'] = 'error'
            discovery_result['error'] = 'test_case目录不存在'
            print("  ❌ test_case目录不存在")
            return discovery_result

        # 查找测试文件
        test_files = list(test_dir.rglob('test_*.py'))
        discovery_result['test_files'] = [str(f.relative_to(self.project_root)) for f in test_files]
        discovery_result['total_files'] = len(test_files)

        # 按模块分组
        for test_file in test_files:
            module_name = test_file.parent.name
            if module_name not in discovery_result['modules']:
                discovery_result['modules'][module_name] = []
            discovery_result['modules'][module_name].append(test_file.name)

        print(f"  ✅ 发现 {len(test_files)} 个测试文件")
        for module, files in discovery_result['modules'].items():
            print(f"    📁 {module}: {len(files)} 个文件")

        return discovery_result

    def check_test_collection(self) -> Dict[str, Any]:
        """检查测试收集"""
        print("\n📋 测试收集检查:")

        collection_result = {
            'status': 'success',
            'total_tests': 0,
            'modules': {},
            'errors': []
        }

        try:
            # 运行pytest --collect-only
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', '--collect-only', '-q'],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=self.project_root
            )

            if result.returncode == 0:
                # 解析收集结果
                output_lines = result.stdout.splitlines()
                test_count = 0

                for line in output_lines:
                    if '::' in line and 'test_' in line:
                        test_count += 1
                        # 解析模块信息
                        parts = line.split('::')
                        if len(parts) >= 2:
                            module_path = parts[0]
                            module_name = Path(module_path).parent.name

                            if module_name not in collection_result['modules']:
                                collection_result['modules'][module_name] = 0
                            collection_result['modules'][module_name] += 1

                collection_result['total_tests'] = test_count
                print(f"  ✅ 收集到 {test_count} 个测试用例")

                for module, count in collection_result['modules'].items():
                    print(f"    📁 {module}: {count} 个用例")

            else:
                collection_result['status'] = 'error'
                collection_result['errors'].append(result.stderr)
                print(f"  ❌ 测试收集失败: {result.stderr[:100]}...")

        except subprocess.TimeoutExpired:
            collection_result['status'] = 'error'
            collection_result['errors'].append("测试收集超时")
            print("  ❌ 测试收集超时")
        except Exception as e:
            collection_result['status'] = 'error'
            collection_result['errors'].append(str(e))
            print(f"  ❌ 测试收集异常: {e}")

        return collection_result

    def check_sample_execution(self) -> Dict[str, Any]:
        """检查示例执行"""
        print("\n⚡ 示例执行检查:")

        execution_result = {
            'status': 'success',
            'login_test': {},
            'execution_time': 0,
            'errors': []
        }

        try:
            # 运行Login模块的一个测试
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', 'test_case/Login/', '-v', '--tb=short', '-x'],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.project_root
            )

            # 解析结果
            output = result.stdout + result.stderr

            # 提取统计信息
            stats_match = re.search(r'(\d+) passed.*in ([\d.]+)s', output)
            if stats_match:
                passed_count = int(stats_match.group(1))
                exec_time = float(stats_match.group(2))

                execution_result['login_test'] = {
                    'passed': passed_count,
                    'execution_time': exec_time,
                    'status': 'success' if result.returncode == 0 else 'failed'
                }
                execution_result['execution_time'] = exec_time

                print(f"  ✅ Login测试: {passed_count} 个通过，耗时 {exec_time}s")
            else:
                # 查找失败信息
                failed_match = re.search(r'(\d+) failed', output)
                if failed_match:
                    failed_count = int(failed_match.group(1))
                    execution_result['login_test'] = {
                        'failed': failed_count,
                        'status': 'failed'
                    }
                    execution_result['status'] = 'warning'
                    print(f"  ⚠️ Login测试: {failed_count} 个失败")
                else:
                    execution_result['status'] = 'error'
                    execution_result['errors'].append("无法解析测试结果")
                    print("  ❌ 无法解析测试结果")

        except subprocess.TimeoutExpired:
            execution_result['status'] = 'error'
            execution_result['errors'].append("测试执行超时")
            print("  ❌ 测试执行超时")
        except Exception as e:
            execution_result['status'] = 'error'
            execution_result['errors'].append(str(e))
            print(f"  ❌ 测试执行异常: {e}")

        return execution_result

    def check_yaml_tests(self) -> Dict[str, Any]:
        """检查YAML数据驱动测试"""
        print("\n📄 YAML数据驱动测试检查:")

        yaml_result = {
            'status': 'success',
            'driver_switch': False,
            'test_execution': False,
            'errors': []
        }

        try:
            # 切换到YAML驱动
            from utils.read_files_tools.data_driver_control import switch_data_driver
            switch_data_driver('yaml')
            yaml_result['driver_switch'] = True
            print("  ✅ 切换到YAML驱动成功")

            # 运行一个简单的测试收集
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', '--collect-only', 'test_case/Login/', '-q'],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.project_root
            )

            if result.returncode == 0:
                yaml_result['test_execution'] = True
                print("  ✅ YAML测试收集成功")
            else:
                yaml_result['errors'].append("YAML测试收集失败")
                print("  ❌ YAML测试收集失败")

        except Exception as e:
            yaml_result['status'] = 'error'
            yaml_result['errors'].append(str(e))
            print(f"  ❌ YAML测试检查异常: {e}")

        return yaml_result

    def check_excel_tests(self) -> Dict[str, Any]:
        """检查Excel数据驱动测试"""
        print("\n📊 Excel数据驱动测试检查:")

        excel_result = {
            'status': 'success',
            'driver_switch': False,
            'test_execution': False,
            'errors': []
        }

        try:
            # 切换到Excel驱动
            from utils.read_files_tools.data_driver_control import switch_data_driver
            switch_data_driver('excel')
            excel_result['driver_switch'] = True
            print("  ✅ 切换到Excel驱动成功")

            # 运行一个简单的测试收集
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', '--collect-only', 'test_case/Login/', '-q'],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.project_root
            )

            if result.returncode == 0:
                excel_result['test_execution'] = True
                print("  ✅ Excel测试收集成功")
            else:
                excel_result['errors'].append("Excel测试收集失败")
                print("  ❌ Excel测试收集失败")

        except Exception as e:
            excel_result['status'] = 'error'
            excel_result['errors'].append(str(e))
            print(f"  ❌ Excel测试检查异常: {e}")

        return excel_result

    def generate_execution_report(self):
        """生成执行报告"""
        print("\n" + "=" * 50)
        print("📊 测试执行检查报告")
        print("=" * 50)

        discovery = self.results.get('test_discovery', {})
        collection = self.results.get('test_collection', {})
        execution = self.results.get('sample_execution', {})
        yaml_tests = self.results.get('yaml_tests', {})
        excel_tests = self.results.get('excel_tests', {})

        # 测试发现统计
        print(f"\n🔍 测试发现:")
        print(f"  测试文件数: {discovery.get('total_files', 0)}")
        print(f"  测试模块数: {len(discovery.get('modules', {}))}")

        # 测试收集统计
        print(f"\n📋 测试收集:")
        print(f"  总用例数: {collection.get('total_tests', 0)}")
        collection_status = collection.get('status', 'unknown')
        print(f"  收集状态: {self._get_status_icon(collection_status)} {collection_status}")

        # 执行结果统计
        print(f"\n⚡ 执行结果:")
        login_test = execution.get('login_test', {})
        if 'passed' in login_test:
            print(f"  Login测试: ✅ {login_test['passed']} 个通过")
            print(f"  执行时间: {login_test.get('execution_time', 0):.2f}s")
        elif 'failed' in login_test:
            print(f"  Login测试: ❌ {login_test['failed']} 个失败")
        else:
            print(f"  Login测试: ⚪ 未执行")

        # 数据驱动测试状态
        print(f"\n📊 数据驱动测试:")
        yaml_status = yaml_tests.get('status', 'unknown')
        excel_status = excel_tests.get('status', 'unknown')

        print(f"  YAML驱动: {self._get_status_icon(yaml_status)} {yaml_status}")
        print(f"  Excel驱动: {self._get_status_icon(excel_status)} {excel_status}")

        # 模块详情
        if collection.get('modules'):
            print(f"\n📁 模块详情:")
            for module, count in collection['modules'].items():
                print(f"  {module}: {count} 个用例")

        # 问题汇总
        all_errors = []
        for category, result in self.results.items():
            if isinstance(result, dict) and result.get('errors'):
                all_errors.extend([f"{category}: {err}" for err in result['errors']])

        if all_errors:
            print(f"\n⚠️ 发现的问题:")
            for error in all_errors[:5]:  # 只显示前5个问题
                print(f"  - {error}")
            if len(all_errors) > 5:
                print(f"  ... 还有 {len(all_errors) - 5} 个问题")

        # 保存报告
        self.save_report()
        print(f"\n✅ 测试执行检查完成！报告已保存到: test_execution_report.json")

    def _get_status_icon(self, status: str) -> str:
        """获取状态图标"""
        status_icons = {
            'success': '🟢',
            'warning': '🟡',
            'error': '🔴',
            'failed': '🔴',
            'unknown': '⚪'
        }
        return status_icons.get(status, '⚪')

    def save_report(self):
        """保存报告到文件"""
        report_file = self.project_root / 'test_execution_report.json'

        # 添加时间戳
        import datetime
        self.results['timestamp'] = datetime.datetime.now().isoformat()
        self.results['project_root'] = str(self.project_root)

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='测试执行检查工具')
    parser.add_argument('--project-root', '-p',
                        help='项目根目录路径',
                        default='.')
    parser.add_argument('--module', '-m',
                        help='指定检查的模块',
                        choices=['Login', 'UserInfo', 'Collect'])

    args = parser.parse_args()

    # 执行检查
    checker = TestExecutionChecker(args.project_root)
    results = checker.check_all_tests()

    return results


if __name__ == "__main__":
    main()
