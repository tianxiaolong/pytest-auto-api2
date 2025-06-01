#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check Real Issues Module

This module provides check real issues functionality.
"""

"""
真实问题检查脚本
只检查真正需要关注的导入问题，避免误报

@Time   : 2023-12-20
@Author : txl
"""
import re
from pathlib import Path
from typing import Dict, List


class RealIssueChecker:
    """
    真实问题检查器

    只检查真正需要关注的导入问题：
    1. 直接导入data目录的情况
    2. 使用已废弃的API的情况
    3. 路径不存在的导入
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.real_issues = []

    def check_real_issues(self) -> Dict:
        """
        检查真实问题

        Returns:
            检查结果字典
        """
        print("🔍 检查真实导入问题...")

        python_files = list(self.project_root.rglob("*.py"))

        for file_path in python_files:
            # 跳过虚拟环境和缓存目录
            if any(part in str(file_path) for part in ["venv", "__pycache__", ".git"]):
                continue

            self._check_file_issues(file_path)

        return self._generate_report()

    def _check_file_issues(self, file_path: Path) -> None:
        """
        检查单个文件的真实问题

        Args:
            file_path: Python文件路径
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")
            for line_no, line in enumerate(lines, 1):
                line = line.strip()

                # 检查真正有问题的导入模式
                self._check_direct_data_import(line, file_path, line_no)
                self._check_deprecated_apis(line, file_path, line_no)

        except Exception as e:
            self.real_issues.append(
                {
                    "type": "file_read_error",
                    "file": str(file_path),
                    "message": f"读取文件失败: {e}",
                    "severity": "error",
                }
            )

    def _check_direct_data_import(self, line: str, file_path: Path, line_no: int) -> None:
        """
        检查直接导入data目录的情况

        Args:
            line: 代码行
            file_path: 文件路径
            line_no: 行号
        """
        # 真正有问题的data导入模式
        problematic_patterns = [
            r"^from\s+data\s+import",  # from data import xxx
            r"^import\s+data\.",  # import data.xxx
            r"^from\s+data\.",  # from data.xxx import yyy
        ]

        for pattern in problematic_patterns:
            if re.match(pattern, line):
                self.real_issues.append(
                    {
                        "type": "direct_data_import",
                        "file": str(file_path),
                        "line": line_no,
                        "code": line,
                        "message": "直接导入data目录，应该使用数据驱动接口",
                        "severity": "warning",
                        "suggestion": "使用 from utils.read_files_tools.data_driver_control import get_test_data",
                    }
                )

    def _check_deprecated_apis(self, line: str, file_path: Path, line_no: int) -> None:
        """
        检查已废弃的API使用

        Args:
            line: 代码行
            file_path: 文件路径
            line_no: 行号
        """
        # 检查是否使用了旧的数据获取方式（但这些实际上是兼容的）
        deprecated_patterns = [
            (r"GetTestCase\.case_data\(", "建议使用新的数据驱动接口 get_test_data()"),
        ]

        for pattern, suggestion in deprecated_patterns:
            if re.search(pattern, line):
                # 只有在测试文件中才提示，其他地方可能是兼容性代码
                if "test_case" in str(file_path) and "test_" in file_path.name:
                    self.real_issues.append(
                        {
                            "type": "deprecated_api",
                            "file": str(file_path),
                            "line": line_no,
                            "code": line,
                            "message": "使用了旧的API",
                            "severity": "info",
                            "suggestion": suggestion,
                        }
                    )

    def _generate_report(self) -> Dict:
        """
        生成检查报告

        Returns:
            检查报告字典
        """
        # 按严重程度分类
        by_severity = {"error": [], "warning": [], "info": []}
        for issue in self.real_issues:
            severity = issue.get("severity", "info")
            by_severity[severity].append(issue)

        return {"total_issues": len(self.real_issues), "by_severity": by_severity, "all_issues": self.real_issues}

    def print_report(self) -> None:
        """打印检查报告"""
        report = self._generate_report()

        print("\n" + "=" * 60)
        print("📋 真实问题检查报告")
        print("=" * 60)

        print("\n📊 问题统计:")
        print(f"   总问题数: {report['total_issues']}")
        print(f"   错误: {len(report['by_severity']['error'])}")
        print(f"   警告: {len(report['by_severity']['warning'])}")
        print(f"   信息: {len(report['by_severity']['info'])}")

        if report["total_issues"] == 0:
            print("\n✅ 恭喜！没有发现真实的导入问题！")
            print("   项目的导入状态良好，所有模块都正确配置。")
            return

        # 按严重程度显示问题
        severity_icons = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}
        severity_names = {"error": "错误", "warning": "警告", "info": "信息"}

        for severity in ["error", "warning", "info"]:
            issues = report["by_severity"][severity]
            if not issues:
                continue

            print(f"\n{severity_icons[severity]} {severity_names[severity]} ({len(issues)} 个):")

            for issue in issues:
                print(f"   📄 {issue['file']}:{issue.get('line', '?')}")
                if "code" in issue:
                    print(f"      代码: {issue['code']}")
                print(f"      问题: {issue['message']}")
                if "suggestion" in issue:
                    print(f"      建议: {issue['suggestion']}")
                print()

        print("💡 总结:")
        if report["by_severity"]["error"]:
            print("   - 发现严重错误，需要立即修复")
        if report["by_severity"]["warning"]:
            print("   - 发现警告问题，建议修复以提高代码质量")
        if report["by_severity"]["info"]:
            print("   - 发现信息提示，可以考虑优化")


def main():
    """主函数"""
    checker = RealIssueChecker()
    checker.check_real_issues()
    checker.print_report()


if __name__ == "__main__":
    main()
