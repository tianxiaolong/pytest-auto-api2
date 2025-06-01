#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据驱动标准化工具

检查并修复项目中所有的数据驱动配置，确保：
1. 统一使用新的get_test_data()接口
2. 移除旧的硬编码case_id方式
3. 确保所有测试文件都指定具体的数据文件名
4. 检查自动生成的代码是否符合标准
"""

import re
import ast
from pathlib import Path
from typing import Dict, List, Any, Tuple


class DataDriverStandardizer:
    """数据驱动标准化器"""

    def __init__(self):
        """初始化标准化器"""
        self.project_root = Path(__file__).parent.parent
        self.test_case_dir = self.project_root / "test_case"

        self.issues_found = []
        self.fixes_applied = []

    def find_all_python_files(self) -> List[Path]:
        """查找所有Python文件"""
        python_files = []

        # 测试文件
        for test_file in self.test_case_dir.rglob("*.py"):
            if "__pycache__" not in str(test_file):
                python_files.append(test_file)

        # 其他可能包含数据驱动代码的文件
        for py_file in self.project_root.rglob("*.py"):
            if (
                "__pycache__" not in str(py_file) and
                "venv" not in str(py_file) and
                ".git" not in str(py_file) and
                py_file not in python_files
            ):
                # 只检查可能包含测试相关代码的文件
                if any(keyword in py_file.name.lower() for keyword in
                       ['test', 'case', 'data', 'driver']):
                    python_files.append(py_file)

        return python_files

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """分析单个文件的数据驱动配置"""
        result = {
            'file': str(file_path.relative_to(self.project_root)),
            'issues': [],
            'old_patterns': [],
            'new_patterns': [],
            'needs_fix': False,
            'content': ''
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                result['content'] = content

            # 检查旧的数据获取方式
            self._check_old_patterns(content, result)

            # 检查新的数据获取方式
            self._check_new_patterns(content, result)

            # 检查是否需要修复
            if result['old_patterns'] or any('未指定文件名' in issue for issue in result['issues']):
                result['needs_fix'] = True

        except Exception as e:
            result['issues'].append(f"文件读取失败: {e}")

        return result

    def _check_old_patterns(self, content: str, result: Dict[str, Any]):
        """检查旧的数据获取模式"""

        # 1. 检查硬编码的case_id列表
        case_id_pattern = r"case_id\s*=\s*\[([^\]]+)\]"
        matches = re.findall(case_id_pattern, content)
        for match in matches:
            result['old_patterns'].append({
                'type': 'hardcoded_case_id',
                'pattern': f"case_id = [{match}]",
                'line': self._find_line_number(content, f"case_id = [{match}]")
            })
            result['issues'].append("发现硬编码的case_id列表，建议使用get_test_data()")

        # 2. 检查GetTestCase.case_data()调用
        get_test_case_pattern = r"GetTestCase\.case_data\([^)]+\)"
        matches = re.findall(get_test_case_pattern, content)
        for match in matches:
            result['old_patterns'].append({
                'type': 'get_test_case',
                'pattern': match,
                'line': self._find_line_number(content, match)
            })
            result['issues'].append("发现旧的GetTestCase.case_data()调用，建议使用get_test_data()")

        # 3. 检查旧的导入
        # 旧的导入（这些是检测模式，不是实际导入）
        old_imports = [
            "from utils.read_files_tools.get_yaml_data_analysis import GetTestCase",
            "from utils.read_files_tools.get_yaml_data_analysis import CaseData"
        ]
        for old_import in old_imports:
            if old_import in content:
                result['old_patterns'].append({
                    'type': 'old_import',
                    'pattern': old_import,
                    'line': self._find_line_number(content, old_import)
                })
                result['issues'].append(f"发现旧的导入: {old_import}")

    def _check_new_patterns(self, content: str, result: Dict[str, Any]):
        """检查新的数据获取模式"""

        # 检查get_test_data调用
        get_test_data_pattern = r'get_test_data\s*\(\s*["\']([^"\']+)["\'](?:\s*,\s*["\']([^"\']*)["\'])?\s*\)'
        matches = re.findall(get_test_data_pattern, content)

        for match in matches:
            module_name = match[0]
            file_name = match[1] if len(match) > 1 and match[1] else None

            pattern_info = {
                'type': 'get_test_data',
                'module': module_name,
                'file_name': file_name,
                'has_file_name': file_name is not None and file_name != '',
                'line': self._find_line_number(content, f"get_test_data('{module_name}'")
            }

            result['new_patterns'].append(pattern_info)

            if not pattern_info['has_file_name']:
                result['issues'].append(f"get_test_data('{module_name}')未指定文件名")

    def _find_line_number(self, content: str, pattern: str) -> int:
        """查找模式在文件中的行号"""
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if pattern in line:
                return i
        return 0

    def generate_fix_suggestions(self, analysis_result: Dict[str, Any]) -> List[str]:
        """生成修复建议"""
        suggestions = []

        # 针对旧模式的修复建议
        for old_pattern in analysis_result['old_patterns']:
            if old_pattern['type'] == 'hardcoded_case_id':
                suggestions.append(
                    f"行 {old_pattern['line']}: 将硬编码的case_id替换为get_test_data()调用"
                )
            elif old_pattern['type'] == 'get_test_case':
                suggestions.append(
                    f"行 {old_pattern['line']}: 将GetTestCase.case_data()替换为get_test_data()"
                )
            elif old_pattern['type'] == 'old_import':
                suggestions.append(
                    f"行 {old_pattern['line']}: 移除旧的导入，添加新的导入"
                )

        # 针对新模式的修复建议
        for new_pattern in analysis_result['new_patterns']:
            if not new_pattern['has_file_name']:
                # 根据文件路径推断应该使用的文件名
                file_path = analysis_result['file']
                if 'test_case' in file_path:
                    module = new_pattern['module']
                    suggested_file = self._suggest_file_name(file_path, module)
                    suggestions.append(
                        f"行 {new_pattern['line']}: 为get_test_data('{module}')指定文件名: '{suggested_file}'"
                    )

        return suggestions

    def _suggest_file_name(self, file_path: str, module: str) -> str:
        """根据文件路径和模块名推断数据文件名"""
        file_name = Path(file_path).stem

        # 移除test_前缀
        if file_name.startswith('test_'):
            base_name = file_name[5:]
        else:
            base_name = file_name

        # 根据模块和文件名推断
        if module.lower() == 'login':
            return 'login.yaml'
        elif module.lower() == 'userinfo':
            return 'get_user_info.yaml'
        elif module.lower() == 'collect':
            if 'addtool' in base_name:
                return 'collect_addtool.yaml'
            elif 'delete' in base_name:
                return 'collect_delete_tool.yaml'
            elif 'update' in base_name:
                return 'collect_update_tool.yaml'
            elif 'list' in base_name:
                return 'collect_tool_list.yaml'
            else:
                return 'collect_addtool.yaml'  # 默认

        return f"{base_name}.yaml"

    def run_analysis(self) -> Dict[str, Any]:
        """运行全面分析"""
        print("🔍 开始数据驱动标准化分析...")

        python_files = self.find_all_python_files()
        results = []

        print(f"📁 找到 {len(python_files)} 个Python文件")

        for py_file in python_files:
            # 跳过分析工具本身，避免检测到工具中的示例模式
            if py_file.name == 'data_driver_standardizer.py':
                continue

            print(f"  📄 分析: {py_file.relative_to(self.project_root)}")
            result = self.analyze_file(py_file)
            if result['issues'] or result['old_patterns']:
                results.append(result)

        # 生成汇总报告
        summary = self._generate_summary(results)

        return {
            'files_analyzed': len(python_files),
            'files_with_issues': len(results),
            'detailed_results': results,
            'summary': summary
        }

    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成汇总信息"""
        summary = {
            'total_issues': 0,
            'old_pattern_count': 0,
            'missing_file_name_count': 0,
            'files_need_fix': 0,
            'issue_types': {}
        }

        for result in results:
            summary['total_issues'] += len(result['issues'])
            summary['old_pattern_count'] += len(result['old_patterns'])

            if result['needs_fix']:
                summary['files_need_fix'] += 1

            # 统计问题类型
            for issue in result['issues']:
                if '硬编码' in issue:
                    summary['issue_types']['hardcoded_case_id'] = summary['issue_types'].get('hardcoded_case_id', 0) + 1
                elif 'GetTestCase' in issue:
                    summary['issue_types']['old_get_test_case'] = summary['issue_types'].get('old_get_test_case', 0) + 1
                elif '未指定文件名' in issue:
                    summary['issue_types']['missing_file_name'] = summary['issue_types'].get('missing_file_name', 0) + 1
                    summary['missing_file_name_count'] += 1

        return summary

    def print_detailed_report(self, analysis_result: Dict[str, Any]):
        """打印详细报告"""
        print("\n" + "=" * 80)
        print("📊 数据驱动标准化分析报告")
        print("=" * 80)

        summary = analysis_result['summary']

        # 总体统计
        print(f"\n📈 总体统计:")
        print(f"  分析文件数: {analysis_result['files_analyzed']}")
        print(f"  有问题的文件: {analysis_result['files_with_issues']}")
        print(f"  需要修复的文件: {summary['files_need_fix']}")
        print(f"  发现问题总数: {summary['total_issues']}")

        # 问题类型统计
        if summary['issue_types']:
            print(f"\n📋 问题类型统计:")
            for issue_type, count in summary['issue_types'].items():
                type_name = {
                    'hardcoded_case_id': '硬编码case_id',
                    'old_get_test_case': '旧的GetTestCase调用',
                    'missing_file_name': '未指定文件名'
                }.get(issue_type, issue_type)
                print(f"  {type_name}: {count} 个")

        # 详细问题
        if analysis_result['files_with_issues'] > 0:
            print(f"\n❌ 详细问题:")
            for result in analysis_result['detailed_results']:
                print(f"\n  📄 {result['file']}:")

                # 显示问题
                for issue in result['issues']:
                    print(f"    ❌ {issue}")

                # 显示旧模式
                for old_pattern in result['old_patterns']:
                    print(f"    🔴 旧模式 (行{old_pattern['line']}): {old_pattern['pattern'][:60]}...")

                # 显示修复建议
                suggestions = self.generate_fix_suggestions(result)
                if suggestions:
                    print(f"    💡 修复建议:")
                    for suggestion in suggestions:
                        print(f"      - {suggestion}")

        # 总体建议
        print(f"\n🔧 总体建议:")
        print(f"  1. 统一使用get_test_data()接口替代旧的数据获取方式")
        print(f"  2. 为所有get_test_data()调用指定具体的文件名")
        print(f"  3. 移除硬编码的case_id列表")
        print(f"  4. 更新导入语句使用新的接口")
        print(f"  5. 检查自动生成的代码是否符合新标准")


def main():
    """主函数"""
    standardizer = DataDriverStandardizer()
    result = standardizer.run_analysis()
    standardizer.print_detailed_report(result)

    # 返回适当的退出码
    if result['files_with_issues'] == 0:
        print("\n🎉 所有数据驱动配置已标准化！")
        return 0
    else:
        print(f"\n⚠️ 发现 {result['files_with_issues']} 个文件需要标准化！")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
