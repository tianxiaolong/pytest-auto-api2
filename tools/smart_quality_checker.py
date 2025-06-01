#!/usr/bin/env python
# -*- coding: utf-8 -*-


import argparse
import sys
from pathlib import Path

"""
智能代码质量检查工具
可以选择不同的严格程度进行检查

@Time   : 2023-12-20
@Author : txl
"""


def run_strict_check():
    """运行严格检查"""
    print("🔍 运行严格代码质量检查...")
    print("=" * 60)

    try:
        from tools.code_quality_checker import main as strict_main
        return strict_main()
    except ImportError:
        print("❌ 无法导入严格检查工具")
        return 1


def run_relaxed_check():
    """运行宽松检查"""
    print("✅ 运行宽松代码质量检查...")
    print("=" * 60)

    try:
        from final_quality_check import main as relaxed_main
        return relaxed_main()
    except ImportError:
        print("❌ 无法导入宽松检查工具")
        return 1


def run_custom_check(focus_areas):
    """运行自定义检查"""
    print(f"🎯 运行自定义检查 (关注: {', '.join(focus_areas)})...")
    print("=" * 60)

    from tools.code_quality_checker import CodeQualityChecker

    checker = CodeQualityChecker()
    python_files = list(Path(".").rglob("*.py"))

    total_issues = 0
    file_results = {}

    for py_file in python_files:
        if 'venv' in str(py_file) or '__pycache__' in str(py_file):
            continue

        file_issues = {}

        # 根据关注领域进行检查
        if 'syntax' in focus_areas:
            issues = checker.check_python_syntax(py_file)
            if issues:
                file_issues['syntax'] = issues

        if 'imports' in focus_areas:
            issues = checker.check_import_style(py_file)
            if issues:
                file_issues['imports'] = issues

        if 'docstrings' in focus_areas:
            issues = checker.check_docstrings(py_file)
            if issues:
                file_issues['docstrings'] = issues

        if 'security' in focus_areas:
            issues = checker.check_security_issues(py_file)
            if issues:
                file_issues['security'] = issues

        if 'complexity' in focus_areas:
            issues = checker.check_function_complexity(py_file)
            if issues:
                file_issues['complexity'] = issues

        if 'naming' in focus_areas:
            issues = checker.check_naming_conventions(py_file)
            if issues:
                file_issues['naming'] = issues

        if file_issues:
            file_results[str(py_file)] = file_issues
            total_issues += sum(len(issues) for issues in file_issues.values())

    # 显示结果
    print(f"\n📊 自定义检查结果:")
    print(f"   关注领域: {', '.join(focus_areas)}")
    print(f"   发现问题: {total_issues}")

    if total_issues > 0:
        print(f"\n📋 问题分布:")
        issue_types = {}
        for file_issues in file_results.values():
            for issue_type, issues in file_issues.items():
                if issue_type not in issue_types:
                    issue_types[issue_type] = 0
                issue_types[issue_type] += len(issues)

        for issue_type, count in issue_types.items():
            print(f"   {issue_type}: {count}")

        return 1
    else:
        print("✅ 在关注领域内未发现问题！")
        return 0


def show_comparison():
    """显示两种检查模式的对比"""
    print("📊 代码质量检查工具对比")
    print("=" * 60)

    comparison_table = """
┌─────────────────┬─────────────────────┬─────────────────────┐
│ 检查项目        │ 严格模式            │ 宽松模式            │
├─────────────────┼─────────────────────┼─────────────────────┤
│ 语法错误        │ ✅ 详细检查         │ ✅ 基础检查         │
│ 导入风格        │ ✅ 严格检查         │ ❌ 不检查           │
│ 函数复杂度      │ ✅ 详细分析         │ ❌ 不检查           │
│ 文档字符串      │ ✅ 全面检查         │ ❌ 不检查           │
│ 命名规范        │ ✅ 严格检查         │ ❌ 不检查           │
│ 行长度          │ ✅ 120字符限制      │ ❌ 不检查           │
│ 安全问题        │ ✅ 多维度检查       │ ❌ 不检查           │
│ 外部工具        │ ✅ flake8集成       │ ❌ 不检查           │
│ 项目结构        │ ❌ 不检查           │ ✅ 基础检查         │
│ 功能完整性      │ ❌ 不检查           │ ✅ 详细检查         │
├─────────────────┼─────────────────────┼─────────────────────┤
│ 检查深度        │ 🔥 非常严格         │ 😊 宽松友好         │
│ 问题数量        │ 📊 数百个           │ 📊 通常<10个        │
│ 适用场景        │ 🔧 开发重构         │ ✅ 验收部署         │
│ 执行时间        │ ⏱️ 较长             │ ⏱️ 很快             │
└─────────────────┴─────────────────────┴─────────────────────┘
"""

    print(comparison_table)

    print("\n💡 使用建议:")
    print("   🔧 开发阶段: python tools/smart_quality_checker.py --mode strict")
    print("   ✅ 验收阶段: python tools/smart_quality_checker.py --mode relaxed")
    print("   🎯 自定义检查: python tools/smart_quality_checker.py --mode custom --focus syntax,security")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="智能代码质量检查工具")
    parser.add_argument(
        "--mode",
        choices=["strict", "relaxed", "custom", "compare"],
        default="relaxed",
        help="检查模式: strict(严格), relaxed(宽松), custom(自定义), compare(对比)"
    )
    parser.add_argument(
        "--focus",
        help="自定义模式的关注领域，用逗号分隔 (syntax,imports,docstrings,security,complexity,naming)"
    )

    args = parser.parse_args()

    if args.mode == "strict":
        return run_strict_check()
    elif args.mode == "relaxed":
        return run_relaxed_check()
    elif args.mode == "custom":
        if not args.focus:
            print("❌ 自定义模式需要指定 --focus 参数")
            print("   示例: --focus syntax,security,docstrings")
            return 1

        focus_areas = [area.strip() for area in args.focus.split(",")]
        valid_areas = {"syntax", "imports", "docstrings", "security", "complexity", "naming"}
        invalid_areas = set(focus_areas) - valid_areas

        if invalid_areas:
            print(f"❌ 无效的关注领域: {invalid_areas}")
            print(f"   有效选项: {valid_areas}")
            return 1

        return run_custom_check(focus_areas)
    elif args.mode == "compare":
        show_comparison()
        return 0
    else:
        print("❌ 未知的检查模式")
        return 1


if __name__ == "__main__":
    sys.exit(main())
