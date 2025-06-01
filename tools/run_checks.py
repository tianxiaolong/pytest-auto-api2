#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from pathlib import Path

"""
项目检查工具快速启动脚本

提供简单的命令行界面来运行各种检查工具
"""

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from project_checker_manager import ProjectCheckerManager


def show_menu():
    """显示菜单"""
    print("\n" + "=" * 60)
    print("🛠️  项目检查工具集")
    print("=" * 60)
    print("请选择要执行的检查类型:")
    print()
    print("1. 🚀 全面检查 (推荐) - 完整的项目健康检查")
    print("2. ⚡ 快速检查 - 核心功能快速验证")
    print("3. 🏥 健康检查 - 仅项目健康状况")
    print("4. 📊 数据驱动检查 - 仅数据驱动功能")
    print("5. 🧪 测试执行检查 - 仅测试执行状况")
    print("6. 📋 查看报告文件")
    print("0. 退出")
    print()


def show_reports():
    """显示报告文件"""
    print("\n📋 可用的报告文件:")
    print("-" * 40)

    report_files = [
        ("project_health_report.json", "项目健康检查报告"),
        ("data_driver_report.json", "数据驱动检查报告"),
        ("test_execution_report.json", "测试执行检查报告"),
        ("comprehensive_report.json", "综合检查报告")
    ]

    for filename, description in report_files:
        file_path = project_root / filename
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  ✅ {filename} - {description} ({size} bytes)")
        else:
            print(f"  ❌ {filename} - {description} (不存在)")

    print("\n💡 提示: 可以用文本编辑器或JSON查看器打开这些文件")


def main():
    """主函数"""
    manager = ProjectCheckerManager()

    while True:
        show_menu()

        try:
            choice = input("请输入选择 (0-6): ").strip()

            if choice == '0':
                print("\n👋 再见！")
                break
            elif choice == '1':
                print("\n🚀 开始全面检查...")
                manager.run_all_checks()
            elif choice == '2':
                print("\n⚡ 开始快速检查...")
                manager.run_quick_check()
            elif choice == '3':
                print("\n🏥 开始健康检查...")
                manager.run_health_check_only()
            elif choice == '4':
                print("\n📊 开始数据驱动检查...")
                manager.run_data_driver_check_only()
            elif choice == '5':
                print("\n🧪 开始测试执行检查...")
                manager.run_test_execution_check_only()
            elif choice == '6':
                show_reports()
            else:
                print("\n❌ 无效选择，请重新输入")
                continue

            if choice in ['1', '2', '3', '4', '5']:
                input("\n按回车键继续...")

        except KeyboardInterrupt:
            print("\n\n👋 用户取消，再见！")
            break
        except Exception as e:
            print(f"\n❌ 执行出错: {e}")
            input("按回车键继续...")


if __name__ == "__main__":
    main()
