#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Code Quality Check Module

This module provides code quality check functionality.
"""

"""
代码质量检查脚本
检查项目中的代码规范、命名规范等问题

@Time   : 2023-12-20
@Author : txl
"""
import ast
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple


class CodeQualityChecker:
    """代码质量检查器"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues = []

    def check_all(self) -> Dict[str, List[str]]:
        """执行所有检查"""
        self.issues = []

        # 检查文件命名
        self._check_file_naming()

        # 检查Python代码规范
        self._check_python_code()

        # 检查导入规范
        self._check_imports()

        # 生成报告
        return self._generate_report()

    def _check_file_naming(self) -> None:
        """检查文件命名规范"""
        python_files = list(self.project_root.rglob("*.py"))

        for file_path in python_files:
            # 跳过虚拟环境和缓存目录
            if any(part in str(file_path) for part in ["venv", "__pycache__", ".git"]):
                continue

            filename = file_path.name

            # 检查Python文件命名（应使用下划线）
            if not re.match(r"^[a-z][a-z0-9_]*\.py$", filename) and filename != "__init__.py":
                self.issues.append(
                    {
                        "type": "naming",
                        "file": str(file_path),
                        "message": f"文件名不符合Python命名规范: {filename}，应使用小写字母和下划线",
                    }
                )

    def _check_python_code(self) -> None:
        """检查Python代码规范"""
        python_files = list(self.project_root.rglob("*.py"))

        for file_path in python_files:
            # 跳过虚拟环境和缓存目录
            if any(part in str(file_path) for part in ["venv", "__pycache__", ".git"]):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # 检查编码声明
                lines = content.split("\n")
                if len(lines) > 1 and "coding" not in lines[1] and "coding" not in lines[0]:
                    self.issues.append({"type": "encoding", "file": str(file_path), "message": "缺少编码声明"})

                # 解析AST检查类名和函数名
                try:
                    tree = ast.parse(content)
                    self._check_ast_naming(tree, file_path)
                except SyntaxError as e:
                    self.issues.append({"type": "syntax", "file": str(file_path), "message": f"语法错误: {e}"})

            except Exception as e:
                self.issues.append({"type": "error", "file": str(file_path), "message": f"读取文件失败: {e}"})

    def _check_ast_naming(self, tree: ast.AST, file_path: Path) -> None:
        """检查AST中的命名规范"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 检查类名（应使用PascalCase）
                if not re.match(r"^[A-Z][a-zA-Z0-9]*$", node.name):
                    self.issues.append(
                        {
                            "type": "class_naming",
                            "file": str(file_path),
                            "message": f"类名不符合规范: {node.name}，应使用PascalCase",
                        }
                    )

            elif isinstance(node, ast.FunctionDef):
                # 检查函数名（应使用snake_case）
                if not re.match(r"^[a-z_][a-z0-9_]*$", node.name) and not node.name.startswith("__"):
                    self.issues.append(
                        {
                            "type": "function_naming",
                            "file": str(file_path),
                            "message": f"函数名不符合规范: {node.name}，应使用snake_case",
                        }
                    )

            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                # 检查变量名（应使用snake_case）
                # 排除 Pydantic 模型字段名和异常类名
                excluded_names = {"AssertType", "requestType", "JSONDecodeError"}
                if (
                    not re.match(r"^[a-z_][a-z0-9_]*$", node.id)
                    and not node.id.isupper()  # 常量可以全大写
                    and not node.id.startswith("_")  # 私有变量可以下划线开头
                    and node.id not in excluded_names
                ):  # 排除特殊字段名
                    self.issues.append(
                        {
                            "type": "variable_naming",
                            "file": str(file_path),
                            "message": f"变量名不符合规范: {node.id}，应使用snake_case",
                        }
                    )

    def _check_imports(self) -> None:
        """检查导入规范"""
        python_files = list(self.project_root.rglob("*.py"))

        for file_path in python_files:
            # 跳过虚拟环境和缓存目录
            if any(part in str(file_path) for part in ["venv", "__pycache__", ".git"]):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                lines = content.split("\n")
                import_lines = []

                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.startswith("import ") or stripped.startswith("from "):
                        import_lines.append((i + 1, stripped))

                # 检查导入顺序（标准库 -> 第三方库 -> 本地库）
                self._check_import_order(import_lines, file_path)

            except Exception as e:
                self.issues.append({"type": "error", "file": str(file_path), "message": f"检查导入失败: {e}"})

    def _check_import_order(self, import_lines: List[Tuple[int, str]], file_path: Path) -> None:
        """检查导入顺序"""
        if len(import_lines) < 2:
            return

        # 更完整的标准库模块列表
        stdlib_modules = {
            "os",
            "sys",
            "json",
            "time",
            "datetime",
            "pathlib",
            "typing",
            "logging",
            "unittest",
            "collections",
            "re",
            "ast",
            "inspect",
            "traceback",
            "functools",
            "itertools",
            "random",
            "string",
            "urllib",
            "http",
            "email",
            "hashlib",
            "base64",
            "uuid",
            "binascii",
            "hmac",
            "socket",
            "threading",
            "multiprocessing",
            "subprocess",
            "shutil",
            "tempfile",
            "glob",
            "fnmatch",
            "linecache",
            "pickle",
            "copyreg",
            "copy",
            "pprint",
            "reprlib",
            "enum",
            "numbers",
            "math",
            "cmath",
            "decimal",
            "fractions",
            "statistics",
            "array",
            "weakre",
            "types",
            "gc",
            "contextlib",
            "abc",
            "atexit",
            "traceback",
            "warnings",
            "dataclasses",
        }

        # 分类所有导入
        stdlib_imports = []
        third_party_imports = []
        local_imports = []

        for line_num, import_line in import_lines:
            if import_line.startswith("from "):
                module = import_line.split()[1].split(".")[0]
            else:
                module = import_line.split()[1].split(".")[0]

            # 确定当前导入的类型
            if module in stdlib_modules:
                stdlib_imports.append((line_num, import_line))
            elif module.startswith(".") or any(local in module for local in ["utils", "common", "test_case"]):
                local_imports.append((line_num, import_line))
            else:
                third_party_imports.append((line_num, import_line))

        # 检查顺序：标准库 -> 第三方库 -> 本地库
        # 但如果某个类型的导入不存在，则跳过
        expected_order = []
        if stdlib_imports:
            expected_order.extend(stdlib_imports)
        if third_party_imports:
            expected_order.extend(third_party_imports)
        if local_imports:
            expected_order.extend(local_imports)

        # 检查实际顺序是否与期望顺序一致
        actual_order = [(line_num, import_line) for line_num, import_line in import_lines]

        # 只有当顺序真的不对时才报告问题
        if len(expected_order) == len(actual_order):
            for i, (expected, actual) in enumerate(zip(expected_order, actual_order)):
                if expected[1].strip() != actual[1].strip():
                    self.issues.append(
                        {
                            "type": "import_order",
                            "file": str(file_path),
                            "message": "导入顺序不正确，建议按照：标准库 -> 第三方库 -> 本地库的顺序",
                        }
                    )
                    break

    def _generate_report(self) -> Dict[str, List[str]]:
        """生成检查报告"""
        report = {
            "naming": [],
            "encoding": [],
            "syntax": [],
            "class_naming": [],
            "function_naming": [],
            "variable_naming": [],
            "import_order": [],
            "error": [],
        }

        for issue in self.issues:
            issue_type = issue["type"]
            if issue_type in report:
                report[issue_type].append(f"{issue['file']}: {issue['message']}")

        return report

    def print_report(self) -> None:
        """打印检查报告"""
        report = self._generate_report()

        print("=" * 60)
        print("代码质量检查报告")
        print("=" * 60)

        total_issues = sum(len(issues) for issues in report.values())

        if total_issues == 0:
            print("✅ 恭喜！没有发现代码质量问题。")
            return

        print(f"🔍 总共发现 {total_issues} 个问题：\n")

        for issue_type, issues in report.items():
            if issues:
                type_names = {
                    "naming": "文件命名问题",
                    "encoding": "编码声明问题",
                    "syntax": "语法错误",
                    "class_naming": "类命名问题",
                    "function_naming": "函数命名问题",
                    "variable_naming": "变量命名问题",
                    "import_order": "导入顺序问题",
                    "error": "其他错误",
                }

                print(f"📋 {type_names.get(issue_type, issue_type)} ({len(issues)} 个):")
                for issue in issues:
                    print(f"   - {issue}")
                print()


def main():
    """主函数"""
    checker = CodeQualityChecker()
    checker.check_all()
    checker.print_report()


if __name__ == "__main__":
    main()
