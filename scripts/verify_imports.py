#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verify Imports Module

This module provides verify imports functionality.
"""

"""
导入验证脚本
验证所有导入修复是否正确，确保项目可以正常运行

@Time   : 2023-12-20
@Author : txl
"""
import importlib
from pathlib import Path
from typing import Dict, List


class ImportVerifier:
    """
    导入验证器

    验证项目中所有模块的导入是否正确。
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.success_imports = []
        self.failed_imports = []

    def verify_all_imports(self) -> Dict:
        """
        验证所有导入

        Returns:
            验证结果字典
        """
        print("🔍 开始验证项目导入...")

        # 关键模块列表
        key_modules = [
            "utils.read_files_tools.data_driver_control",
            "utils.read_files_tools.excel_control",
            "utils.read_files_tools.yaml_control",
            "utils.read_files_tools.get_yaml_data_analysis",
            "test_case.Login.test_login",
            "test_case.UserInfo.test_get_user_info",
            "test_case.Collect.test_collect_addtool",
        ]

        for module_name in key_modules:
            self._verify_single_module(module_name)

        return self._generate_report()

    def _verify_single_module(self, module_name: str) -> None:
        """
        验证单个模块的导入

        Args:
            module_name: 模块名称
        """
        try:
            # 尝试导入模块
            module = importlib.import_module(module_name)

            # 检查关键属性/函数是否存在
            self._check_module_attributes(module, module_name)

            self.success_imports.append({"module": module_name, "status": "success"})
            print(f"✅ {module_name}")

        except ImportError as e:
            self.failed_imports.append({"module": module_name, "error": f"ImportError: {e}", "type": "import_error"})
            print(f"❌ {module_name}: ImportError - {e}")

        except AttributeError as e:
            self.failed_imports.append(
                {"module": module_name, "error": f"AttributeError: {e}", "type": "attribute_error"}
            )
            print(f"⚠️  {module_name}: AttributeError - {e}")

        except Exception as e:
            self.failed_imports.append({"module": module_name, "error": f"Other Error: {e}", "type": "other_error"})
            print(f"❌ {module_name}: {type(e).__name__} - {e}")

    def _check_module_attributes(self, module, module_name: str) -> None:
        """
        检查模块的关键属性

        Args:
            module: 导入的模块对象
            module_name: 模块名称
        """
        # 根据模块类型检查不同的属性
        if "data_driver_control" in module_name:
            required_attrs = ["get_test_data", "DataDriverManager", "switch_data_driver"]
            for attr in required_attrs:
                if not hasattr(module, attr):
                    raise AttributeError(f"Missing required attribute: {attr}")

        elif "excel_control" in module_name:
            required_attrs = ["ExcelDataReader", "ExcelDataProcessor"]
            for attr in required_attrs:
                if not hasattr(module, attr):
                    raise AttributeError(f"Missing required attribute: {attr}")

        elif "test_" in module_name:
            # 检查测试模块是否有test_data变量
            if not hasattr(module, "test_data"):
                raise AttributeError("Missing test_data variable")

    def verify_data_driver_functionality(self) -> Dict:
        """
        验证数据驱动功能

        Returns:
            功能验证结果
        """
        print("\n🧪 验证数据驱动功能...")

        results = {"yaml_driver": False, "excel_driver": False, "switch_function": False, "errors": []}

        try:
            from utils.read_files_tools.data_driver_control import data_driver, get_test_data, switch_data_driver

            # 测试YAML数据驱动
            try:
                switch_data_driver("yaml")
                modules = data_driver.list_available_modules()
                if modules:
                    test_data = get_test_data(modules[0])
                    results["yaml_driver"] = True
                    print("✅ YAML数据驱动功能正常")
                else:
                    print("⚠️  没有找到YAML数据模块")
            except Exception as e:
                results["errors"].append(f"YAML数据驱动测试失败: {e}")
                print(f"❌ YAML数据驱动测试失败: {e}")

            # 测试Excel数据驱动
            try:
                switch_data_driver("excel")
                results["excel_driver"] = True
                results["switch_function"] = True
                print("✅ Excel数据驱动切换功能正常")
            except ImportError as e:
                results["errors"].append(f"Excel数据驱动需要安装依赖: {e}")
                print(f"⚠️  Excel数据驱动需要安装依赖: {e}")
            except Exception as e:
                results["errors"].append(f"Excel数据驱动测试失败: {e}")
                print(f"❌ Excel数据驱动测试失败: {e}")

        except Exception as e:
            results["errors"].append(f"数据驱动模块导入失败: {e}")
            print(f"❌ 数据驱动模块导入失败: {e}")

        return results

    def _generate_report(self) -> Dict:
        """
        生成验证报告

        Returns:
            验证报告字典
        """
        return {
            "total_modules": len(self.success_imports) + len(self.failed_imports),
            "success_count": len(self.success_imports),
            "failed_count": len(self.failed_imports),
            "success_imports": self.success_imports,
            "failed_imports": self.failed_imports,
        }

    def print_summary(self) -> None:
        """打印验证摘要"""
        report = self._generate_report()
        functionality_report = self.verify_data_driver_functionality()

        print("\n" + "=" * 60)
        print("📋 导入验证摘要")
        print("=" * 60)

        print("\n📊 模块导入统计:")
        print(f"   总模块数: {report['total_modules']}")
        print(f"   成功导入: {report['success_count']}")
        print(f"   导入失败: {report['failed_count']}")

        if report["failed_imports"]:
            print("\n❌ 导入失败的模块:")
            for failed in report["failed_imports"]:
                print(f"   📄 {failed['module']}")
                print(f"      错误: {failed['error']}")

        print("\n🧪 功能验证结果:")
        print(f"   YAML数据驱动: {'✅' if functionality_report['yaml_driver'] else '❌'}")
        print(f"   Excel数据驱动: {'✅' if functionality_report['excel_driver'] else '❌'}")
        print(f"   切换功能: {'✅' if functionality_report['switch_function'] else '❌'}")

        if functionality_report["errors"]:
            print("\n⚠️  功能验证错误:")
            for error in functionality_report["errors"]:
                print(f"   - {error}")

        # 总体评估
        success_rate = report["success_count"] / report["total_modules"] * 100
        print("\n🎯 总体评估:")
        print(f"   导入成功率: {success_rate:.1f}%")

        if success_rate >= 90:
            print("   状态: ✅ 优秀 - 项目导入状态良好")
        elif success_rate >= 70:
            print("   状态: ⚠️  良好 - 有少量问题需要修复")
        else:
            print("   状态: ❌ 需要修复 - 存在较多导入问题")

        print("\n💡 建议:")
        if report["failed_imports"]:
            print("   1. 修复导入失败的模块")
            print("   2. 检查文件路径和模块名称")
        if not functionality_report["excel_driver"]:
            print("   3. 安装Excel支持库: pip install pandas openpyxl")
        print("   4. 运行测试验证功能正常")


def main():
    """主函数"""
    verifier = ImportVerifier()
    verifier.verify_all_imports()
    verifier.print_summary()


if __name__ == "__main__":
    main()
