#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Restructure Data Directory Module

This module provides restructure data directory functionality.
"""

"""
数据目录重构脚本
将现有的data目录重构为 data/yaml_data/项目名/模块名 的结构

@Time   : 2023-12-20
@Author : txl
"""
import shutil
from pathlib import Path
from typing import Dict, List

import yaml

from common.setting import ensure_path_sep
from utils import config


class DataDirectoryRestructure:
    """
    数据目录重构器

    负责将现有的data目录重构为新的层级结构：
    data/yaml_data/项目名/模块名
    """

    def __init__(self):
        self.old_data_path = Path("data")
        self.new_data_path = Path("data")
        self.project_name = config.project_name or "default_project"

    def create_new_structure(self) -> None:
        """
        创建新的目录结构
        """
        # 创建新的目录结构
        yaml_data_path = self.new_data_path / "yaml_data" / self.project_name
        excel_data_path = self.new_data_path / "excel_data" / self.project_name

        # 创建目录
        yaml_data_path.mkdir(parents=True, exist_ok=True)
        excel_data_path.mkdir(parents=True, exist_ok=True)

        print("✅ 创建目录结构:")
        print(f"   📁 {yaml_data_path}")
        print(f"   📁 {excel_data_path}")

    def migrate_existing_data(self) -> None:
        """
        迁移现有的YAML数据文件
        """
        if not self.old_data_path.exists():
            print("❌ 原data目录不存在")
            return

        yaml_files = list(self.old_data_path.glob("**/*.yaml")) + list(self.old_data_path.glob("**/*.yml"))

        if not yaml_files:
            print("ℹ️  没有找到需要迁移的YAML文件")
            return

        new_yaml_path = self.new_data_path / "yaml_data" / self.project_name

        for yaml_file in yaml_files:
            # 根据文件路径确定模块名
            relative_path = yaml_file.relative_to(self.old_data_path)

            if len(relative_path.parts) > 1:
                # 如果文件在子目录中，使用子目录名作为模块名
                module_name = relative_path.parts[0]
            else:
                # 如果文件在根目录，根据文件名推断模块名
                module_name = self.infer_module_name(yaml_file.stem)

            # 创建模块目录
            module_path = new_yaml_path / module_name
            module_path.mkdir(exist_ok=True)

            # 复制文件
            new_file_path = module_path / yaml_file.name
            shutil.copy2(yaml_file, new_file_path)

            print(f"📄 迁移文件: {yaml_file} -> {new_file_path}")

    def infer_module_name(self, filename: str) -> str:
        """
        根据文件名推断模块名

        Args:
            filename: 文件名（不含扩展名）

        Returns:
            推断的模块名
        """
        # 常见的模块名映射
        module_mapping = {
            "login": "Login",
            "user": "UserInfo",
            "collect": "Collect",
            "tool": "Tool",
            "api": "API",
            "test": "Test",
        }

        filename_lower = filename.lower()

        for key, module in module_mapping.items():
            if key in filename_lower:
                return module

        # 如果没有匹配，使用首字母大写的文件名
        return filename.capitalize()

    def create_sample_excel_data(self) -> None:
        """
        创建示例Excel数据文件结构
        """
        excel_path = self.new_data_path / "excel_data" / self.project_name

        # 创建示例模块目录
        sample_modules = ["Login", "UserInfo", "Collect"]

        for module in sample_modules:
            module_path = excel_path / module
            module_path.mkdir(exist_ok=True)

            # 创建示例Excel文件说明
            readme_path = module_path / "README.md"
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(
                    """# {module} 模块 Excel 数据说明

## Excel 文件格式要求

### 1. 文件命名
- 文件名格式: `{module.lower()}_test_data.xlsx`
- 每个模块一个Excel文件

### 2. Sheet结构
- **case_common**: 公共配置信息
- **test_cases**: 测试用例数据

### 3. 列结构说明
| 列名 | 说明 | 必填 | 示例 |
|------|------|------|------|
| case_id | 用例ID | 是 | login_001 |
| detail | 用例描述 | 是 | 正常登录测试 |
| url | 接口地址 | 是 | /api/login |
| method | 请求方法 | 是 | POST |
| headers | 请求头 | 否 | {{"Content-Type": "application/json"}} |
| requestType | 请求类型 | 是 | json |
| data | 请求数据 | 否 | {{"username": "test", "password": "123456"}} |
| assert | 断言配置 | 是 | {{"status_code": 200}} |
| is_run | 是否执行 | 否 | True |

### 4. 使用方式
在配置文件中设置 `data_driver_type: excel` 即可使用Excel数据驱动。
"""
                )

            print(f"📁 创建模块目录: {module_path}")

    def update_config_example(self) -> None:
        """
        更新配置文件示例
        """
        config_example = """
# 数据驱动配置示例
data_driver:
  # 数据驱动类型: yaml 或 excel
  type: yaml

  # 数据文件路径配置
  yaml_data_path: data/yaml_data
  excel_data_path: data/excel_data

  # 项目名称（用于数据文件路径）
  project_name: ${project_name}
"""

        with open("config_data_driver_example.yaml", "w", encoding="utf-8") as f:
            f.write(config_example)

        print("📄 创建配置示例文件: config_data_driver_example.yaml")

    def run_restructure(self) -> None:
        """
        执行完整的重构流程
        """
        print("🚀 开始数据目录重构...")
        print("=" * 50)

        # 1. 创建新目录结构
        self.create_new_structure()
        print()

        # 2. 迁移现有数据
        print("📦 迁移现有YAML数据...")
        self.migrate_existing_data()
        print()

        # 3. 创建Excel示例
        print("📊 创建Excel数据示例...")
        self.create_sample_excel_data()
        print()

        # 4. 更新配置示例
        print("⚙️  创建配置示例...")
        self.update_config_example()
        print()

        print("✅ 数据目录重构完成！")
        print("=" * 50)
        print("📋 后续步骤:")
        print("1. 检查迁移后的YAML文件")
        print("2. 根据需要调整模块分类")
        print("3. 配置数据驱动类型")
        print("4. 创建Excel测试数据（如需要）")


def main():
    """主函数"""
    restructure = DataDirectoryRestructure()
    restructure.run_restructure()


if __name__ == "__main__":
    main()
