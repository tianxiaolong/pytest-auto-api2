#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path
from typing import Dict, Any

"""
项目检查工具管理器

统一管理所有检查工具，提供一键检查功能
"""

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 导入各个检查工具
try:
    from .project_health_checker import ProjectHealthChecker
    from .data_driver_checker import DataDriverChecker
    from .test_execution_checker import TestExecutionChecker
except ImportError:
    # 如果作为独立脚本运行
    sys.path.append(str(Path(__file__).parent))
    from project_health_checker import ProjectHealthChecker
    from data_driver_checker import DataDriverChecker
    from test_execution_checker import TestExecutionChecker


class ProjectCheckerManager:
    """项目检查工具管理器"""

    def __init__(self, project_root: str = None):
        """
        初始化管理器

        Args:
            project_root: 项目根目录，默认为当前目录
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.results = {}

    def run_all_checks(self) -> Dict[str, Any]:
        """运行所有检查"""
        print("🚀 开始项目全面检查...")
        print("=" * 60)

        # 1. 项目健康检查
        print("\n🏥 第一步：项目健康检查")
        print("-" * 40)
        health_checker = ProjectHealthChecker(self.project_root)
        self.results['health_check'] = health_checker.check_all()

        # 2. 数据驱动检查
        print("\n📊 第二步：数据驱动检查")
        print("-" * 40)
        driver_checker = DataDriverChecker(self.project_root)
        self.results['data_driver_check'] = driver_checker.check_all_drivers()

        # 3. 测试执行检查
        print("\n🧪 第三步：测试执行检查")
        print("-" * 40)
        execution_checker = TestExecutionChecker(self.project_root)
        self.results['test_execution_check'] = execution_checker.check_all_tests()

        # 生成综合报告
        self.generate_comprehensive_report()

        return self.results

    def run_quick_check(self) -> Dict[str, Any]:
        """运行快速检查（仅核心功能）"""
        print("⚡ 开始项目快速检查...")
        print("=" * 60)

        # 只检查核心模块和数据驱动
        health_checker = ProjectHealthChecker(self.project_root)
        self.results['core_modules'] = health_checker.check_core_modules()

        driver_checker = DataDriverChecker(self.project_root)
        self.results['data_drivers'] = driver_checker.check_yaml_driver()
        self.results['data_drivers'].update(driver_checker.check_excel_driver())

        self.generate_quick_report()

        return self.results

    def run_health_check_only(self) -> Dict[str, Any]:
        """仅运行健康检查"""
        print("🏥 项目健康检查...")
        health_checker = ProjectHealthChecker(self.project_root)
        self.results = health_checker.check_all()
        return self.results

    def run_data_driver_check_only(self) -> Dict[str, Any]:
        """仅运行数据驱动检查"""
        print("📊 数据驱动检查...")
        driver_checker = DataDriverChecker(self.project_root)
        self.results = driver_checker.check_all_drivers()
        return self.results

    def run_test_execution_check_only(self) -> Dict[str, Any]:
        """仅运行测试执行检查"""
        print("🧪 测试执行检查...")
        execution_checker = TestExecutionChecker(self.project_root)
        self.results = execution_checker.check_all_tests()
        return self.results

    def generate_comprehensive_report(self):
        """生成综合报告"""
        print("\n" + "=" * 60)
        print("📋 项目综合检查报告")
        print("=" * 60)

        # 计算总体得分
        all_scores = []

        # 健康检查得分
        health_results = self.results.get('health_check', {})
        for category, result in health_results.items():
            if isinstance(result, dict) and 'score' in result:
                all_scores.append(result['score'])

        # 数据驱动得分
        driver_results = self.results.get('data_driver_check', {})
        yaml_modules = driver_results.get('yaml_driver', {}).get('modules', {})
        excel_modules = driver_results.get('excel_driver', {}).get('modules', {})

        # 计算数据驱动得分
        yaml_success = sum(1 for m in yaml_modules.values() if isinstance(m, dict) and m.get('status') == 'success')
        excel_success = sum(1 for m in excel_modules.values() if isinstance(m, dict) and m.get('status') == 'success')
        total_modules = len(yaml_modules) + len(excel_modules)
        if total_modules > 0:
            driver_score = (yaml_success + excel_success) / total_modules * 100
            all_scores.append(driver_score)

        # 测试执行得分
        execution_results = self.results.get('test_execution_check', {})
        execution_checks = [
            execution_results.get('test_discovery', {}).get('total_files', 0) > 0,
            execution_results.get('test_collection', {}).get('status') == 'success',
            execution_results.get('yaml_tests', {}).get('status') == 'success',
            execution_results.get('excel_tests', {}).get('status') == 'success'
        ]
        execution_score = sum(execution_checks) / len(execution_checks) * 100
        all_scores.append(execution_score)

        # 总体得分
        overall_score = sum(all_scores) / len(all_scores) if all_scores else 0

        print(f"\n🎯 项目总体评分: {overall_score:.1f}/100")

        # 评级
        if overall_score >= 90:
            grade = "A+ (优秀)"
            icon = "🏆"
        elif overall_score >= 80:
            grade = "A (良好)"
            icon = "🥇"
        elif overall_score >= 70:
            grade = "B (一般)"
            icon = "🥈"
        elif overall_score >= 60:
            grade = "C (及格)"
            icon = "🥉"
        else:
            grade = "D (需改进)"
            icon = "⚠️"

        print(f"📊 项目评级: {icon} {grade}")

        # 分类得分
        print(f"\n📋 分类得分:")

        # 健康检查
        health_score = sum(s for s in all_scores[:6]) / 6 if len(all_scores) >= 6 else 0
        print(f"  🏥 项目健康: {health_score:.1f}%")

        # 数据驱动
        if total_modules > 0:
            print(f"  📊 数据驱动: {driver_score:.1f}%")

        # 测试执行
        print(f"  🧪 测试执行: {execution_score:.1f}%")

        # 关键统计
        print(f"\n📈 关键统计:")

        # 测试用例统计
        yaml_total = driver_results.get('yaml_driver', {}).get('total_cases', 0)
        excel_total = driver_results.get('excel_driver', {}).get('total_cases', 0)
        test_files = execution_results.get('test_discovery', {}).get('total_files', 0)

        print(f"  📄 YAML用例数: {yaml_total}")
        print(f"  📊 Excel用例数: {excel_total}")
        print(f"  📁 测试文件数: {test_files}")

        # 模块状态
        working_modules = len(health_results.get('core_modules', {}).get('working_modules', []))
        total_modules_check = len(health_results.get('core_modules', {}).get('working_modules', [])) + \
                              len(health_results.get('core_modules', {}).get('failed_modules', []))

        print(f"  🔧 正常模块: {working_modules}/{total_modules_check}")

        # 保存综合报告
        self.save_comprehensive_report()
        print(f"\n✅ 综合检查完成！报告已保存到: comprehensive_report.json")

    def generate_quick_report(self):
        """生成快速报告"""
        print("\n" + "=" * 40)
        print("⚡ 快速检查报告")
        print("=" * 40)

        # 核心模块状态
        core_modules = self.results.get('core_modules', {})
        working_count = len(core_modules.get('working_modules', []))
        failed_count = len(core_modules.get('failed_modules', []))
        total_count = working_count + failed_count

        print(f"\n🔧 核心模块: {working_count}/{total_count} 正常")

        # 数据驱动状态
        data_drivers = self.results.get('data_drivers', {})
        if data_drivers:
            # 检查YAML模块
            yaml_modules = data_drivers.get('modules', {})
            yaml_count = sum(1 for v in yaml_modules.values() if isinstance(v, dict) and v.get('case_count', 0) > 0)
            print(f"📄 YAML数据: {yaml_count} 个模块正常")

            # 检查Excel模块（如果有的话）
            if 'excel_modules' in data_drivers:
                excel_modules = data_drivers.get('excel_modules', {})
                excel_count = sum(
                    1 for v in excel_modules.values() if isinstance(v, dict) and v.get('case_count', 0) > 0)
                print(f"📊 Excel数据: {excel_count} 个模块正常")

        print(f"\n✅ 快速检查完成！")

    def save_comprehensive_report(self):
        """保存综合报告"""
        report_file = self.project_root / 'comprehensive_report.json'

        # 添加元数据
        import datetime
        report_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'check_type': 'comprehensive',
            'results': self.results
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
