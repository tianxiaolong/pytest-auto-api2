#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auto Fix Code Module

This module provides auto fix code functionality.
"""

"""
自动修复代码规范问题脚本

@Time   : 2023-12-20
@Author : txl
"""
import os
import re
from pathlib import Path
from typing import List


class CodeAutoFixer:
    """代码自动修复器"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.fixed_files = []

    def fix_all(self) -> None:
        """执行所有修复"""
        print("开始自动修复代码规范问题...")

        # 修复编码声明
        self._fix_encoding_declarations()

        # 修复变量命名
        self._fix_variable_naming()

        # 修复导入顺序
        self._fix_import_order()

        # 生成报告
        self._print_summary()

    def _fix_encoding_declarations(self) -> None:
        """修复编码声明"""
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

                # 检查是否缺少编码声明
                has_encoding = any("coding" in line for line in lines[:3])
                has_shebang = lines[0].startswith("#!")

                if not has_encoding:
                    # 添加编码声明
                    if has_shebang:
                        # 在shebang后添加编码声明
                        lines.insert(1, "# -*- coding: utf-8 -*-\n")
                    else:
                        # 在文件开头添加编码声明
                        lines.insert(0, "#!/usr/bin/env python\n")
                        lines.insert(1, "# -*- coding: utf-8 -*-\n")

                    # 写回文件
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.writelines(lines)

                    self.fixed_files.append(f"添加编码声明: {file_path}")

            except Exception as e:
                print(f"修复编码声明失败 {file_path}: {e}")

    def _fix_variable_naming(self) -> None:
        """修复变量命名问题"""
        # 修复测试用例中的 TestData -> test_data
        test_files = list(self.project_root.rglob("test_*.py"))

        for file_path in test_files:
            if any(part in str(file_path) for part in ["venv", "__pycache__", ".git"]):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # 替换 TestData 为 test_data
                if "TestData" in content:
                    new_content = content.replace("TestData", "test_data")

                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)

                    self.fixed_files.append(f"修复变量命名: {file_path}")

            except Exception as e:
                print(f"修复变量命名失败 {file_path}: {e}")

    def _fix_import_order(self) -> None:
        """修复导入顺序问题"""
        python_files = list(self.project_root.rglob("*.py"))

        for file_path in python_files:
            if any(part in str(file_path) for part in ["venv", "__pycache__", ".git"]):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                # 找到导入语句的范围
                import_start = -1
                import_end = -1

                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.startswith(("import ", "from ")) and not stripped.startswith("#"):
                        if import_start == -1:
                            import_start = i
                        import_end = i
                    elif import_start != -1 and stripped and not stripped.startswith("#"):
                        # 遇到非导入语句，结束导入区域
                        break

                if import_start == -1 or import_end == -1:
                    continue

                # 提取导入语句
                import_lines = lines[import_start : import_end + 1]
                other_lines = lines[:import_start] + lines[import_end + 1 :]

                # 分类导入语句
                stdlib_imports = []
                third_party_imports = []
                local_imports = []

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
                }

                for line in import_lines:
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#"):
                        continue

                    if stripped.startswith("from "):
                        module = stripped.split()[1].split(".")[0]
                    else:
                        module = stripped.split()[1].split(".")[0]

                    if module in stdlib_modules:
                        stdlib_imports.append(line)
                    elif module.startswith(".") or any(local in module for local in ["utils", "common", "test_case"]):
                        local_imports.append(line)
                    else:
                        third_party_imports.append(line)

                # 重新排序导入
                sorted_imports = []
                if stdlib_imports:
                    sorted_imports.extend(stdlib_imports)
                    sorted_imports.append("\n")
                if third_party_imports:
                    sorted_imports.extend(third_party_imports)
                    sorted_imports.append("\n")
                if local_imports:
                    sorted_imports.extend(local_imports)
                    sorted_imports.append("\n")

                # 重新组合文件内容
                new_lines = other_lines[:import_start] + sorted_imports + other_lines[import_start:]

                # 检查是否有变化
                if new_lines != lines:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.writelines(new_lines)

                    self.fixed_files.append(f"修复导入顺序: {file_path}")

            except Exception as e:
                print(f"修复导入顺序失败 {file_path}: {e}")

    def _print_summary(self) -> None:
        """打印修复总结"""
        print("\n" + "=" * 60)
        print("代码自动修复完成")
        print("=" * 60)

        if not self.fixed_files:
            print("✅ 没有需要修复的问题。")
            return

        print(f"🔧 总共修复了 {len(self.fixed_files)} 个问题：\n")

        for fix in self.fixed_files:
            print(f"   ✓ {fix}")

        print("\n🎉 修复完成！建议重新运行代码质量检查验证结果。")


def main():
    """主函数"""
    fixer = CodeAutoFixer()
    fixer.fix_all()


if __name__ == "__main__":
    main()
