#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Encryption Algorithm Control Module

This module provides encryption algorithm control functionality.
"""

"""
# @Time    : 2022/5/23 21:27
# @Author : txl
# @Email   : 1603453211@qq.com
# @File    : encryption_algorithm_control
# @describe:
"""
import binascii
import hashlib
import hmac
from hashlib import sha256
from typing import Text

from pyDes import ECB, PAD_PKCS5, des


def hmac_sha256_encrypt(key, data):
    """hmac sha 256算法"""
    _key = key.encode("utf8")
    _data = data.encode("utf8")
    encrypt_data = hmac.new(_key, _data, digestmod=sha256).hexdigest()
    return encrypt_data


def md5_encryption(value):
    """md5 加密"""
    str_md5 = hashlib.md5(str(value).encode(encoding="utf-8")).hexdigest()
    return str_md5


def sha1_secret_str(_str: Text):
    """
    使用sha1加密算法，返回str加密后的字符串
    """
    encrypts = hashlib.sha1(_str.encode("utf-8")).hexdigest()
    return encrypts


def des_encrypt(_str):
    """
    DES 加密
    :return: 加密后字符串，16进制
    """
    # 密钥，自行修改
    _key = "PASSWORD"
    secret_key = _key
    _iv = secret_key
    key = des(secret_key, ECB, _iv, pad=None, padmode=PAD_PKCS5)
    _encrypt = key.encrypt(_str, padmode=PAD_PKCS5)
    return binascii.b2a_hex(_encrypt)


def encryption(ency_type):
    """
    :param ency_type: 加密类型
    :return:
    """

    def decorator(func):
        """
        装饰器函数

        Args:
            func: 被装饰的函数

        Returns:
            装饰后的函数
        """

        def swapper(*args, **kwargs):
            """
            包装函数

            执行原函数并对返回数据进行加密处理。

            Args:
                *args: 位置参数
                **kwargs: 关键字参数

            Returns:
                加密处理后的函数返回值
            """
            res = func(*args, **kwargs)
            _data = res["body"]
            if ency_type == "md5":

                def ency_value(data):
                    """
                    递归加密数据值

                    对字典中的所有值进行MD5加密，支持嵌套字典。

                    Args:
                        data: 要加密的数据字典
                    """
                    if data is not None:
                        for key, value in data.items():
                            if isinstance(value, dict):
                                ency_value(data=value)
                            else:
                                data[key] = md5_encryption(value)

            else:
                raise ValueError("暂不支持该加密规则，如有需要，请联系管理员")
            ency_value(_data)
            return res

        return swapper

    return decorator
