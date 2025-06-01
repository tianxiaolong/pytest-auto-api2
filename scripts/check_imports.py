#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check Imports Module

This module provides check imports functionality.
"""

"""
导入检查和修复脚本
检查项目中所有受目录结构变动影响的导入路径

@Time   : 2023-12-20
@Author : txl
"""
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple


class ImportChecker:
    """
    导入检查器

    检查项目中所有Python文件的导入语句，
    识别受目录结构变动影响的导入路径。
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues = []
        self.data_related_imports = set()
        self.all_imports = set()

    def scan_project(self) -> Dict:
        """
        扫描整个项目的导入情况

        Returns:
            扫描结果字典
        """
        print("🔍 开始扫描项目导入情况...")

        python_files = list(self.project_root.rglob("*.py"))

        for file_path in python_files:
            # 跳过虚拟环境和缓存目录
            if any(part in str(file_path) for part in ["venv", "__pycache__", ".git", "node_modules"]):
                continue

            self._analyze_file(file_path)

        return self._generate_report()

    def _analyze_file(self, file_path: Path) -> None:
        """
        分析单个文件的导入情况

        Args:
            file_path: Python文件路径
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 使用AST分析导入
            try:
                tree = ast.parse(content)
                self._analyze_imports_ast(tree, file_path)
            except SyntaxError:
                # 如果AST解析失败，使用正则表达式
                self._analyze_imports_regex(content, file_path)

        except Exception as e:
            self.issues.append({"type": "read_error", "file": str(file_path), "message": f"读取文件失败: {e}"})

    def _analyze_imports_ast(self, tree: ast.AST, file_path: Path) -> None:
        """
        使用AST分析导入语句

        Args:
            tree: AST树
            file_path: 文件路径
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self._check_import(alias.name, file_path, node.lineno)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self._check_import(node.module, file_path, node.lineno, is_from=True)

    def _analyze_imports_regex(self, content: str, file_path: Path) -> None:
        """
        使用正则表达式分析导入语句

        Args:
            content: 文件内容
            file_path: 文件路径
        """
        # 匹配import语句
        import_patterns = [
            r"^import\s+([^\s#]+)",
            r"^from\s+([^\s#]+)\s+import",
        ]

        lines = content.split("\n")
        for line_no, line in enumerate(lines, 1):
            line = line.strip()
            for pattern in import_patterns:
                match = re.match(pattern, line)
                if match:
                    module_name = match.group(1)
                    self._check_import(module_name, file_path, line_no)

    def _check_import(self, module_name: str, file_path: Path, line_no: int, is_from: bool = False) -> None:
        """
        检查单个导入语句

        Args:
            module_name: 模块名称
            file_path: 文件路径
            line_no: 行号
            is_from: 是否是from import语句
        """
        self.all_imports.add(module_name)

        # 检查是否是数据相关的导入
        data_related_patterns = [
            r".*\.yaml_control$",
            r".*\.get_yaml_data.*",
            r".*\.excel_control$",
            r".*\.data_driver_control$",
            r".*GetYamlData.*",
            r".*CaseData.*",
        ]

        for pattern in data_related_patterns:
            if re.search(pattern, module_name, re.IGNORECASE):
                self.data_related_imports.add(module_name)
                break

        # 检查可能有问题的导入（更精确的匹配）
        problematic_patterns = [
            # 只检查真正有问题的导入模式
            (r"^data\..*", "直接导入data目录可能有问题"),
            (r".*GetYamlData.*", "可能需要更新为统一的数据驱动接口"),
            # 排除正常的模块名包含data的情况
            (r"from\s+data\s+import", "直接从data目录导入"),
            (r"import\s+data\.", "直接导入data目录下的模块"),
        ]

        for pattern, message in problematic_patterns:
            if re.search(pattern, module_name):
                self.issues.append(
                    {
                        "type": "potentially_problematic",
                        "file": str(file_path),
                        "line": line_no,
                        "import": module_name,
                        "message": message,
                        "is_from": is_from,
                    }
                )

    def _generate_report(self) -> Dict:
        """
        生成分析报告

        Returns:
            分析报告字典
        """
        return {
            "total_imports": len(self.all_imports),
            "data_related_imports": len(self.data_related_imports),
            "issues": self.issues,
            "data_imports": list(self.data_related_imports),
            "all_imports": list(self.all_imports),
        }

    def print_report(self) -> None:
        """打印分析报告"""
        report = self._generate_report()

        print("\n" + "=" * 60)
        print("📋 导入分析报告")
        print("=" * 60)

        print("\n📊 统计信息:")
        print(f"   总导入数: {report['total_imports']}")
        print(f"   数据相关导入数: {report['data_related_imports']}")
        print(f"   潜在问题数: {len(report['issues'])}")

        if report["data_imports"]:
            print("\n📦 数据相关导入:")
            for imp in sorted(report["data_imports"]):
                print(f"   - {imp}")

        if report["issues"]:
            print("\n⚠️  潜在问题:")

            # 按类型分组
            issues_by_type = {}
            for issue in report["issues"]:
                issue_type = issue["type"]
                if issue_type not in issues_by_type:
                    issues_by_type[issue_type] = []
                issues_by_type[issue_type].append(issue)

            for issue_type, issues in issues_by_type.items():
                print(f"\n📋 {issue_type} ({len(issues)} 个):")
                for issue in issues:
                    if "import" in issue:
                        print(f"   📄 {issue['file']}:{issue['line']}")
                        print(f"      导入: {issue['import']}")
                        print(f"      说明: {issue['message']}")
                    else:
                        print(f"   📄 {issue['file']}")
                        print(f"      说明: {issue['message']}")

        print("\n💡 建议:")
        print("   1. 检查数据相关的导入路径")
        print("   2. 更新为统一的数据驱动接口")
        print("   3. 移除直接的data目录导入")
        print("   4. 使用新的数据驱动管理器")


def main():
    """主函数"""
    checker = ImportChecker()
    checker.scan_project()
    checker.print_report()


if __name__ == "__main__":
    main()
