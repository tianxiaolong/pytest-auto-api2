#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Security Manager Module

This module provides security manager functionality.
"""

"""
安全管理模块
提供API密钥管理、请求频率限制、数据加密等安全功能

@Time   : 2023-12-20
@Author : txl
"""
import base64
import hashlib
import json
import os
import secrets
import time
from functools import wraps
from typing import Any, Dict, Optional

from cryptography.fernet import Fernet


class APIKeyManager:
    """API密钥管理器"""

    def __init__(self):
        self.keys: Dict[str, Dict[str, Any]] = {}
        self.rotation_interval = 3600 * 24  # 24小时

    def generate_key(self, service_name: str) -> str:
        """生成新的API密钥"""
        key = secrets.token_urlsafe(32)
        self.keys[service_name] = {"key": key, "created_at": time.time(), "last_used": None, "usage_count": 0}
        return key

    def get_key(self, service_name: str) -> Optional[str]:
        """获取API密钥"""
        if service_name in self.keys:
            key_info = self.keys[service_name]
            key_info["last_used"] = time.time()
            key_info["usage_count"] += 1
            return key_info["key"]
        return None

    def rotate_key(self, service_name: str) -> str:
        """轮换API密钥"""
        old_key = self.keys.get(service_name, {}).get("key")
        new_key = self.generate_key(service_name)

        if old_key:
            # 保留旧密钥一段时间以确保平滑过渡
            self.keys[f"{service_name}_old"] = {
                "key": old_key,
                "created_at": time.time(),
                "expires_at": time.time() + 3600,  # 1小时后过期
                "deprecated": True,
            }

        return new_key

    def is_key_expired(self, service_name: str) -> bool:
        """检查密钥是否过期"""
        if service_name not in self.keys:
            return True

        key_info = self.keys[service_name]
        age = time.time() - key_info["created_at"]
        return age > self.rotation_interval

    def cleanup_expired_keys(self):
        """清理过期密钥"""
        current_time = time.time()
        expired_keys = []

        for service_name, key_info in self.keys.items():
            if key_info.get("deprecated") and current_time > key_info.get("expires_at", 0):
                expired_keys.append(service_name)

        for key in expired_keys:
            del self.keys[key]


class RateLimiter:
    """请求频率限制器"""

    def __init__(self, max_requests: int = 100, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, list] = {}

    def is_allowed(self, identifier: str) -> bool:
        """检查是否允许请求"""
        current_time = time.time()

        if identifier not in self.requests:
            self.requests[identifier] = []

        # 清理过期的请求记录
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier] if current_time - req_time < self.time_window
        ]

        # 检查是否超过限制
        if len(self.requests[identifier]) >= self.max_requests:
            return False

        # 记录当前请求
        self.requests[identifier].append(current_time)
        return True

    def get_remaining_requests(self, identifier: str) -> int:
        """获取剩余请求次数"""
        current_time = time.time()

        if identifier not in self.requests:
            return self.max_requests

        # 清理过期的请求记录
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier] if current_time - req_time < self.time_window
        ]

        return max(0, self.max_requests - len(self.requests[identifier]))

    def reset_limit(self, identifier: str):
        """重置限制"""
        if identifier in self.requests:
            del self.requests[identifier]


class DataEncryption:
    """数据加密工具"""

    def __init__(self, key: Optional[bytes] = None):
        if key is None:
            key = Fernet.generate_key()
        self.cipher = Fernet(key)
        self.key = key

    def encrypt(self, data: str) -> str:
        """加密数据"""
        encrypted_data = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """解密数据"""
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = self.cipher.decrypt(encrypted_bytes)
        return decrypted_data.decode()

    def encrypt_dict(self, data: Dict[str, Any]) -> str:
        """加密字典数据"""
        json_data = json.dumps(data, ensure_ascii=False)
        return self.encrypt(json_data)

    def decrypt_dict(self, encrypted_data: str) -> Dict[str, Any]:
        """解密字典数据"""
        json_data = self.decrypt(encrypted_data)
        return json.loads(json_data)

    def get_key(self) -> str:
        """获取加密密钥（Base64编码）"""
        return base64.urlsafe_b64encode(self.key).decode()


class SecurityManager:
    """安全管理器"""

    def __init__(self):
        self.api_key_manager = APIKeyManager()
        self.rate_limiter = RateLimiter()
        self.encryption = DataEncryption()
        self.sensitive_fields = {
            "password",
            "passwd",
            "secret",
            "token",
            "key",
            "api_key",
            "access_token",
            "refresh_token",
            "private_key",
            "cert",
        }

    def sanitize_data(self, data: Any) -> Any:
        """清理敏感数据"""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in self.sensitive_fields):
                    sanitized[key] = "***HIDDEN***"
                else:
                    sanitized[key] = self.sanitize_data(value)
            return sanitized
        elif isinstance(data, list):
            return [self.sanitize_data(item) for item in data]
        else:
            return data

    def validate_input(self, data: str, max_length: int = 1000) -> bool:
        """验证输入数据"""
        if not isinstance(data, str):
            return False

        if len(data) > max_length:
            return False

        # 检查恶意模式
        malicious_patterns = [
            r"<script.*?>.*?</script>",  # XSS
            r"union.*select",  # SQL注入
            r"drop.*table",  # SQL注入
            r"exec\s*\(",  # 代码执行
            r"eval\s*\(",  # 代码执行
        ]

        import re

        for pattern in malicious_patterns:
            if re.search(pattern, data, re.IGNORECASE):
                return False

        return True

    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple:
        """哈希密码"""
        if salt is None:
            salt = secrets.token_hex(16)

        # 使用PBKDF2进行密码哈希
        password_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000  # 迭代次数
        )

        return base64.urlsafe_b64encode(password_hash).decode(), salt

    def verify_password(self, password: str, hashed_password: str, salt: str) -> bool:
        """验证密码"""
        new_hash, _ = self.hash_password(password, salt)
        return new_hash == hashed_password

    def generate_csrf_token(self) -> str:
        """生成CSRF令牌"""
        return secrets.token_urlsafe(32)

    def secure_headers(self) -> Dict[str, str]:
        """获取安全HTTP头"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }


# 全局安全管理器实例
security_manager = SecurityManager()


def rate_limit(max_requests: int = 100, time_window: int = 60, identifier_func=None):
    """请求频率限制装饰器"""
    limiter = RateLimiter(max_requests, time_window)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 确定限制标识符
            if identifier_func:
                identifier = identifier_func(*args, **kwargs)
            else:
                identifier = f"{func.__module__}.{func.__name__}"

            if not limiter.is_allowed(identifier):
                raise Exception("请求频率超限，请稍后再试")

            return func(*args, **kwargs)

        return wrapper

    return decorator


def secure_api_call(encrypt_request: bool = False, encrypt_response: bool = False):
    """安全API调用装饰器"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 加密请求数据
            if encrypt_request and "data" in kwargs:
                kwargs["data"] = security_manager.encryption.encrypt_dict(kwargs["data"])

            # 添加安全头
            if "headers" in kwargs:
                kwargs["headers"].update(security_manager.secure_headers())
            else:
                kwargs["headers"] = security_manager.secure_headers()

            # 执行函数
            result = func(*args, **kwargs)

            # 解密响应数据
            if encrypt_response and hasattr(result, "json"):
                try:
                    encrypted_data = result.json().get("encrypted_data")
                    if encrypted_data:
                        result.decrypted_data = security_manager.encryption.decrypt_dict(encrypted_data)
                except Exception:
                    pass

            return result

        return wrapper

    return decorator


def load_security_config():
    """加载安全配置"""
    config = {
        "encryption_key": os.getenv("ENCRYPTION_KEY"),
        "api_key_rotation_interval": int(os.getenv("API_KEY_ROTATION_INTERVAL", "86400")),
        "rate_limit_max_requests": int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "100")),
        "rate_limit_time_window": int(os.getenv("RATE_LIMIT_TIME_WINDOW", "60")),
        "enable_request_encryption": os.getenv("ENABLE_REQUEST_ENCRYPTION", "false").lower() == "true",
        "enable_response_encryption": os.getenv("ENABLE_RESPONSE_ENCRYPTION", "false").lower() == "true",
    }

    # 如果没有加密密钥，生成一个新的
    if not config["encryption_key"]:
        encryption_key = Fernet.generate_key()
        config["encryption_key"] = base64.urlsafe_b64encode(encryption_key).decode()
        print(f"⚠️ 生成新的加密密钥，请保存到环境变量: ENCRYPTION_KEY={config['encryption_key']}")

    return config


def main():
    """主函数 - 安全功能演示"""
    print("🔒 安全管理器演示")
    print("=" * 50)

    # API密钥管理演示
    print("🔑 API密钥管理:")
    key = security_manager.api_key_manager.generate_key("test_service")
    print(f"   生成密钥: {key[:10]}...")

    retrieved_key = security_manager.api_key_manager.get_key("test_service")
    print(f"   获取密钥: {retrieved_key[:10]}...")

    # 频率限制演示
    print("\n⏱️ 频率限制:")
    for i in range(3):
        allowed = security_manager.rate_limiter.is_allowed("test_user")
        remaining = security_manager.rate_limiter.get_remaining_requests("test_user")
        print(f"   请求 {i+1}: {'允许' if allowed else '拒绝'}, 剩余: {remaining}")

    # 数据加密演示
    print("\n🔐 数据加密:")
    test_data = {"username": "test", "password": "secret123"}
    encrypted = security_manager.encryption.encrypt_dict(test_data)
    print(f"   加密数据: {encrypted[:30]}...")

    decrypted = security_manager.encryption.decrypt_dict(encrypted)
    print(f"   解密数据: {decrypted}")

    # 数据清理演示
    print("\n🧹 敏感数据清理:")
    sensitive_data = {"username": "test", "password": "secret123", "api_key": "abc123"}
    sanitized = security_manager.sanitize_data(sensitive_data)
    print(f"   原始数据: {sensitive_data}")
    print(f"   清理后: {sanitized}")

    print("\n✅ 安全管理器演示完成")


if __name__ == "__main__":
    main()
