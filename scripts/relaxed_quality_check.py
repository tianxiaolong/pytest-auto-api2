#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Relaxed Quality Check Module

This module provides relaxed quality check functionality.
"""

"""
宽松的代码质量检查脚本
专注于真正重要的代码质量问题

@Time   : 2023-12-20
@Author : txl
"""
import ast
import re
from pathlib import Path
from typing import Dict, List


class RelaxedCodeQualityChecker:
    """宽松的代码质量检查器"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues = []

    def check_all(self) -> Dict[str, List[str]]:
        """执行所有检查"""
        self.issues = []

        # 检查文件命名
        self._check_file_naming()

        # 检查编码声明
        self._check_encoding_declarations()

        # 检查Python代码规范
        self._check_python_code()

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

    def _check_encoding_declarations(self) -> None:
        """检查编码声明"""
        python_files = list(self.project_root.rglob("*.py"))

        for file_path in python_files:
            # 跳过虚拟环境和缓存目录
            if any(part in str(file_path) for part in ["venv", "__pycache__", ".git"]):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                if len(lines) < 2:
                    continue

                # 检查前3行是否包含编码声明
                has_encoding = any("coding" in line for line in lines[:3])

                if not has_encoding:
                    self.issues.append({"type": "encoding", "file": str(file_path), "message": "缺少编码声明"})

            except Exception as e:
                self.issues.append({"type": "error", "file": str(file_path), "message": f"读取文件失败: {e}"})

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

    def _generate_report(self) -> Dict[str, List[str]]:
        """生成检查报告"""
        report = {"naming": [], "encoding": [], "syntax": [], "class_naming": [], "function_naming": [], "error": []}

        for issue in self.issues:
            issue_type = issue["type"]
            if issue_type in report:
                report[issue_type].append(f"{issue['file']}: {issue['message']}")

        return report

    def print_report(self) -> None:
        """打印检查报告"""
        report = self._generate_report()

        print("=" * 60)
        print("代码质量检查报告（宽松模式）")
        print("=" * 60)

        total_issues = sum(len(issues) for issues in report.values())

        if total_issues == 0:
            print("✅ 恭喜！没有发现重要的代码质量问题。")
            print("\n📝 注意：此检查采用宽松模式，专注于核心问题。")
            print("   如需更严格的检查，请使用 code_quality_check.py")
            return

        print(f"🔍 总共发现 {total_issues} 个重要问题：\n")

        for issue_type, issues in report.items():
            if issues:
                type_names = {
                    "naming": "文件命名问题",
                    "encoding": "编码声明问题",
                    "syntax": "语法错误",
                    "class_naming": "类命名问题",
                    "function_naming": "函数命名问题",
                    "error": "其他错误",
                }

                print(f"📋 {type_names.get(issue_type, issue_type)} ({len(issues)} 个):")
                for issue in issues:
                    print(f"   - {issue}")
                print()

        print("💡 建议：")
        print("   1. 优先修复语法错误和编码声明问题")
        print("   2. 类名和函数名问题影响代码可读性，建议修复")
        print("   3. 文件命名问题可以逐步改进")


def main():
    """主函数"""
    checker = RelaxedCodeQualityChecker()
    checker.check_all()
    checker.print_report()


if __name__ == "__main__":
    main()
