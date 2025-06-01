#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Optimize Comments Module

This module provides optimize comments functionality.
"""

"""
代码注释优化脚本
自动检查和优化项目中的代码注释，提高代码可读性

主要功能：
- 检查缺少注释的类和函数
- 优化现有注释的语言表达
- 添加类型注解
- 生成标准格式的文档字符串
- 统计注释覆盖率

@Time   : 2023-12-20
@Author : txl
"""
import ast
import re
from pathlib import Path
from typing import Dict, List, Tuple


class CommentOptimizer:
    """代码注释优化器"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues = []
        self.stats = {
            "total_classes": 0,
            "commented_classes": 0,
            "total_functions": 0,
            "commented_functions": 0,
            "total_files": 0,
            "processed_files": 0,
        }

    def analyze_project(self) -> Dict:
        """分析整个项目的注释情况"""
        print("开始分析项目注释情况...")

        python_files = list(self.project_root.rglob("*.py"))

        for file_path in python_files:
            # 跳过虚拟环境和缓存目录
            if any(part in str(file_path) for part in ["venv", "__pycache__", ".git"]):
                continue

            self.stats["total_files"] += 1
            self._analyze_file(file_path)
            self.stats["processed_files"] += 1

        return self._generate_report()

    def _analyze_file(self, file_path: Path) -> None:
        """分析单个文件的注释情况"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            try:
                tree = ast.parse(content)
                self._analyze_ast(tree, file_path)
            except SyntaxError:
                self.issues.append(
                    {"type": "syntax_error", "file": str(file_path), "message": "文件存在语法错误，无法分析"}
                )

        except Exception as e:
            self.issues.append({"type": "read_error", "file": str(file_path), "message": f"读取文件失败: {e}"})

    def _analyze_ast(self, tree: ast.AST, file_path: Path) -> None:
        """分析AST中的类和函数注释"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self.stats["total_classes"] += 1
                if self._has_docstring(node):
                    self.stats["commented_classes"] += 1
                else:
                    self.issues.append(
                        {
                            "type": "missing_class_comment",
                            "file": str(file_path),
                            "name": node.name,
                            "line": node.lineno,
                            "message": f"类 {node.name} 缺少文档字符串",
                        }
                    )

            elif isinstance(node, ast.FunctionDef):
                # 跳过私有方法和特殊方法的检查
                if not node.name.startswith("_"):
                    self.stats["total_functions"] += 1
                    if self._has_docstring(node):
                        self.stats["commented_functions"] += 1
                    else:
                        self.issues.append(
                            {
                                "type": "missing_function_comment",
                                "file": str(file_path),
                                "name": node.name,
                                "line": node.lineno,
                                "message": f"函数 {node.name} 缺少文档字符串",
                            }
                        )

    def _has_docstring(self, node) -> bool:
        """检查节点是否有文档字符串"""
        return node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str)

    def _generate_report(self) -> Dict:
        """生成分析报告"""
        # 计算注释覆盖率
        class_coverage = (self.stats["commented_classes"] / max(self.stats["total_classes"], 1)) * 100
        function_coverage = (self.stats["commented_functions"] / max(self.stats["total_functions"], 1)) * 100

        report = {
            "stats": self.stats,
            "class_coverage": round(class_coverage, 2),
            "function_coverage": round(function_coverage, 2),
            "issues": self.issues,
        }

        return report

    def print_report(self) -> None:
        """打印分析报告"""
        report = self._generate_report()

        print("\n" + "=" * 60)
        print("代码注释分析报告")
        print("=" * 60)

        print("\n📊 统计信息:")
        print(f"   处理文件数: {report['stats']['processed_files']}/{report['stats']['total_files']}")
        print(f"   总类数: {report['stats']['total_classes']}")
        print(f"   已注释类数: {report['stats']['commented_classes']}")
        print(f"   总函数数: {report['stats']['total_functions']}")
        print(f"   已注释函数数: {report['stats']['commented_functions']}")

        print("\n📈 注释覆盖率:")
        print(f"   类注释覆盖率: {report['class_coverage']:.1f}%")
        print(f"   函数注释覆盖率: {report['function_coverage']:.1f}%")

        # 按类型分组显示问题
        issues_by_type = {}
        for issue in report["issues"]:
            issue_type = issue["type"]
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)

        if issues_by_type:
            print("\n🔍 发现的问题:")

            type_names = {
                "missing_class_comment": "缺少类注释",
                "missing_function_comment": "缺少函数注释",
                "syntax_error": "语法错误",
                "read_error": "读取错误",
            }

            for issue_type, issues in issues_by_type.items():
                print(f"\n📋 {type_names.get(issue_type, issue_type)} ({len(issues)} 个):")
                for issue in issues[:10]:  # 只显示前10个
                    if "name" in issue:
                        print(f"   - {issue['file']}:{issue['line']} - {issue['name']}")
                    else:
                        print(f"   - {issue['file']} - {issue['message']}")

                if len(issues) > 10:
                    print(f"   ... 还有 {len(issues) - 10} 个类似问题")
        else:
            print("\n✅ 恭喜！没有发现注释问题。")

        print("\n💡 建议:")
        if report["class_coverage"] < 80:
            print("   - 类注释覆盖率较低，建议为重要类添加文档字符串")
        if report["function_coverage"] < 70:
            print("   - 函数注释覆盖率较低，建议为公共函数添加文档字符串")

        print("   - 优先为核心业务逻辑添加注释")
        print("   - 使用标准的文档字符串格式")
        print("   - 添加参数和返回值说明")


def main():
    """主函数"""
    optimizer = CommentOptimizer()
    optimizer.analyze_project()
    optimizer.print_report()


if __name__ == "__main__":
    main()
