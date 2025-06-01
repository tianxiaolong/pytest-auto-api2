#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Log Control Module

This module provides log control functionality.
"""

"""
日志控制模块
提供彩色日志输出和文件日志记录功能

@Time   : 2022/3/28 10:56
@Author : txl
@Update : 2023-12-20 优化日志配置和类型注解
"""
import logging
import time
from logging import handlers
from typing import Dict

import colorlog

from common.setting import ensure_path_sep


class LogHandler:
    """日志处理器，提供彩色日志输出和文件日志记录功能"""

    # 日志级别关系映射
    level_relations: Dict[str, int] = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    def __init__(
        self,
        filename: str,
        level: str = "info",
        when: str = "D",
        fmt: str = "%(levelname)-8s%(asctime)s%(name)s:%(filename)s:%(lineno)d %(message)s",
    ) -> None:
        """
        初始化日志处理器

        Args:
            filename: 日志文件名
            level: 日志级别
            when: 日志轮转时间间隔
            fmt: 日志格式
        """
        self.logger = logging.getLogger(filename)

        # 避免重复添加处理器
        if self.logger.handlers:
            return

        formatter = self._create_color_formatter()

        # 设置日志格式
        file_formatter = logging.Formatter(fmt)
        # 设置日志级别
        self.logger.setLevel(self.level_relations.get(level, logging.INFO))

        # 控制台输出处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        # 设置控制台编码
        if hasattr(console_handler.stream, "reconfigure"):
            console_handler.stream.reconfigure(encoding="utf-8")

        # 文件输出处理器 - 按时间轮转
        file_handler = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=3, encoding="utf-8")
        file_handler.setFormatter(file_formatter)

        # 添加处理器到logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

        self.log_path = ensure_path_sep("\\logs\\log.log")

    @classmethod
    def _create_color_formatter(cls) -> colorlog.ColoredFormatter:
        """
        创建彩色日志格式化器

        Returns:
            彩色日志格式化器
        """
        log_colors_config = {
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red",
        }

        formatter = colorlog.ColoredFormatter(
            "%(log_color)s[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s",
            log_colors=log_colors_config,
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        return formatter

    @classmethod
    def log_color(cls) -> colorlog.ColoredFormatter:
        """向后兼容的方法"""
        return cls._create_color_formatter()


now_time_day = time.strftime("%Y-%m-%d", time.localtime())
INFO = LogHandler(ensure_path_sep(f"\\logs\\info-{now_time_day}.log"), level="info")
ERROR = LogHandler(ensure_path_sep(f"\\logs\\error-{now_time_day}.log"), level="error")
WARNING = LogHandler(ensure_path_sep(f"\\logs\\warning-{now_time_day}.log"))

if __name__ == "__main__":
    ERROR.logger.error("测试")
