#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Final Fix Module

This module provides final fix functionality.
"""

"""
最终修复脚本 - 彻底解决剩余的代码质量问题

@Time   : 2023-12-20
@Author : txl
"""
import os
from pathlib import Path


def fix_utils_init():
    """修复 utils/__init__.py 的编码声明问题"""
    file_path = Path("utils/__init__.py")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 确保文件以正确的编码声明开始
    if content.startswith("\n"):
        content = content.lstrip("\n")

    if not content.startswith("#!/usr/bin/env python"):
        content = "#!/usr/bin/env python\n# -*- coding: utf-8 -*-\n" + content
    elif "# -*- coding: utf-8 -*-" not in content[:100]:
        lines = content.split("\n")
        lines.insert(1, "# -*- coding: utf-8 -*-")
        content = "\n".join(lines)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✓ 修复了 {file_path} 的编码声明问题")


def fix_import_orders():
    """修复导入顺序问题"""
    files_to_fix = [
        "utils/notify/ding_talk.py",
        "utils/read_files_tools/regular_control.py",
        "utils/read_files_tools/testcase_template.py",
        "utils/recording/mitmproxy_control.py",
        "utils/requests_tool/encryption_algorithm_control.py",
        "utils/requests_tool/request_control.py",
    ]

    for file_path in files_to_fix:
        try:
            path = Path(file_path)
            if not path.exists():
                continue

            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # 找到导入区域
            import_start = -1
            import_end = -1

            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith(("import ", "from ")) and not stripped.startswith("#"):
                    if import_start == -1:
                        import_start = i
                    import_end = i
                elif (
                    import_start != -1
                    and stripped
                    and not stripped.startswith("#")
                    and not stripped.startswith('"""')
                    and not stripped.startswith("'''")
                ):
                    break

            if import_start == -1:
                continue

            # 提取导入语句
            before_imports = lines[:import_start]
            import_lines = lines[import_start : import_end + 1]
            after_imports = lines[import_end + 1 :]

            # 分类导入
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
                "binascii",
                "hmac",
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

            # 重新排序
            new_imports = []
            if stdlib_imports:
                new_imports.extend(sorted(stdlib_imports))
                new_imports.append("\n")
            if third_party_imports:
                new_imports.extend(sorted(third_party_imports))
                new_imports.append("\n")
            if local_imports:
                new_imports.extend(sorted(local_imports))
                if after_imports and after_imports[0].strip():
                    new_imports.append("\n")

            # 重新组合文件
            new_content = before_imports + new_imports + after_imports

            with open(path, "w", encoding="utf-8") as f:
                f.writelines(new_content)

            print(f"✓ 修复了 {file_path} 的导入顺序")

        except Exception as e:
            print(f"✗ 修复 {file_path} 失败: {e}")


def main():
    """主函数"""
    print("开始最终修复...")

    # 修复编码声明
    fix_utils_init()

    # 修复导入顺序
    fix_import_orders()

    print("\n🎉 最终修复完成！")
    print("建议运行 'python scripts/code_quality_check.py' 验证修复结果")


if __name__ == "__main__":
    main()
