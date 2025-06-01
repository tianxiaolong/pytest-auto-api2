#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path
import ast
import re
import sys

from typing import Any, Dict, List, Tuple
import subprocess

"""
代码质量检查工具
提供代码质量检查、格式化和优化建议

@Time   : 2023-12-20
@Author : txl
"""


class CodeQualityChecker:
    """代码质量检查器"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues = []
        self.suggestions = []

    def check_python_syntax(self, file_path: Path) -> List[str]:
        """检查Python语法"""
        issues = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            try:
                ast.parse(content)
            except SyntaxError as e:
                issues.append(f"语法错误 {file_path}:{e.lineno}: {e.msg}")
        except Exception as e:
            issues.append(f"无法读取文件 {file_path}: {e}")

        return issues

    def check_import_style(self, file_path: Path) -> List[str]:
        """检查导入风格"""
        issues = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            import_section_ended = False
            for i, line in enumerate(lines, 1):
                line = line.strip()

                # 检查导入顺序
                if line.startswith("import ") or line.startswith("from "):
                    if import_section_ended:
                        issues.append(f"{file_path}:{i}: 导入语句应该在文件顶部")
                elif line and not line.startswith("#") and not line.startswith('"""') and not line.startswith("'''"):
                    import_section_ended = True

                # 检查相对导入
                if line.startswith("from ."):
                    continue  # 相对导入是允许的

                # 检查通配符导入
                if "import *" in line:
                    issues.append(f"{file_path}:{i}: 避免使用通配符导入 (import *)")

        except Exception as e:
            issues.append(f"检查导入风格失败 {file_path}: {e}")

        return issues

    def check_function_complexity(self, file_path: Path) -> List[str]:
        """检查函数复杂度"""
        issues = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # 计算函数行数
                    if hasattr(node, "end_lineno") and node.end_lineno:
                        lines = node.end_lineno - node.lineno
                        if lines > 50:
                            issues.append(
                                f"{file_path}:{node.lineno}: " f"函数 '{node.name}' 过长 ({lines} 行)，建议拆分"
                            )

                    # 检查参数数量
                    arg_count = len(node.args.args)
                    if arg_count > 7:
                        issues.append(
                            f"{file_path}:{node.lineno}: " f"函数 '{node.name}' 参数过多 ({arg_count} 个)，建议重构"
                        )

        except Exception as e:
            issues.append(f"检查函数复杂度失败 {file_path}: {e}")

        return issues

    def check_docstrings(self, file_path: Path) -> List[str]:
        """检查文档字符串"""
        issues = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            # 检查模块文档字符串
            if not ast.get_docstring(tree):
                issues.append(f"{file_path}: 缺少模块文档字符串")

            # 检查类和函数文档字符串
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        node_type = "函数" if isinstance(node, ast.FunctionDef) else "类"
                        issues.append(f"{file_path}:{node.lineno}: " f"{node_type} '{node.name}' 缺少文档字符串")

        except Exception as e:
            issues.append(f"检查文档字符串失败 {file_path}: {e}")

        return issues

    def check_naming_conventions(self, file_path: Path) -> List[str]:
        """检查命名规范"""
        issues = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # 函数名应该是snake_case，但排除HTTP处理器的标准方法
                    http_handler_methods = {
                        "do_GET",
                        "do_POST",
                        "do_PUT",
                        "do_DELETE",
                        "do_HEAD",
                        "do_OPTIONS",
                        "do_PATCH",
                        "do_TRACE",
                        "do_CONNECT",
                    }

                    if node.name not in http_handler_methods and not re.match(r"^[a-z_][a-z0-9_]*$", node.name):
                        issues.append(f"{file_path}:{node.lineno}: " f"函数名 '{node.name}' 应使用snake_case命名")

                elif isinstance(node, ast.ClassDef):
                    # 类名应该是PascalCase
                    if not re.match(r"^[A-Z][a-zA-Z0-9]*$", node.name):
                        issues.append(f"{file_path}:{node.lineno}: " f"类名 '{node.name}' 应使用PascalCase命名")

                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    # 变量名应该是snake_case（排除常量）
                    if (
                            not node.id.isupper()
                            and not re.match(r"^[a-z_][a-z0-9_]*$", node.id)
                            and not node.id.startswith("_")
                    ):
                        issues.append(f"{file_path}:{node.lineno}: " f"变量名 '{node.id}' 应使用snake_case命名")

        except Exception as e:
            issues.append(f"检查命名规范失败 {file_path}: {e}")

        return issues

    def check_line_length(self, file_path: Path, max_length: int = 120) -> List[str]:
        """检查行长度"""
        issues = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for i, line in enumerate(lines, 1):
                if len(line.rstrip()) > max_length:
                    issues.append(f"{file_path}:{i}: " f"行长度超过 {max_length} 字符 ({len(line.rstrip())} 字符)")

        except Exception as e:
            issues.append(f"检查行长度失败 {file_path}: {e}")

        return issues

    def check_security_issues(self, file_path: Path) -> List[str]:
        """检查安全问题"""
        issues = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 检查硬编码密码
            password_patterns = [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'passwd\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']',
            ]

            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                for pattern in password_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append(f"{file_path}:{i}: " "可能包含硬编码的敏感信息")

            # 检查SQL注入风险
            if "execute(" in content and "%" in content:
                issues.append(f"{file_path}: 可能存在SQL注入风险，建议使用参数化查询")

            # 检查eval使用
            if "eval(" in content:
                issues.append(f"{file_path}: 使用eval()可能存在安全风险")

        except Exception as e:
            issues.append(f"检查安全问题失败 {file_path}: {e}")

        return issues

    def run_external_tools(self, file_path: Path) -> List[str]:
        """运行外部代码质量工具"""
        issues = []

        # 尝试运行flake8
        try:
            result = subprocess.run(
                ["flake8", str(file_path), "--max-line-length=120"], capture_output=True, text=True, timeout=30
            )
            if result.stdout:
                issues.extend(result.stdout.strip().split("\n"))
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return issues

    def check_file(self, file_path: Path) -> Dict[str, List[str]]:
        """检查单个文件"""
        if not file_path.suffix == ".py":
            return {}

        if "venv" in str(file_path) or "__pycache__" in str(file_path):
            return {}

        results = {
            "syntax": self.check_python_syntax(file_path),
            "imports": self.check_import_style(file_path),
            "complexity": self.check_function_complexity(file_path),
            "docstrings": self.check_docstrings(file_path),
            "naming": self.check_naming_conventions(file_path),
            "line_length": self.check_line_length(file_path),
            "security": self.check_security_issues(file_path),
            "external": self.run_external_tools(file_path),
        }

        return {k: v for k, v in results.items() if v}

    def check_project(self) -> Dict[str, Any]:
        """检查整个项目"""
        print("🔍 开始代码质量检查...")

        python_files = list(self.project_root.rglob("*.py"))
        total_issues = 0
        file_results = {}

        for py_file in python_files:
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            file_issues = self.check_file(py_file)
            if file_issues:
                file_results[str(py_file)] = file_issues
                total_issues += sum(len(issues) for issues in file_issues.values())

        # 生成摘要
        summary = {
            "total_files_checked": len(
                [f for f in python_files if "venv" not in str(f) and "__pycache__" not in str(f)]
            ),
            "files_with_issues": len(file_results),
            "total_issues": total_issues,
            "issue_types": {},
        }

        # 统计问题类型
        for file_issues in file_results.values():
            for issue_type, issues in file_issues.items():
                if issue_type not in summary["issue_types"]:
                    summary["issue_types"][issue_type] = 0
                summary["issue_types"][issue_type] += len(issues)

        return {"summary": summary, "file_results": file_results, "suggestions": self.generate_suggestions(summary)}

    def generate_suggestions(self, summary: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        suggestions = []

        if summary["total_issues"] == 0:
            suggestions.append("🎉 代码质量检查通过，未发现问题！")
            return suggestions

        suggestions.append(f"📊 发现 {summary['total_issues']} 个问题，建议优化：")

        issue_types = summary.get("issue_types", {})

        if "syntax" in issue_types:
            suggestions.append("🔧 修复语法错误（最高优先级）")

        if "security" in issue_types:
            suggestions.append("🔒 修复安全问题（高优先级）")

        if "docstrings" in issue_types:
            suggestions.append("📝 添加缺失的文档字符串")

        if "naming" in issue_types:
            suggestions.append("🏷️ 修正命名规范问题")

        if "complexity" in issue_types:
            suggestions.append("🔄 重构复杂函数")

        if "line_length" in issue_types:
            suggestions.append("📏 调整过长的代码行")

        if "imports" in issue_types:
            suggestions.append("📦 优化导入语句")

        suggestions.extend(
            [
                "",
                "💡 推荐工具:",
                "   - 使用 black 进行代码格式化",
                "   - 使用 isort 整理导入语句",
                "   - 使用 mypy 进行类型检查",
                "   - 配置 pre-commit 钩子自动检查",
            ]
        )

        return suggestions

    def save_report(self, results: Dict[str, Any], file_path: str = "code_quality_report.json"):
        """保存检查报告"""
        import json

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"📄 代码质量报告已保存到: {file_path}")


def main():
    """主函数"""
    checker = CodeQualityChecker()
    results = checker.check_project()

    # 显示摘要
    summary = results["summary"]
    print("\n📋 代码质量检查摘要:")
    print(f"   检查文件数: {summary['total_files_checked']}")
    print(f"   有问题文件: {summary['files_with_issues']}")
    print(f"   问题总数: {summary['total_issues']}")

    if summary["issue_types"]:
        print("   问题分布:")
        for issue_type, count in summary["issue_types"].items():
            print(f"     {issue_type}: {count}")

    # 显示建议
    print("\n💡 改进建议:")
    for suggestion in results["suggestions"]:
        print(suggestion)

    # 保存报告
    checker.save_report(results)

    # 返回退出码
    return 1 if summary["total_issues"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
