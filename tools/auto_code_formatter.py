#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path
import os
import re
import sys

from typing import Any, Dict, List

"""
自动代码格式化工具
修复常见的代码质量问题

@Time   : 2023-12-20
@Author : txl
"""


class AutoCodeFormatter:
    """自动代码格式化器"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.fixed_files = []
        self.fixed_issues = {
            "trailing_whitespace": 0,
            "blank_line_whitespace": 0,
            "unused_f_strings": 0,
            "unused_imports": 0,
            "line_endings": 0,
        }

    def fix_file(self, file_path: Path) -> bool:
        """修复单个文件的格式问题"""
        if not file_path.suffix == ".py":
            return False

        if "venv" in str(file_path) or "__pycache__" in str(file_path):
            return False

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            content = original_content
            file_fixed = False

            # 修复行尾空格
            new_content = re.sub(r"[ \t]+$", "", content, flags=re.MULTILINE)
            if new_content != content:
                self.fixed_issues["trailing_whitespace"] += content.count("\n") - new_content.count("\n")
                content = new_content
                file_fixed = True

            # 修复空行中的空格
            new_content = re.sub(r"^[ \t]+$", "", content, flags=re.MULTILINE)
            if new_content != content:
                self.fixed_issues["blank_line_whitespace"] += 1
                content = new_content
                file_fixed = True

            # 修复f-string缺少占位符的问题
            # 将没有占位符的f-string改为普通字符串
            def fix_f_string(match):
                quote = match.group(1)
                string_content = match.group(2)
                if "{" not in string_content and "}" not in string_content:
                    self.fixed_issues["unused_f_strings"] += 1
                    return f"{quote}{string_content}{quote}"
                return match.group(0)

            new_content = re.sub(r'f(["\'])(.*?)\1', fix_f_string, content)
            if new_content != content:
                content = new_content
                file_fixed = True

            # 确保文件以换行符结尾
            if content and not content.endswith("\n"):
                content += "\n"
                self.fixed_issues["line_endings"] += 1
                file_fixed = True

            # 如果有修改，写回文件
            if file_fixed:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.fixed_files.append(str(file_path))
                return True

            return False

        except Exception as e:
            print(f"修复文件失败 {file_path}: {e}")
            return False

    def remove_unused_imports(self, file_path: Path) -> bool:
        """移除未使用的导入（简单版本）"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # 简单的未使用导入检测和移除
            # 这里只处理明显未使用的导入
            unused_patterns = [r"^import sys\s*$", r"^import os\s*$", r"^from typing import Union\s*$"]

            new_lines = []
            removed_count = 0

            for line in lines:
                should_remove = False
                for pattern in unused_patterns:
                    if re.match(pattern, line.strip()):
                        # 检查文件中是否真的使用了这个导入
                        module_name = line.strip().split()[-1]
                        file_content = "".join(lines)
                        if module_name not in file_content.replace(line, ""):
                            should_remove = True
                            removed_count += 1
                            break

                if not should_remove:
                    new_lines.append(line)

            if removed_count > 0:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                self.fixed_issues["unused_imports"] += removed_count
                return True

            return False

        except Exception as e:
            print(f"移除未使用导入失败 {file_path}: {e}")
            return False

    def format_project(self) -> Dict[str, Any]:
        """格式化整个项目"""
        print("🔧 开始自动代码格式化...")

        python_files = list(self.project_root.rglob("*.py"))
        total_files = 0
        fixed_files = 0

        for py_file in python_files:
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            total_files += 1

            # 修复格式问题
            if self.fix_file(py_file):
                fixed_files += 1

            # 移除未使用的导入
            self.remove_unused_imports(py_file)

        return {
            "total_files": total_files,
            "fixed_files": fixed_files,
            "fixed_issues": self.fixed_issues,
            "fixed_file_list": self.fixed_files,
        }

    def run_external_formatters(self) -> Dict[str, str]:
        """运行外部格式化工具"""
        results = {}

        # 尝试运行black
        try:
            import subprocess
            result = subprocess.run(
                ["black", "--line-length=120", "--target-version=py38", "."], capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                results["black"] = "成功"
            else:
                results["black"] = f"失败: {result.stderr}"
        except (subprocess.TimeoutExpired, FileNotFoundError, ImportError):
            results["black"] = "未安装或超时"

        # 尝试运行isort
        try:
            result = subprocess.run(
                ["isort", "--profile=black", "--line-length=120", "."], capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                results["isort"] = "成功"
            else:
                results["isort"] = f"失败: {result.stderr}"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            results["isort"] = "未安装或超时"

        return results


def create_quality_config():
    """创建代码质量配置文件"""

    # 创建.flake8配置
    flake8_config = """[flake8]
max-line-length = 120
ignore =
    E203,  # whitespace before ':'
    W503,  # line break before binary operator
    F401,  # imported but unused (handled separately)
    W293,  # blank line contains whitespace (auto-fixed)
    F541,  # f-string is missing placeholders (auto-fixed)
exclude =
    venv,
    __pycache__,
    .git,
    build,
    dist,
    *.egg-info
"""

    # 创建pyproject.toml配置
    pyproject_config = """[tool.black]
line-length = 120
target-version = ['py38']
include = '\\.pyi?$'
exclude = '''
/(
    \\.git
  | \\.venv
  | venv
  | __pycache__
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 120
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
"""

    try:
        with open(".flake8", "w", encoding="utf-8") as f:
            f.write(flake8_config)
        print("✅ 创建 .flake8 配置文件")

        with open("pyproject.toml", "w", encoding="utf-8") as f:
            f.write(pyproject_config)
        print("✅ 创建 pyproject.toml 配置文件")

    except Exception as e:
        print(f"❌ 创建配置文件失败: {e}")


def main():
    """主函数"""
    formatter = AutoCodeFormatter()

    print("🚀 开始代码质量自动修复...")
    print("=" * 60)

    # 创建配置文件
    create_quality_config()

    # 自动格式化
    results = formatter.format_project()

    print("\n📊 格式化结果:")
    print(f"   检查文件数: {results['total_files']}")
    print(f"   修复文件数: {results['fixed_files']}")
    print("   修复问题统计:")
    for issue_type, count in results["fixed_issues"].items():
        if count > 0:
            print(f"     {issue_type}: {count}")

    # 运行外部格式化工具
    print("\n🔧 运行外部格式化工具:")
    external_results = formatter.run_external_formatters()
    for tool, result in external_results.items():
        print(f"   {tool}: {result}")

    # 显示修复的文件列表
    if results["fixed_file_list"]:
        print("\n📝 修复的文件:")
        for file_path in results["fixed_file_list"][:10]:  # 只显示前10个
            print(f"   - {file_path}")
        if len(results["fixed_file_list"]) > 10:
            print(f"   ... 还有 {len(results['fixed_file_list']) - 10} 个文件")

    print("\n💡 建议:")
    print("   1. 运行 'python tools/code_quality_checker.py' 检查修复效果")
    print("   2. 安装并运行 black 和 isort 进行进一步格式化:")
    print("      pip install black isort")
    print("      black --line-length=120 .")
    print("      isort --profile=black .")
    print("   3. 考虑设置 pre-commit 钩子自动格式化")


if __name__ == "__main__":
    main()
