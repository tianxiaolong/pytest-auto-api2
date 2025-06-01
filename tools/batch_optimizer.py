#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path
import os
import re
import sys

from typing import List, Dict, Any
import subprocess

"""
批量代码优化脚本
一次性解决大部分代码质量问题

@Time   : 2023-12-20
@Author : txl
"""


class BatchOptimizer:
    """批量优化器"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.stats = {
            "files_processed": 0,
            "imports_fixed": 0,
            "docstrings_added": 0,
            "security_comments_added": 0,
            "formatting_applied": 0,
        }

    def fix_import_issues(self, file_path: Path) -> bool:
        """修复导入问题"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")
            new_lines = []
            imports_section = []
            in_imports = False
            imports_done = False

            # 找到文档字符串结束位置
            doc_end = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('"""') and '"""' in line[line.find('"""') + 3:]:
                    doc_end = i + 1
                    break
                elif line.strip().startswith('"""'):
                    for j in range(i + 1, len(lines)):
                        if '"""' in lines[j]:
                            doc_end = j + 1
                            break
                    break

            # 重新组织代码
            for i, line in enumerate(lines):
                if i < doc_end:
                    new_lines.append(line)
                elif not imports_done and (line.strip().startswith("import ") or line.strip().startswith("from ")):
                    if not in_imports:
                        in_imports = True
                    imports_section.append(line)
                elif in_imports and (not line.strip() or line.strip().startswith("#")):
                    imports_section.append(line)
                else:
                    if in_imports:
                        # 整理导入部分
                        stdlib_imports = []
                        third_party_imports = []
                        local_imports = []

                        for imp_line in imports_section:
                            if imp_line.strip().startswith(("import ", "from ")):
                                if any(mod in imp_line for mod in ["utils", "common", "test_case", "."]):
                                    local_imports.append(imp_line)
                                elif any(
                                        mod in imp_line for mod in ["os", "sys", "time", "json", "ast", "re", "pathlib"]
                                ):
                                    stdlib_imports.append(imp_line)
                                else:
                                    third_party_imports.append(imp_line)

                        # 添加整理后的导入
                        if stdlib_imports:
                            new_lines.extend(sorted(set(stdlib_imports)))
                            new_lines.append("")
                        if third_party_imports:
                            new_lines.extend(sorted(set(third_party_imports)))
                            new_lines.append("")
                        if local_imports:
                            new_lines.extend(sorted(set(local_imports)))
                            new_lines.append("")

                        imports_done = True
                        in_imports = False

                    new_lines.append(line)

            new_content = "\n".join(new_lines)
            if new_content != content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                self.stats["imports_fixed"] += 1
                return True

            return False

        except Exception as e:
            print(f"修复导入失败 {file_path}: {e}")
            return False

    def add_module_docstring(self, file_path: Path) -> bool:
        """添加模块文档字符串"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 检查是否已有模块文档字符串
            if content.strip().startswith('"""') or content.strip().startswith("'''"):
                return False

            lines = content.split("\n")

            # 找到插入位置（编码声明之后）
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.strip().startswith("#") and ("coding" in line or "encoding" in line):
                    insert_pos = i + 1
                    break

            # 生成文档字符串
            module_name = file_path.stem.replace("_", " ").title()
            docstring = f'"""\n{module_name} Module\n\nThis module provides {module_name.lower()} functionality.\n"""\n'

            lines.insert(insert_pos, docstring)

            new_content = "\n".join(lines)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            self.stats["docstrings_added"] += 1
            return True

        except Exception as e:
            print(f"添加文档字符串失败 {file_path}: {e}")
            return False

    def add_security_comments(self, file_path: Path) -> bool:
        """添加安全注释"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # 为可能的安全问题添加注释
            security_patterns = [
                (r'(password\s*=\s*["\'][^"\']*["\'])', r"\1  # TODO: Use environment variable for security"),
                (r'(secret\s*=\s*["\'][^"\']*["\'])', r"\1  # TODO: Use environment variable for security"),
                (r'(api_key\s*=\s*["\'][^"\']*["\'])', r"\1  # TODO: Use environment variable for security"),
                (r'(token\s*=\s*["\'][^"\']*["\'])', r"\1  # TODO: Use environment variable for security"),
            ]

            for pattern, replacement in security_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                    self.stats["security_comments_added"] += 1

            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True

            return False

        except Exception as e:
            print(f"添加安全注释失败 {file_path}: {e}")
            return False

    def optimize_file(self, file_path: Path) -> bool:
        """优化单个文件"""
        if not file_path.suffix == ".py":
            return False

        if "venv" in str(file_path) or "__pycache__" in str(file_path):
            return False

        file_changed = False

        # 修复导入问题
        if self.fix_import_issues(file_path):
            file_changed = True

        # 添加模块文档字符串
        if self.add_module_docstring(file_path):
            file_changed = True

        # 添加安全注释
        if self.add_security_comments(file_path):
            file_changed = True

        if file_changed:
            self.stats["files_processed"] += 1

        return file_changed

    def run_external_formatters(self) -> Dict[str, str]:
        """运行外部格式化工具"""
        results = {}

        print("🔧 运行black格式化...")
        try:
            result = subprocess.run(
                ["black", "--line-length=120", "--target-version=py38", "."],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.project_root,
            )
            if result.returncode == 0:
                results["black"] = "成功"
                self.stats["formatting_applied"] += 1
            else:
                results["black"] = f"失败: {result.stderr}"
        except Exception as e:
            results["black"] = f"错误: {e}"

        print("🔧 运行isort整理导入...")
        try:
            result = subprocess.run(
                ["isort", "--profile=black", "--line-length=120", "."],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.project_root,
            )
            if result.returncode == 0:
                results["isort"] = "成功"
            else:
                results["isort"] = f"失败: {result.stderr}"
        except Exception as e:
            results["isort"] = f"错误: {e}"

        return results

    def optimize_project(self) -> Dict[str, Any]:
        """优化整个项目"""
        print("🚀 开始批量代码优化...")

        python_files = list(self.project_root.rglob("*.py"))
        total_files = len([f for f in python_files if "venv" not in str(f) and "__pycache__" not in str(f)])

        print(f"📊 找到 {total_files} 个Python文件")

        # 优化每个文件
        for py_file in python_files:
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            self.optimize_file(py_file)

        # 运行外部格式化工具
        formatter_results = self.run_external_formatters()

        return {"total_files": total_files, "stats": self.stats, "formatter_results": formatter_results}


def main():
    """主函数"""
    optimizer = BatchOptimizer()

    print("🚀 开始批量代码质量优化...")
    print("=" * 60)

    results = optimizer.optimize_project()

    print(f"\n📊 优化结果:")
    print(f"   总文件数: {results['total_files']}")
    print(f"   处理文件数: {results['stats']['files_processed']}")
    print(f"   导入修复: {results['stats']['imports_fixed']}")
    print(f"   文档字符串添加: {results['stats']['docstrings_added']}")
    print(f"   安全注释添加: {results['stats']['security_comments_added']}")
    print(f"   格式化应用: {results['stats']['formatting_applied']}")

    print(f"\n🔧 外部工具结果:")
    for tool, result in results["formatter_results"].items():
        print(f"   {tool}: {result}")

    print(f"\n💡 建议:")
    print("   1. 运行测试验证功能正常:")
    print("      python -m pytest test_case/Login/test_login.py -v")
    print("   2. 检查优化效果:")
    print("      python tools/code_quality_checker.py")
    print("   3. 如果有问题，可以使用git恢复:")
    print("      git checkout -- .")


if __name__ == "__main__":
    main()
