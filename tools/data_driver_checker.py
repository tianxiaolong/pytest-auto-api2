#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

"""
数据驱动检查工具

专门用于检查YAML和Excel数据驱动功能的工具
"""

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class DataDriverChecker:
    """数据驱动检查器"""

    def __init__(self, project_root: str = None):
        """
        初始化检查器

        Args:
            project_root: 项目根目录，默认为当前目录
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.results = {}

    def _get_file_name_for_module(self, module_name: str) -> str:
        """根据模块名获取对应的文件名"""
        file_mapping = {
            'Login': 'login.yaml',
            'UserInfo': 'get_user_info.yaml',
            'Collect': 'collect_addtool.yaml'
        }
        return file_mapping.get(module_name, f"{module_name.lower()}.yaml")

    def check_all_drivers(self) -> Dict[str, Any]:
        """检查所有数据驱动"""
        print("🔍 数据驱动功能全面检查")
        print("=" * 50)

        self.results['yaml_driver'] = self.check_yaml_driver()
        self.results['excel_driver'] = self.check_excel_driver()
        self.results['switch_functionality'] = self.check_switch_functionality()

        self.generate_comparison_report()

        return self.results

    def check_yaml_driver(self) -> Dict[str, Any]:
        """检查YAML数据驱动"""
        print("\n📄 YAML数据驱动检查:")

        yaml_result = {
            'status': 'success',
            'modules': {},
            'total_cases': 0,
            'errors': []
        }

        try:
            from utils.read_files_tools.data_driver_control import switch_data_driver, get_test_data

            # 切换到YAML驱动
            switch_data_driver('yaml')

            # 检查各个模块
            modules_to_check = ['Login', 'UserInfo', 'Collect']

            for module_name in modules_to_check:
                try:
                    # 根据模块名指定对应的文件名
                    file_name = self._get_file_name_for_module(module_name)
                    data = get_test_data(module_name, file_name)
                    case_count = len(data)
                    yaml_result['modules'][module_name] = {
                        'status': 'success',
                        'case_count': case_count,
                        'sample_case': data[0] if data else None
                    }
                    yaml_result['total_cases'] += case_count
                    print(f"  ✅ {module_name}模块: {case_count} 个用例")

                except Exception as e:
                    yaml_result['modules'][module_name] = {
                        'status': 'error',
                        'error': str(e)
                    }
                    yaml_result['errors'].append(f"{module_name}: {str(e)}")
                    print(f"  ❌ {module_name}模块: 错误 - {str(e)[:50]}...")

            if yaml_result['errors']:
                yaml_result['status'] = 'warning'

        except Exception as e:
            yaml_result['status'] = 'error'
            yaml_result['errors'].append(f"YAML驱动初始化失败: {str(e)}")
            print(f"  ❌ YAML驱动初始化失败: {e}")

        return yaml_result

    def check_excel_driver(self) -> Dict[str, Any]:
        """检查Excel数据驱动"""
        print("\n📊 Excel数据驱动检查:")

        excel_result = {
            'status': 'success',
            'modules': {},
            'total_cases': 0,
            'errors': []
        }

        try:
            from utils.read_files_tools.data_driver_control import switch_data_driver, get_test_data

            # 切换到Excel驱动
            switch_data_driver('excel')

            # 检查各个模块
            modules_to_check = ['Login', 'UserInfo', 'Collect']

            for module_name in modules_to_check:
                try:
                    # 根据模块名指定对应的文件名
                    file_name = self._get_file_name_for_module(module_name)
                    data = get_test_data(module_name, file_name)
                    case_count = len(data)
                    excel_result['modules'][module_name] = {
                        'status': 'success',
                        'case_count': case_count,
                        'sample_case': data[0] if data else None
                    }
                    excel_result['total_cases'] += case_count
                    print(f"  ✅ {module_name}模块: {case_count} 个用例")

                except Exception as e:
                    excel_result['modules'][module_name] = {
                        'status': 'error',
                        'error': str(e)
                    }
                    excel_result['errors'].append(f"{module_name}: {str(e)}")
                    print(f"  ❌ {module_name}模块: 错误 - {str(e)[:50]}...")

            if excel_result['errors']:
                excel_result['status'] = 'warning'

        except Exception as e:
            excel_result['status'] = 'error'
            excel_result['errors'].append(f"Excel驱动初始化失败: {str(e)}")
            print(f"  ❌ Excel驱动初始化失败: {e}")

        return excel_result

    def check_switch_functionality(self) -> Dict[str, Any]:
        """检查切换功能"""
        print("\n🔄 数据驱动切换功能检查:")

        switch_result = {
            'status': 'success',
            'yaml_to_excel': False,
            'excel_to_yaml': False,
            'config_update': False,
            'errors': []
        }

        try:
            from utils.read_files_tools.data_driver_control import switch_data_driver
            import utils

            # 测试YAML到Excel切换
            try:
                # 切换到YAML
                switch_data_driver('yaml')
                current_type = getattr(utils.config, 'data_driver_type', None)

                if current_type == 'yaml':
                    # 切换到Excel
                    switch_data_driver('excel')
                    new_type = getattr(utils.config, 'data_driver_type', None)

                    if new_type == 'excel':
                        switch_result['yaml_to_excel'] = True
                        print("  ✅ YAML → Excel: 切换成功")
                    else:
                        print(f"  ❌ YAML → Excel: 配置未更新 (期望:excel, 实际:{new_type})")
                else:
                    print(f"  ❌ YAML → Excel: 初始切换失败 (期望:yaml, 实际:{current_type})")
            except Exception as e:
                switch_result['errors'].append(f"YAML→Excel切换失败: {str(e)}")
                print(f"  ❌ YAML → Excel: 切换失败 - {str(e)}")

            # 测试Excel到YAML切换
            try:
                # 切换到Excel
                switch_data_driver('excel')
                current_type = getattr(utils.config, 'data_driver_type', None)

                if current_type == 'excel':
                    # 切换到YAML
                    switch_data_driver('yaml')
                    new_type = getattr(utils.config, 'data_driver_type', None)

                    if new_type == 'yaml':
                        switch_result['excel_to_yaml'] = True
                        print("  ✅ Excel → YAML: 切换成功")
                    else:
                        print(f"  ❌ Excel → YAML: 配置未更新 (期望:yaml, 实际:{new_type})")
                else:
                    print(f"  ❌ Excel → YAML: 初始切换失败 (期望:excel, 实际:{current_type})")
            except Exception as e:
                switch_result['errors'].append(f"Excel→YAML切换失败: {str(e)}")
                print(f"  ❌ Excel → YAML: 切换失败 - {str(e)}")

            # 测试数据获取功能
            try:
                from utils.read_files_tools.data_driver_control import get_test_data

                # 测试YAML数据获取
                switch_data_driver('yaml')
                yaml_data = get_test_data('Login', 'login.yaml')
                yaml_works = len(yaml_data) > 0

                # 测试Excel数据获取
                switch_data_driver('excel')
                excel_data = get_test_data('Login', 'login.yaml')
                excel_works = len(excel_data) > 0

                if yaml_works and excel_works:
                    print("  ✅ 数据获取功能: 正常")
                    switch_result['data_access'] = True
                else:
                    print(f"  ⚠️ 数据获取功能: YAML({yaml_works}), Excel({excel_works})")
                    switch_result['data_access'] = False

            except Exception as e:
                switch_result['errors'].append(f"数据获取测试失败: {str(e)}")
                print(f"  ❌ 数据获取测试失败: {str(e)}")

            # 检查配置更新
            switch_result['config_update'] = switch_result['yaml_to_excel'] and switch_result['excel_to_yaml']

            if switch_result['errors']:
                switch_result['status'] = 'warning'

        except Exception as e:
            switch_result['status'] = 'error'
            switch_result['errors'].append(f"切换功能检查失败: {str(e)}")
            print(f"  ❌ 切换功能检查失败: {e}")

        return switch_result

    def generate_comparison_report(self):
        """生成对比报告"""
        print("\n" + "=" * 50)
        print("📊 数据驱动对比报告")
        print("=" * 50)

        yaml_result = self.results.get('yaml_driver', {})
        excel_result = self.results.get('excel_driver', {})
        switch_result = self.results.get('switch_functionality', {})

        # 用例数量对比
        print("\n📈 用例数量对比:")
        print("| 模块 | YAML用例数 | Excel用例数 | 状态 |")
        print("|------|------------|-------------|------|")

        modules = set()
        if 'modules' in yaml_result:
            modules.update(yaml_result['modules'].keys())
        if 'modules' in excel_result:
            modules.update(excel_result['modules'].keys())

        for module in sorted(modules):
            yaml_count = yaml_result.get('modules', {}).get(module, {}).get('case_count', 0)
            excel_count = excel_result.get('modules', {}).get(module, {}).get('case_count', 0)

            if yaml_count > 0 and excel_count > 0:
                status = "✅ 双驱动"
            elif yaml_count > 0:
                status = "⚠️ 仅YAML"
            elif excel_count > 0:
                status = "⚠️ 仅Excel"
            else:
                status = "❌ 无数据"

            print(f"| {module} | {yaml_count} | {excel_count} | {status} |")

        # 总体统计
        yaml_total = yaml_result.get('total_cases', 0)
        excel_total = excel_result.get('total_cases', 0)

        print(f"\n📊 总体统计:")
        print(f"  YAML总用例数: {yaml_total}")
        print(f"  Excel总用例数: {excel_total}")
        print(f"  切换功能: {'✅ 正常' if switch_result.get('config_update') else '❌ 异常'}")

        # 状态总结
        print(f"\n🎯 状态总结:")
        yaml_status = yaml_result.get('status', 'unknown')
        excel_status = excel_result.get('status', 'unknown')
        switch_status = switch_result.get('status', 'unknown')

        print(f"  YAML驱动: {self._get_status_icon(yaml_status)} {yaml_status}")
        print(f"  Excel驱动: {self._get_status_icon(excel_status)} {excel_status}")
        print(f"  切换功能: {self._get_status_icon(switch_status)} {switch_status}")

        # 保存报告
        self.save_report()
        print(f"\n✅ 数据驱动检查完成！报告已保存到: data_driver_report.json")

    def _get_status_icon(self, status: str) -> str:
        """获取状态图标"""
        status_icons = {
            'success': '🟢',
            'warning': '🟡',
            'error': '🔴',
            'unknown': '⚪'
        }
        return status_icons.get(status, '⚪')

    def save_report(self):
        """保存报告到文件"""
        report_file = self.project_root / 'data_driver_report.json'

        # 添加时间戳
        import datetime
        self.results['timestamp'] = datetime.datetime.now().isoformat()
        self.results['project_root'] = str(self.project_root)

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='数据驱动检查工具')
    parser.add_argument('--project-root', '-p',
                        help='项目根目录路径',
                        default='.')

    args = parser.parse_args()

    # 执行检查
    checker = DataDriverChecker(args.project_root)
    results = checker.check_all_drivers()

    return results


if __name__ == "__main__":
    main()
