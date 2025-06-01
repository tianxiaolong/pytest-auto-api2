#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any
import importlib.util

"""
项目健康检查工具

提供全面的项目状态检查，包括：
- 核心模块检查
- 数据驱动功能检查
- 配置文件检查
- 依赖检查
- 测试执行检查
"""

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class ProjectHealthChecker:
    """项目健康检查器"""

    def __init__(self, project_root: str = None):
        """
        初始化检查器

        Args:
            project_root: 项目根目录，默认为当前目录
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.results = {}

    def check_all(self) -> Dict[str, Any]:
        """执行所有检查"""
        print("🔍 开始项目健康检查...")
        print("=" * 60)

        # 执行各项检查
        self.results['project_structure'] = self.check_project_structure()
        self.results['core_modules'] = self.check_core_modules()
        self.results['data_drivers'] = self.check_data_drivers()
        self.results['config_files'] = self.check_config_files()
        self.results['dependencies'] = self.check_dependencies()
        self.results['test_execution'] = self.check_test_execution()

        # 生成总结报告
        self.generate_summary_report()

        return self.results

    def check_project_structure(self) -> Dict[str, Any]:
        """检查项目结构"""
        print("\n📁 检查项目结构...")

        required_dirs = [
            'common', 'data', 'test_case', 'utils', 'logs', 'report'
        ]

        required_files = [
            'requirements.txt', 'pytest.ini', 'run.py', 'README.md'
        ]

        structure_result = {
            'status': 'success',
            'missing_dirs': [],
            'missing_files': [],
            'score': 0
        }

        # 检查目录
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                print(f"  ✅ {dir_name}/ - 存在")
            else:
                print(f"  ❌ {dir_name}/ - 缺失")
                structure_result['missing_dirs'].append(dir_name)

        # 检查文件
        for file_name in required_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                print(f"  ✅ {file_name} - 存在")
            else:
                print(f"  ❌ {file_name} - 缺失")
                structure_result['missing_files'].append(file_name)

        # 计算得分
        total_items = len(required_dirs) + len(required_files)
        missing_items = len(structure_result['missing_dirs']) + len(structure_result['missing_files'])
        structure_result['score'] = (total_items - missing_items) / total_items * 100

        if missing_items > 0:
            structure_result['status'] = 'warning'

        return structure_result

    def check_core_modules(self) -> Dict[str, Any]:
        """检查核心模块"""
        print("\n🔧 检查核心模块...")

        modules_to_check = [
            ('请求控制模块', 'utils.requests_tool.request_control', 'RequestControl'),
            ('断言控制模块', 'utils.assertion.assert_control', 'Assert'),
            ('缓存控制模块', 'utils.cache_process.cache_control', 'CacheHandler'),
            ('日志控制模块', 'utils.logging_tool.log_control', 'LogHandler'),
            ('通知模块-钉钉', 'utils.notify.ding_talk', 'DingTalkSendMsg'),
            ('通知模块-微信', 'utils.notify.wechat_send', 'WeChatSend'),
            ('数据库模块', 'utils.mysql_tool.mysql_control', 'MysqlDB'),
            ('时间工具模块', 'utils.times_tool.time_control', 'TimeControl'),
            ('Excel控制模块', 'utils.read_files_tools.excel_control', 'ExcelDataProcessor'),
            ('YAML控制模块', 'utils.read_files_tools.yaml_control', 'GetYamlData'),
            ('数据驱动控制', 'utils.read_files_tools.data_driver_control', 'switch_data_driver'),
        ]

        module_result = {
            'status': 'success',
            'working_modules': [],
            'failed_modules': [],
            'score': 0
        }

        for module_name, module_path, class_name in modules_to_check:
            try:
                module = importlib.import_module(module_path)
                getattr(module, class_name)
                print(f"  ✅ {module_name}: 正常")
                module_result['working_modules'].append(module_name)
            except Exception as e:
                print(f"  ❌ {module_name}: {str(e)[:50]}...")
                module_result['failed_modules'].append({
                    'name': module_name,
                    'error': str(e)
                })

        # 计算得分
        total_modules = len(modules_to_check)
        working_modules = len(module_result['working_modules'])
        module_result['score'] = working_modules / total_modules * 100

        if len(module_result['failed_modules']) > 0:
            module_result['status'] = 'warning'

        return module_result

    def check_data_drivers(self) -> Dict[str, Any]:
        """检查数据驱动功能"""
        print("\n📊 检查数据驱动功能...")

        driver_result = {
            'status': 'success',
            'yaml_driver': {'status': 'unknown', 'modules': {}},
            'excel_driver': {'status': 'unknown', 'modules': {}},
            'score': 0
        }

        try:
            # 检查YAML数据驱动
            from utils.read_files_tools.data_driver_control import switch_data_driver, get_test_data

            print("  📄 YAML数据驱动:")
            switch_data_driver('yaml')
            yaml_modules = {}

            for module_name in ['Login', 'UserInfo', 'Collect']:
                try:
                    data = get_test_data(module_name)
                    count = len(data)
                    yaml_modules[module_name] = count
                    print(f"    ✅ {module_name}模块: {count} 个用例")
                except Exception as e:
                    yaml_modules[module_name] = f"错误: {str(e)[:30]}..."
                    print(f"    ❌ {module_name}模块: 错误")

            driver_result['yaml_driver'] = {
                'status': 'success',
                'modules': yaml_modules
            }

            # 检查Excel数据驱动
            print("  📊 Excel数据驱动:")
            switch_data_driver('excel')
            excel_modules = {}

            for module_name in ['Login', 'UserInfo', 'Collect']:
                try:
                    data = get_test_data(module_name)
                    count = len(data)
                    excel_modules[module_name] = count
                    print(f"    ✅ {module_name}模块: {count} 个用例")
                except Exception as e:
                    excel_modules[module_name] = f"错误: {str(e)[:30]}..."
                    print(f"    ❌ {module_name}模块: 错误")

            driver_result['excel_driver'] = {
                'status': 'success',
                'modules': excel_modules
            }

            # 计算得分
            yaml_success = sum(1 for v in yaml_modules.values() if isinstance(v, int))
            excel_success = sum(1 for v in excel_modules.values() if isinstance(v, int))
            total_checks = len(yaml_modules) + len(excel_modules)
            driver_result['score'] = (yaml_success + excel_success) / total_checks * 100

        except Exception as e:
            print(f"  ❌ 数据驱动检查失败: {e}")
            driver_result['status'] = 'error'
            driver_result['error'] = str(e)
            driver_result['score'] = 0

        return driver_result

    def check_config_files(self) -> Dict[str, Any]:
        """检查配置文件"""
        print("\n⚙️ 检查配置文件...")

        config_result = {
            'status': 'success',
            'files': {},
            'score': 0
        }

        config_files = {
            'common/config.yaml': '主配置文件',
            'pytest.ini': 'pytest配置文件',
            'requirements.txt': '依赖配置文件'
        }

        working_files = 0

        for file_path, description in config_files.items():
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    # 检查文件是否可读
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    config_result['files'][file_path] = {
                        'status': 'success',
                        'size': len(content),
                        'lines': len(content.splitlines())
                    }
                    print(f"  ✅ {description}: 正常 ({len(content.splitlines())} 行)")
                    working_files += 1

                except Exception as e:
                    config_result['files'][file_path] = {
                        'status': 'error',
                        'error': str(e)
                    }
                    print(f"  ❌ {description}: 读取错误")
            else:
                config_result['files'][file_path] = {
                    'status': 'missing'
                }
                print(f"  ❌ {description}: 文件不存在")

        config_result['score'] = working_files / len(config_files) * 100

        if working_files < len(config_files):
            config_result['status'] = 'warning'

        return config_result

    def check_dependencies(self) -> Dict[str, Any]:
        """检查依赖"""
        print("\n📦 检查依赖...")

        dep_result = {
            'status': 'success',
            'requirements_file': False,
            'pip_check': False,
            'score': 0
        }

        # 检查requirements.txt
        req_file = self.project_root / 'requirements.txt'
        if req_file.exists():
            dep_result['requirements_file'] = True
            print("  ✅ requirements.txt: 存在")
        else:
            print("  ❌ requirements.txt: 不存在")

        # 检查pip依赖
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'check'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                dep_result['pip_check'] = True
                print("  ✅ pip依赖检查: 通过")
            else:
                print("  ⚠️ pip依赖检查: 有冲突")
                dep_result['pip_issues'] = result.stdout
        except Exception as e:
            print(f"  ❌ pip依赖检查: 失败 ({e})")

        # 计算得分
        checks = [dep_result['requirements_file'], dep_result['pip_check']]
        dep_result['score'] = sum(checks) / len(checks) * 100

        if not all(checks):
            dep_result['status'] = 'warning'

        return dep_result

    def check_test_execution(self) -> Dict[str, Any]:
        """检查测试执行"""
        print("\n🧪 检查测试执行...")

        test_result = {
            'status': 'success',
            'pytest_available': False,
            'test_discovery': False,
            'sample_test': False,
            'score': 0
        }

        try:
            # 检查pytest是否可用
            import pytest
            test_result['pytest_available'] = True
            print("  ✅ pytest: 可用")

            # 检查测试发现
            test_dir = self.project_root / 'test_case'
            if test_dir.exists():
                test_files = list(test_dir.rglob('test_*.py'))
                if test_files:
                    test_result['test_discovery'] = True
                    print(f"  ✅ 测试发现: 找到 {len(test_files)} 个测试文件")
                else:
                    print("  ❌ 测试发现: 未找到测试文件")
            else:
                print("  ❌ 测试目录: 不存在")

            # 尝试运行一个简单测试
            if test_result['test_discovery']:
                try:
                    result = subprocess.run(
                        [sys.executable, '-m', 'pytest', '--collect-only', '-q'],
                        capture_output=True,
                        text=True,
                        timeout=30,
                        cwd=self.project_root
                    )
                    if result.returncode == 0:
                        test_result['sample_test'] = True
                        print("  ✅ 测试收集: 成功")
                    else:
                        print("  ❌ 测试收集: 失败")
                except Exception as e:
                    print(f"  ❌ 测试收集: 异常 ({e})")

        except ImportError:
            print("  ❌ pytest: 未安装")
        except Exception as e:
            print(f"  ❌ 测试检查: 异常 ({e})")

        # 计算得分
        checks = [
            test_result['pytest_available'],
            test_result['test_discovery'],
            test_result['sample_test']
        ]
        test_result['score'] = sum(checks) / len(checks) * 100

        if not all(checks):
            test_result['status'] = 'warning'

        return test_result

    def generate_summary_report(self):
        """生成总结报告"""
        print("\n" + "=" * 60)
        print("📊 项目健康检查报告")
        print("=" * 60)

        # 计算总体得分
        scores = []
        for category, result in self.results.items():
            if isinstance(result, dict) and 'score' in result:
                scores.append(result['score'])

        overall_score = sum(scores) / len(scores) if scores else 0

        # 显示各项得分
        print(f"\n🎯 总体评分: {overall_score:.1f}/100")
        print("\n📋 详细得分:")

        score_mapping = {
            'project_structure': '项目结构',
            'core_modules': '核心模块',
            'data_drivers': '数据驱动',
            'config_files': '配置文件',
            'dependencies': '依赖管理',
            'test_execution': '测试执行'
        }

        for category, result in self.results.items():
            if isinstance(result, dict) and 'score' in result:
                name = score_mapping.get(category, category)
                score = result['score']
                status = result.get('status', 'unknown')

                if score >= 90:
                    icon = "🟢"
                elif score >= 70:
                    icon = "🟡"
                else:
                    icon = "🔴"

                print(f"  {icon} {name}: {score:.1f}% ({status})")

        # 生成建议
        print(f"\n💡 改进建议:")

        for category, result in self.results.items():
            if isinstance(result, dict):
                if result.get('status') in ['warning', 'error']:
                    name = score_mapping.get(category, category)
                    print(f"  ⚠️ {name}: 需要关注")

                    # 具体建议
                    if category == 'core_modules' and 'failed_modules' in result:
                        for failed in result['failed_modules']:
                            print(f"    - 修复模块: {failed['name']}")

                    elif category == 'project_structure':
                        if result.get('missing_dirs'):
                            print(f"    - 创建缺失目录: {', '.join(result['missing_dirs'])}")
                        if result.get('missing_files'):
                            print(f"    - 创建缺失文件: {', '.join(result['missing_files'])}")

        # 保存报告到文件
        self.save_report_to_file()

        print(f"\n✅ 检查完成！报告已保存到: project_health_report.json")

    def save_report_to_file(self):
        """保存报告到文件"""
        report_file = self.project_root / 'project_health_report.json'

        # 添加时间戳
        import datetime
        self.results['timestamp'] = datetime.datetime.now().isoformat()
        self.results['project_root'] = str(self.project_root)

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='项目健康检查工具')
    parser.add_argument('--project-root', '-p',
                        help='项目根目录路径',
                        default='.')
    parser.add_argument('--output', '-o',
                        help='输出报告文件路径',
                        default='project_health_report.json')

    args = parser.parse_args()

    # 执行检查
    checker = ProjectHealthChecker(args.project_root)
    results = checker.check_all()

    return results


if __name__ == "__main__":
    main()
