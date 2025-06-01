#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Update Test Imports Module

This module provides update test imports functionality.
"""

"""
测试用例导入更新脚本
批量更新所有测试用例文件的导入语句，使用新的数据驱动接口

@Time   : 2023-12-20
@Author : txl
"""
import re
from pathlib import Path
from typing import Dict, List


class TestImportUpdater:
    """
    测试导入更新器

    批量更新测试用例文件中的导入语句和数据获取方式。
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.updated_files = []
        self.errors = []

        # 模块名映射（文件路径到模块名）
        self.module_mapping = {"Login": "Login", "UserInfo": "UserInfo", "Collect": "Collect", "Tool": "Tool"}

    def update_all_test_files(self) -> None:
        """更新所有测试文件"""
        print("🔄 开始更新测试用例导入...")

        test_case_dir = self.project_root / "test_case"

        # 查找所有测试文件
        test_files = list(test_case_dir.rglob("test_*.py"))

        for test_file in test_files:
            # 跳过示例文件
            if "example" in test_file.name:
                continue

            try:
                self._update_single_file(test_file)
            except Exception as e:
                self.errors.append({"file": str(test_file), "error": str(e)})

        self._print_summary()

    def _update_single_file(self, file_path: Path) -> None:
        """
        更新单个测试文件

        Args:
            file_path: 测试文件路径
        """
        # 从文件路径推断模块名
        module_name = self._infer_module_name(file_path)

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # 1. 更新导入语句
        content = self._update_imports(content)

        # 2. 更新数据获取方式
        content = self._update_data_acquisition(content, module_name)

        # 3. 更新注释中的数据来源说明
        content = self._update_data_source_comments(content, module_name)

        # 如果内容有变化，写回文件
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            self.updated_files.append(str(file_path))
            print(f"✅ 更新文件: {file_path}")

    def _infer_module_name(self, file_path: Path) -> str:
        """
        从文件路径推断模块名

        Args:
            file_path: 文件路径

        Returns:
            模块名称
        """
        # 从父目录名推断
        parent_dir = file_path.parent.name
        if parent_dir in self.module_mapping:
            return self.module_mapping[parent_dir]

        # 从文件名推断
        file_name = file_path.stem
        if "login" in file_name.lower():
            return "Login"
        elif "user" in file_name.lower():
            return "UserInfo"
        elif "collect" in file_name.lower():
            return "Collect"
        elif "tool" in file_name.lower():
            return "Tool"

        # 默认返回父目录名的首字母大写
        return parent_dir.capitalize()

    def _update_imports(self, content: str) -> str:
        """
        更新导入语句

        Args:
            content: 文件内容

        Returns:
            更新后的内容
        """
        # 替换旧的导入
        patterns = [
            (
                r"from utils\.read_files_tools\.get_yaml_data_analysis import GetTestCase",
                "from utils.read_files_tools.data_driver_control import get_test_data",
            ),
        ]

        for old_pattern, new_import in patterns:
            content = re.sub(old_pattern, new_import, content)

        return content

    def _update_data_acquisition(self, content: str, module_name: str) -> str:
        """
        更新数据获取方式

        Args:
            content: 文件内容
            module_name: 模块名称

        Returns:
            更新后的内容
        """
        # 替换数据获取方式
        patterns = [
            # 替换 case_id 和 GetTestCase.case_data 的模式
            (
                r"case_id = \[.*?\]\s*\ntest_data = GetTestCase\.case_data\(case_id\)",
                "# 使用新的数据驱动接口获取测试数据\n# 注意：需要根据实际情况指定具体的文件名\ntest_data = get_test_data('{module_name}', 'specific_file.yaml')",
            ),
            # 如果没有case_id，直接替换GetTestCase.case_data
            (r"test_data = GetTestCase\.case_data\([^)]+\)", "# 注意：需要根据实际情况指定具体的文件名\ntest_data = get_test_data('{module_name}', 'specific_file.yaml')"),
        ]

        for old_pattern, new_code in patterns:
            content = re.sub(old_pattern, new_code, content, flags=re.DOTALL)

        return content

    def _update_data_source_comments(self, content: str, module_name: str) -> str:
        """
        更新注释中的数据来源说明

        Args:
            content: 文件内容
            module_name: 模块名称

        Returns:
            更新后的内容
        """
        # 更新注释中的数据来源
        old_patterns = [
            r"测试数据来源：data/.*?\.yaml",
            r"数据来源：data/.*?\.yaml",
        ]

        new_comment = f"测试数据来源：data/yaml_data/项目名/{module_name}/ (支持YAML和Excel数据驱动)"

        for pattern in old_patterns:
            content = re.sub(pattern, new_comment, content)

        return content

    def _print_summary(self) -> None:
        """打印更新摘要"""
        print("\n" + "=" * 60)
        print("📋 测试用例导入更新摘要")
        print("=" * 60)

        print(f"\n✅ 成功更新文件数: {len(self.updated_files)}")
        if self.updated_files:
            for file_path in self.updated_files:
                print(f"   📄 {file_path}")

        if self.errors:
            print(f"\n❌ 更新失败文件数: {len(self.errors)}")
            for error in self.errors:
                print(f"   📄 {error['file']}")
                print(f"      错误: {error['error']}")

        print("\n💡 更新内容:")
        print("   1. 导入语句: GetTestCase → get_test_data")
        print("   2. 数据获取: case_id方式 → 模块名方式")
        print("   3. 注释更新: 数据来源路径更新")

        print("\n📋 后续步骤:")
        print("   1. 检查更新后的文件是否正确")
        print("   2. 运行测试验证功能正常")
        print("   3. 根据需要调整数据驱动类型")


def main():
    """主函数"""
    updater = TestImportUpdater()
    updater.update_all_test_files()


if __name__ == "__main__":
    main()
