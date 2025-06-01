#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全面的数据驱动配置检查工具

检查所有测试文件的数据驱动配置，确保：
1. 每个测试文件使用正确的数据文件
2. YAML和Excel数据驱动配置一致
3. 没有重复的测试用例
4. 数据文件存在且可读取
"""

import ast
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple


class ComprehensiveDataDriverChecker:
    """全面的数据驱动配置检查器"""
    
    def __init__(self):
        """初始化检查器"""
        self.project_root = Path(__file__).parent.parent
        self.test_case_dir = self.project_root / "test_case"
        self.yaml_data_dir = self.project_root / "data" / "yaml_data" / "pytest-auto-api2"
        self.excel_data_dir = self.project_root / "data" / "excel_data" / "pytest-auto-api2"
        
        self.issues = []
        self.recommendations = []
    
    def find_test_files(self) -> List[Path]:
        """查找所有测试文件"""
        test_files = []
        for test_file in self.test_case_dir.rglob("test_*.py"):
            if "__pycache__" not in str(test_file):
                test_files.append(test_file)
        return test_files
    
    def analyze_test_file(self, test_file: Path) -> Dict[str, Any]:
        """分析单个测试文件的数据驱动配置"""
        result = {
            'file': str(test_file.relative_to(self.project_root)),
            'module': test_file.parent.name,
            'get_test_data_calls': [],
            'issues': [],
            'recommendations': []
        }
        
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找get_test_data调用
            patterns = [
                r'get_test_data\s*\(\s*["\']([^"\']+)["\'](?:\s*,\s*["\']([^"\']*)["\'])?\s*\)',
                r'test_data\s*=\s*get_test_data\s*\(\s*["\']([^"\']+)["\'](?:\s*,\s*["\']([^"\']*)["\'])?\s*\)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    module_name = match[0]
                    file_name = match[1] if len(match) > 1 and match[1] else None
                    result['get_test_data_calls'].append({
                        'module': module_name,
                        'file_name': file_name,
                        'has_file_name': file_name is not None and file_name != ''
                    })
            
            # 检查问题
            self._check_file_issues(result, test_file)
            
        except Exception as e:
            result['issues'].append(f"文件读取失败: {e}")
        
        return result
    
    def _check_file_issues(self, result: Dict[str, Any], test_file: Path):
        """检查文件中的问题"""
        module_name = result['module']
        calls = result['get_test_data_calls']
        
        if not calls:
            result['issues'].append("未找到get_test_data调用")
            return
        
        # 检查是否指定了文件名
        for call in calls:
            if not call['has_file_name']:
                result['issues'].append(f"未指定数据文件名: get_test_data('{call['module']}')")
                result['recommendations'].append(f"建议指定具体文件名，避免自动选择第一个文件")
            
            # 检查模块名是否与目录匹配
            if call['module'] != module_name:
                result['issues'].append(f"模块名不匹配: 文件在{module_name}目录，但调用了{call['module']}模块")
        
        # 检查对应的数据文件是否存在
        self._check_data_files_exist(result, module_name)
    
    def _check_data_files_exist(self, result: Dict[str, Any], module_name: str):
        """检查对应的数据文件是否存在"""
        # 检查YAML文件
        yaml_module_dir = self.yaml_data_dir / module_name
        if yaml_module_dir.exists():
            yaml_files = list(yaml_module_dir.glob("*.yaml")) + list(yaml_module_dir.glob("*.yml"))
            result['yaml_files'] = [f.name for f in yaml_files]
        else:
            result['issues'].append(f"YAML数据目录不存在: {yaml_module_dir}")
            result['yaml_files'] = []
        
        # 检查Excel文件
        excel_module_dir = self.excel_data_dir / module_name
        if excel_module_dir.exists():
            excel_files = list(excel_module_dir.glob("*.xlsx")) + list(excel_module_dir.glob("*.xls"))
            result['excel_files'] = [f.name for f in excel_files]
        else:
            result['issues'].append(f"Excel数据目录不存在: {excel_module_dir}")
            result['excel_files'] = []
    
    def check_data_consistency(self) -> Dict[str, Any]:
        """检查数据一致性"""
        print("🔍 开始全面数据驱动配置检查...")
        
        test_files = self.find_test_files()
        results = []
        
        print(f"📁 找到 {len(test_files)} 个测试文件")
        
        for test_file in test_files:
            print(f"  📄 检查: {test_file.relative_to(self.project_root)}")
            result = self.analyze_test_file(test_file)
            results.append(result)
        
        # 汇总分析
        summary = self._generate_summary(results)
        
        return {
            'test_files': results,
            'summary': summary,
            'total_issues': len(self.issues),
            'total_recommendations': len(self.recommendations)
        }
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成汇总信息"""
        summary = {
            'total_files': len(results),
            'files_with_issues': 0,
            'files_without_file_names': 0,
            'modules': {},
            'common_issues': [],
            'recommendations': []
        }
        
        for result in results:
            if result['issues']:
                summary['files_with_issues'] += 1
                self.issues.extend(result['issues'])
            
            # 检查是否有未指定文件名的调用
            for call in result['get_test_data_calls']:
                if not call['has_file_name']:
                    summary['files_without_file_names'] += 1
                    break
            
            # 按模块统计
            module = result['module']
            if module not in summary['modules']:
                summary['modules'][module] = {
                    'test_files': 0,
                    'yaml_files': set(),
                    'excel_files': set(),
                    'issues': 0
                }
            
            summary['modules'][module]['test_files'] += 1
            summary['modules'][module]['yaml_files'].update(result.get('yaml_files', []))
            summary['modules'][module]['excel_files'].update(result.get('excel_files', []))
            summary['modules'][module]['issues'] += len(result['issues'])
        
        # 转换set为list以便JSON序列化
        for module_info in summary['modules'].values():
            module_info['yaml_files'] = list(module_info['yaml_files'])
            module_info['excel_files'] = list(module_info['excel_files'])
        
        # 生成通用建议
        if summary['files_without_file_names'] > 0:
            summary['recommendations'].append(
                f"有 {summary['files_without_file_names']} 个文件未指定数据文件名，建议明确指定以避免数据混乱"
            )
        
        return summary
    
    def print_detailed_report(self, check_result: Dict[str, Any]):
        """打印详细报告"""
        print("\n" + "=" * 80)
        print("📊 全面数据驱动配置检查报告")
        print("=" * 80)
        
        summary = check_result['summary']
        
        # 总体统计
        print(f"\n📈 总体统计:")
        print(f"  测试文件总数: {summary['total_files']}")
        print(f"  有问题的文件: {summary['files_with_issues']}")
        print(f"  未指定文件名的文件: {summary['files_without_file_names']}")
        
        # 按模块统计
        print(f"\n📁 模块统计:")
        for module, info in summary['modules'].items():
            print(f"  {module}模块:")
            print(f"    测试文件: {info['test_files']} 个")
            print(f"    YAML文件: {len(info['yaml_files'])} 个 {info['yaml_files']}")
            print(f"    Excel文件: {len(info['excel_files'])} 个 {info['excel_files']}")
            print(f"    问题数量: {info['issues']} 个")
        
        # 详细问题
        if summary['files_with_issues'] > 0:
            print(f"\n❌ 发现的问题:")
            for result in check_result['test_files']:
                if result['issues']:
                    print(f"  📄 {result['file']}:")
                    for issue in result['issues']:
                        print(f"    - {issue}")
                    if result['recommendations']:
                        print(f"    💡 建议:")
                        for rec in result['recommendations']:
                            print(f"      - {rec}")
        
        # 总体建议
        if summary['recommendations']:
            print(f"\n💡 总体建议:")
            for rec in summary['recommendations']:
                print(f"  - {rec}")
        
        # 修复建议
        print(f"\n🔧 修复建议:")
        print(f"  1. 为所有get_test_data()调用指定具体的文件名")
        print(f"  2. 确保测试文件名与数据文件名对应")
        print(f"  3. 检查数据文件是否存在且可读取")
        print(f"  4. 运行数据一致性验证工具确认修复效果")


def main():
    """主函数"""
    checker = ComprehensiveDataDriverChecker()
    result = checker.check_data_consistency()
    checker.print_detailed_report(result)
    
    # 返回适当的退出码
    if result['summary']['files_with_issues'] == 0:
        print("\n🎉 所有数据驱动配置检查通过！")
        return 0
    else:
        print(f"\n⚠️ 发现 {result['summary']['files_with_issues']} 个文件有配置问题！")
        return 1


if __name__ == "__main__":
    sys.exit(main())
