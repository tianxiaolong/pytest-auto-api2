#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证作者信息替换结果
检查项目中是否还有旧的作者信息
"""

import os
import re
from pathlib import Path


def check_old_authors():
    """检查是否还有旧的作者信息"""
    project_root = Path(__file__).parent.parent

    # 要检查的旧作者信息
    old_authors = [
        r'@Author\s*:\s*余少琪',
        r'@Author\s*:\s*测试工程师'
    ]

    found_old_authors = []

    # 遍历所有Python文件
    for py_file in project_root.rglob("*.py"):
        if "venv" in str(py_file) or "__pycache__" in str(py_file):
            continue

        # 跳过替换脚本本身，因为它包含旧作者信息作为注释说明
        if py_file.name == "replace_author.py":
            continue

        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            for pattern in old_authors:
                matches = re.findall(pattern, content)
                if matches:
                    found_old_authors.append({
                        'file': str(py_file.relative_to(project_root)),
                        'pattern': pattern,
                        'matches': matches
                    })

        except Exception as e:
            print(f"⚠️ 无法读取文件 {py_file}: {e}")

    return found_old_authors


def check_new_author():
    """检查新作者信息的数量"""
    project_root = Path(__file__).parent.parent

    new_author_count = 0
    files_with_new_author = []

    # 遍历所有Python文件
    for py_file in project_root.rglob("*.py"):
        if "venv" in str(py_file) or "__pycache__" in str(py_file):
            continue

        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查新的作者信息
            if re.search(r'@Author\s*:\s*txl', content):
                new_author_count += 1
                files_with_new_author.append(str(py_file.relative_to(project_root)))

        except Exception as e:
            print(f"⚠️ 无法读取文件 {py_file}: {e}")

    return new_author_count, files_with_new_author


def main():
    """主函数"""
    print("🔍 验证作者信息替换结果...")
    print("=" * 60)

    # 检查旧作者信息
    old_authors = check_old_authors()

    if old_authors:
        print("❌ 发现未替换的旧作者信息:")
        for item in old_authors:
            print(f"  📁 {item['file']}")
            print(f"     模式: {item['pattern']}")
            print(f"     匹配: {item['matches']}")
            print()
    else:
        print("✅ 未发现旧作者信息，替换成功！")

    print("-" * 60)

    # 检查新作者信息
    new_count, new_files = check_new_author()

    print(f"📊 新作者信息统计:")
    print(f"  总文件数: {new_count}")
    print(f"  包含 '@Author : txl' 的文件:")

    for file_path in sorted(new_files):
        print(f"    ✅ {file_path}")

    print("=" * 60)

    if not old_authors:
        print("🎉 作者信息替换完成！")
        print(f"   成功替换了 {new_count} 个文件中的作者信息")
        print("   所有文件的作者信息已统一为: txl")
    else:
        print("⚠️ 还有部分文件需要手动处理")
        return False

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
