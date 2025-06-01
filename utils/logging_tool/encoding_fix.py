#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Encoding Fix Module

This module provides encoding fix functionality.
"""

"""
日志编码修复工具
解决中文字符在日志中显示乱码的问题

@Time   : 2023-12-20
@Author : txl
"""
import locale
import logging
import os
import sys
from typing import Optional


class EncodingFixer:
    """编码修复器"""

    @staticmethod
    def fix_console_encoding() -> bool:
        """
        修复控制台编码

        Returns:
            是否修复成功
        """
        try:
            # 设置标准输出编码
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8")

            # 设置标准错误输出编码
            if hasattr(sys.stderr, "reconfigure"):
                sys.stderr.reconfigure(encoding="utf-8")

            # 设置环境变量
            os.environ["PYTHONIOENCODING"] = "utf-8"

            return True
        except Exception as e:
            print(f"修复控制台编码失败: {e}")
            return False

    @staticmethod
    def fix_logging_encoding() -> bool:
        """
        修复日志编码

        Returns:
            是否修复成功
        """
        try:
            # 获取根日志记录器
            root_logger = logging.getLogger()

            # 修复所有处理器的编码
            for handler in root_logger.handlers:
                if hasattr(handler, "stream") and hasattr(handler.stream, "reconfigure"):
                    handler.stream.reconfigure(encoding="utf-8")
                elif hasattr(handler, "setStream"):
                    # 对于文件处理器，重新设置编码
                    if hasattr(handler, "baseFilename"):
                        handler.close()
                        # 重新打开文件，使用UTF-8编码
                        handler.stream = open(handler.baseFilename, "a", encoding="utf-8")

            return True
        except Exception as e:
            print(f"修复日志编码失败: {e}")
            return False

    @staticmethod
    def get_system_encoding_info() -> dict:
        """
        获取系统编码信息

        Returns:
            系统编码信息字典
        """
        return {
            "default_encoding": sys.getdefaultencoding(),
            "filesystem_encoding": sys.getfilesystemencoding(),
            "preferred_encoding": locale.getpreferredencoding(),
            "stdout_encoding": getattr(sys.stdout, "encoding", "unknown"),
            "stderr_encoding": getattr(sys.stderr, "encoding", "unknown"),
            "platform": sys.platform,
            "python_version": sys.version,
        }

    @staticmethod
    def test_encoding(test_string: str = "测试中文编码") -> bool:
        """
        测试编码是否正常

        Args:
            test_string: 测试字符串

        Returns:
            编码是否正常
        """
        try:
            # 测试打印
            print(test_string)

            # 测试编码解码
            encoded = test_string.encode("utf-8")
            decoded = encoded.decode("utf-8")

            return decoded == test_string
        except Exception as e:
            print(f"编码测试失败: {e}")
            return False

    @classmethod
    def fix_all_encoding(cls) -> bool:
        """
        修复所有编码问题

        Returns:
            是否全部修复成功
        """
        print("🔧 开始修复编码问题...")

        # 显示当前编码信息
        info = cls.get_system_encoding_info()
        print("📊 当前系统编码信息:")
        for key, value in info.items():
            print(f"   {key}: {value}")

        # 修复控制台编码
        console_fixed = cls.fix_console_encoding()
        print(f"🖥️ 控制台编码修复: {'✅ 成功' if console_fixed else '❌ 失败'}")

        # 修复日志编码
        logging_fixed = cls.fix_logging_encoding()
        print(f"📝 日志编码修复: {'✅ 成功' if logging_fixed else '❌ 失败'}")

        # 测试编码
        test_passed = cls.test_encoding()
        print(f"🧪 编码测试: {'✅ 通过' if test_passed else '❌ 失败'}")

        success = console_fixed and logging_fixed and test_passed
        print(f"🎯 总体结果: {'✅ 全部成功' if success else '❌ 部分失败'}")

        return success


def setup_utf8_encoding():
    """设置UTF-8编码（在程序启动时调用）"""
    # 设置环境变量
    os.environ["PYTHONIOENCODING"] = "utf-8"

    # 修复控制台编码
    EncodingFixer.fix_console_encoding()


# 自动修复编码（导入时执行）
if __name__ != "__main__":
    setup_utf8_encoding()


def main():
    """主函数"""
    print("🚀 日志编码修复工具")
    print("=" * 50)

    # 修复所有编码问题
    success = EncodingFixer.fix_all_encoding()

    if success:
        print("\n🎉 编码修复完成！现在可以正常显示中文了。")
        print("建议在程序入口处导入此模块：")
        print("from utils.logging_tool.encoding_fix import setup_utf8_encoding")
        print("setup_utf8_encoding()")
    else:
        print("\n⚠️ 编码修复未完全成功，可能需要手动设置：")
        print("1. 设置PowerShell编码: chcp 65001")
        print("2. 设置环境变量: set PYTHONIOENCODING=utf-8")
        print("3. 检查IDE编码设置")


if __name__ == "__main__":
    main()
