#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Clean Files Module

This module provides clean files functionality.
"""

"""
# @Time   : 2022/4/7 11:56
# @Author : txl
"""
import os


def del_file(path):
    """删除目录下的文件"""
    list_path = os.listdir(path)
    for i in list_path:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            del_file(c_path)
        else:
            os.remove(c_path)
