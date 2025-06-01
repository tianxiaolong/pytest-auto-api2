#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path
import ast
import json
import os
import re
import sys

from typing import Any, Dict, List, Set

"""
高级代码优化工具
自动修复导入语句、添加文档字符串、优化代码结构

@Time   : 2023-12-20
@Author : txl
"""


class AdvancedCodeOptimizer:
    """高级代码优化器"""

    def __init__(self, project_root: str = "."):
        """初始化实例"""
        self.project_root = Path(project_root)
        self.fixed_files = []
        self.fixed_issues = {
            "import_organization": 0,
            "docstrings_added": 0,
            "security_fixes": 0,
            "naming_fixes": 0,
            "line_length_fixes": 0,
        }

    def organize_imports(self, file_path: Path) -> bool:
        """整理导入语句"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")

            # 找到文档字符串结束位置
            doc_end = 0
            in_docstring = False
            docstring_quote = None

            for i, line in enumerate(lines):
                stripped = line.strip()
                if not in_docstring:
                    if stripped.startswith('"""') or stripped.startswith("'''"):
                        docstring_quote = stripped[:3]
                        if stripped.count(docstring_quote) >= 2:
                            # 单行文档字符串
                            doc_end = i + 1
                        else:
                            in_docstring = True
                    elif stripped.startswith("#") or not stripped:
                        continue
                    else:
                        doc_end = i
                        break
                else:
                    if docstring_quote in line:
                        doc_end = i + 1
                        break

            # 分离导入语句和其他代码
            imports = []
            other_lines = []
            import_section_ended = False

            for i, line in enumerate(lines):
                if i < doc_end:
                    other_lines.append(line)
                    continue

                stripped = line.strip()
                if (stripped.startswith("import ") or stripped.startswith("from ")) and not import_section_ended:
                    imports.append(line)
                elif stripped and not stripped.startswith("#"):
                    import_section_ended = True
                    other_lines.append(line)
                else:
                    other_lines.append(line)

            if not imports:
                return False

            # 对导入语句进行分类和排序
            stdlib_imports = []
            third_party_imports = []
            local_imports = []

            stdlib_modules = {
                "os",
                "sys",
                "time",
                "json",
                "ast",
                "re",
                "pathlib",
                "typing",
                "subprocess",
                "threading",
                "multiprocessing",
                "collections",
                "functools",
                "itertools",
                "datetime",
                "hashlib",
                "base64",
                "urllib",
                "http",
                "socket",
                "ssl",
                "email",
                "xml",
                "csv",
            }

            for imp in imports:
                stripped = imp.strip()
                if stripped.startswith("from "):
                    module = stripped.split()[1].split(".")[0]
                else:
                    module = stripped.split()[1].split(".")[0]

                if module in stdlib_modules:
                    stdlib_imports.append(imp)
                elif module.startswith(".") or "utils" in module or "common" in module or "test_case" in module:
                    local_imports.append(imp)
                else:
                    third_party_imports.append(imp)

            # 重新组织文件内容
            new_content_lines = other_lines[:doc_end]

            if stdlib_imports:
                new_content_lines.extend(sorted(stdlib_imports))
                new_content_lines.append("")

            if third_party_imports:
                new_content_lines.extend(sorted(third_party_imports))
                new_content_lines.append("")

            if local_imports:
                new_content_lines.extend(sorted(local_imports))
                new_content_lines.append("")

            # 添加其余内容
            remaining_lines = other_lines[doc_end:]
            # 跳过开头的空行
            while remaining_lines and not remaining_lines[0].strip():
                remaining_lines.pop(0)

            new_content_lines.extend(remaining_lines)

            new_content = "\n".join(new_content_lines)

            if new_content != content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                self.fixed_issues["import_organization"] += 1
                return True

            return False

        except Exception as e:
            print(f"整理导入失败 {file_path}: {e}")
            return False

    def add_missing_docstrings(self, file_path: Path) -> bool:
        """添加缺失的文档字符串"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            lines = content.split("\n")

            # 检查模块文档字符串
            if not ast.get_docstring(tree):
                # 添加模块文档字符串
                module_name = file_path.stem
                docstring = (
                    f'"""\n{module_name} module\nProvides functionality for {module_name.replace("_", " ")}\n"""\n'
                )

                # 找到插入位置（在编码声明和导入之前）
                insert_pos = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith("#") and ("coding" in line or "encoding" in line):
                        insert_pos = i + 1
                        break

                lines.insert(insert_pos, docstring)
                self.fixed_issues["docstrings_added"] += 1

            # 为类和函数添加文档字符串
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        # 这里只标记需要添加，实际添加比较复杂
                        # 可以在后续版本中实现
                        pass

            new_content = "\n".join(lines)
            if new_content != content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                return True

            return False

        except Exception as e:
            print(f"添加文档字符串失败 {file_path}: {e}")
            return False

    def fix_security_issues(self, file_path: Path) -> bool:
        """修复安全问题"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # 修复硬编码密码（添加注释提醒）
            password_patterns = [
                (
                    r'password\s*=\s*["\']([^"\']+)["\']',
                    r'password = "***"  # TODO: Use environment variable for security  # TODO: Use environment variable  # TODO: Use environment variable  # TODO: Use environment variable  # TODO: Use environment variable  # TODO: Use environment variable  # TODO: Use environment variable',
                ),
                (
                    r'secret\s*=\s*["\']([^"\']+)["\']',
                    r'secret = "***"  # TODO: Use environment variable for security  # TODO: Use environment variable  # TODO: Use environment variable  # TODO: Use environment variable  # TODO: Use environment variable  # TODO: Use environment variable  # TODO: Use environment variable',
                ),
                (
                    r'token\s*=\s*["\']([^"\']+)["\']',
                    r'token = "***"  # TODO: Use environment variable for security  # TODO: Use environment variable  # TODO: Use environment variable  # TODO: Use environment variable  # TODO: Use environment variable  # TODO: Use environment variable  # TODO: Use environment variable',
                ),
            ]

            for pattern, replacement in password_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    # 只添加注释，不修改实际值（避免破坏功能）
                    content = re.sub(
                        pattern,
                        lambda m: f"{m.group(0)}  # TODO: Use environment variable",
                        content,
                        flags=re.IGNORECASE,
                    )
                    self.fixed_issues["security_fixes"] += 1

            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True

            return False

        except Exception as e:
            print(f"修复安全问题失败 {file_path}: {e}")
            return False

    def fix_line_length(self, file_path: Path, max_length: int = 120) -> bool:
        """修复行长度问题"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            fixed = False
            new_lines = []

            for line in lines:
                if len(line.rstrip()) > max_length:
                    # 简单的行分割（只处理明显可以分割的情况）
                    stripped = line.rstrip()
                    indent = len(line) - len(line.lstrip())
                    indent_str = " " * indent

                    # 如果是字符串连接，可以分割
                    if " + " in stripped and '"' in stripped:
                        parts = stripped.split(" + ")
                        if len(parts) > 1:
                            new_lines.append(parts[0] + " + \\\n")
                            for part in parts[1:-1]:
                                new_lines.append(indent_str + "    " + part + " + \\\n")
                            new_lines.append(indent_str + "    " + parts[-1] + "\n")
                            fixed = True
                            self.fixed_issues["line_length_fixes"] += 1
                            continue

                new_lines.append(line)

            if fixed:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                return True

            return False

        except Exception as e:
            print(f"修复行长度失败 {file_path}: {e}")
            return False

    def optimize_file(self, file_path: Path) -> bool:
        """优化单个文件"""
        if not file_path.suffix == ".py":
            return False

        if "venv" in str(file_path) or "__pycache__" in str(file_path):
            return False

        file_fixed = False

        # 整理导入语句
        if self.organize_imports(file_path):
            file_fixed = True

        # 添加文档字符串
        if self.add_missing_docstrings(file_path):
            file_fixed = True

        # 修复安全问题
        if self.fix_security_issues(file_path):
            file_fixed = True

        # 修复行长度
        if self.fix_line_length(file_path):
            file_fixed = True

        if file_fixed:
            self.fixed_files.append(str(file_path))

        return file_fixed

    def optimize_project(self) -> Dict[str, Any]:
        """优化整个项目"""
        print("🔧 开始高级代码优化...")

        python_files = list(self.project_root.rglob("*.py"))
        total_files = 0
        fixed_files = 0

        for py_file in python_files:
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            total_files += 1

            if self.optimize_file(py_file):
                fixed_files += 1

        return {
            "total_files": total_files,
            "fixed_files": fixed_files,
            "fixed_issues": self.fixed_issues,
            "fixed_file_list": self.fixed_files,
        }


def create_pre_commit_config():
    """创建pre-commit配置"""
    config = """repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        args: [--line-length=120]
        
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=black, --line-length=120]
        
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=120, --ignore=E203,W503]
        
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, types-PyYAML]
"""

    try:
        with open(".pre-commit-config.yaml", "w", encoding="utf-8") as f:
            f.write(config)
        print("✅ 创建 .pre-commit-config.yaml")
    except Exception as e:
        print(f"❌ 创建pre-commit配置失败: {e}")


def main():
    """主函数"""
    optimizer = AdvancedCodeOptimizer()

    print("🚀 开始高级代码质量优化...")
    print("=" * 60)

    # 创建pre-commit配置
    create_pre_commit_config()

    # 运行优化
    results = optimizer.optimize_project()

    print(f"\n📊 优化结果:")
    print(f"   检查文件数: {results['total_files']}")
    print(f"   优化文件数: {results['fixed_files']}")
    print(f"   优化问题统计:")
    for issue_type, count in results["fixed_issues"].items():
        if count > 0:
            print(f"     {issue_type}: {count}")

    # 显示优化的文件列表
    if results["fixed_file_list"]:
        print(f"\n📝 优化的文件:")
        for file_path in results["fixed_file_list"][:15]:  # 显示前15个
            print(f"   - {file_path}")
        if len(results["fixed_file_list"]) > 15:
            print(f"   ... 还有 {len(results['fixed_file_list']) - 15} 个文件")

    print(f"\n💡 下一步建议:")
    print("   1. 运行 'python tools/code_quality_checker.py' 检查优化效果")
    print("   2. 安装并配置pre-commit:")
    print("      pip install pre-commit")
    print("      pre-commit install")
    print("   3. 运行所有格式化工具:")
    print("      black --line-length=120 .")
    print("      isort --profile=black .")
    print("   4. 验证测试仍然通过:")
    print("      python -m pytest test_case/Login/test_login.py -v")


if __name__ == "__main__":
    main()
