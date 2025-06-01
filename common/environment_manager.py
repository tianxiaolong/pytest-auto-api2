#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
环境管理器模块

提供多环境配置管理功能，支持测试环境、预发环境、生产环境的切换
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
from common.config_loader import ConfigLoader


class EnvironmentManager:
    """环境管理器"""
    
    # 支持的环境类型
    SUPPORTED_ENVIRONMENTS = {
        'test': '测试环境',
        'staging': '预发环境', 
        'prod': '生产环境'
    }
    
    def __init__(self, config_loader: ConfigLoader = None):
        """
        初始化环境管理器
        
        Args:
            config_loader: 配置加载器实例
        """
        self.config_loader = config_loader or ConfigLoader()
        self._current_env = None
        self._env_config = None
    
    def get_current_environment(self) -> str:
        """
        获取当前环境
        
        Returns:
            当前环境名称
        """
        if self._current_env is None:
            # 优先从环境变量获取
            self._current_env = os.getenv('TEST_ENV', 'test')
            
            # 验证环境是否支持
            if self._current_env not in self.SUPPORTED_ENVIRONMENTS:
                print(f"⚠️ 不支持的环境: {self._current_env}，使用默认环境: test")
                self._current_env = 'test'
                
        return self._current_env
    
    def set_environment(self, env: str) -> bool:
        """
        设置当前环境
        
        Args:
            env: 环境名称
            
        Returns:
            设置是否成功
        """
        if env not in self.SUPPORTED_ENVIRONMENTS:
            print(f"❌ 不支持的环境: {env}")
            print(f"支持的环境: {list(self.SUPPORTED_ENVIRONMENTS.keys())}")
            return False
            
        self._current_env = env
        self._env_config = None  # 清除缓存
        
        # 设置环境变量
        os.environ['TEST_ENV'] = env
        
        print(f"✅ 环境已切换到: {env} ({self.SUPPORTED_ENVIRONMENTS[env]})")
        return True
    
    def get_environment_config(self, env: str = None) -> Dict[str, Any]:
        """
        获取指定环境的配置
        
        Args:
            env: 环境名称，默认为当前环境
            
        Returns:
            环境配置字典
        """
        if env is None:
            env = self.get_current_environment()
            
        if self._env_config is None or self._current_env != env:
            config = self.config_loader.load_config()
            environments = config.get('environments', {})
            
            if env not in environments:
                print(f"⚠️ 环境配置不存在: {env}，使用默认配置")
                return self._get_default_config()
                
            self._env_config = environments[env]
            
        return self._env_config
    
    def get_host(self, env: str = None) -> str:
        """
        获取指定环境的主机地址
        
        Args:
            env: 环境名称，默认为当前环境
            
        Returns:
            主机地址
        """
        env_config = self.get_environment_config(env)
        return env_config.get('host', 'https://www.wanandroid.com')
    
    def get_app_host(self, env: str = None) -> str:
        """
        获取指定环境的应用主机地址
        
        Args:
            env: 环境名称，默认为当前环境
            
        Returns:
            应用主机地址
        """
        env_config = self.get_environment_config(env)
        return env_config.get('app_host', '')
    
    def get_database_url(self, env: str = None) -> str:
        """
        获取指定环境的数据库连接地址
        
        Args:
            env: 环境名称，默认为当前环境
            
        Returns:
            数据库连接地址
        """
        env_config = self.get_environment_config(env)
        return env_config.get('database_url', '')
    
    def get_environment_name(self, env: str = None) -> str:
        """
        获取环境的中文名称
        
        Args:
            env: 环境名称，默认为当前环境
            
        Returns:
            环境中文名称
        """
        if env is None:
            env = self.get_current_environment()
        return self.SUPPORTED_ENVIRONMENTS.get(env, env)
    
    def list_environments(self) -> Dict[str, str]:
        """
        列出所有支持的环境
        
        Returns:
            环境名称和描述的字典
        """
        return self.SUPPORTED_ENVIRONMENTS.copy()
    
    def validate_environment_config(self, env: str = None) -> Dict[str, Any]:
        """
        验证环境配置的完整性
        
        Args:
            env: 环境名称，默认为当前环境
            
        Returns:
            验证结果
        """
        if env is None:
            env = self.get_current_environment()
            
        result = {
            'environment': env,
            'valid': True,
            'missing_configs': [],
            'warnings': []
        }
        
        env_config = self.get_environment_config(env)
        
        # 检查必需的配置项
        required_configs = ['host']
        for config_key in required_configs:
            if not env_config.get(config_key):
                result['missing_configs'].append(config_key)
                result['valid'] = False
        
        # 检查可选配置项
        optional_configs = ['app_host', 'database_url']
        for config_key in optional_configs:
            if not env_config.get(config_key):
                result['warnings'].append(f"可选配置 {config_key} 未设置")
        
        return result
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置
        
        Returns:
            默认配置字典
        """
        return {
            'name': '默认环境',
            'host': 'https://www.wanandroid.com',
            'app_host': '',
            'database_url': ''
        }
    
    def print_current_environment_info(self):
        """打印当前环境信息"""
        current_env = self.get_current_environment()
        env_config = self.get_environment_config()
        
        print(f"\n🌍 当前环境信息:")
        print(f"  环境代码: {current_env}")
        print(f"  环境名称: {self.get_environment_name()}")
        print(f"  主机地址: {env_config.get('host', 'N/A')}")
        print(f"  应用地址: {env_config.get('app_host', 'N/A')}")
        print(f"  数据库地址: {env_config.get('database_url', 'N/A')}")


# 全局环境管理器实例
environment_manager = EnvironmentManager()


def get_environment_manager() -> EnvironmentManager:
    """
    获取环境管理器实例
    
    Returns:
        环境管理器实例
    """
    return environment_manager


def get_current_host() -> str:
    """
    获取当前环境的主机地址
    
    Returns:
        主机地址
    """
    return environment_manager.get_host()


def get_current_app_host() -> str:
    """
    获取当前环境的应用主机地址
    
    Returns:
        应用主机地址
    """
    return environment_manager.get_app_host()


if __name__ == "__main__":
    # 测试环境管理器
    manager = EnvironmentManager()
    
    print("🧪 环境管理器测试")
    print("=" * 50)
    
    # 列出所有环境
    print("\n📋 支持的环境:")
    for env_code, env_name in manager.list_environments().items():
        print(f"  {env_code}: {env_name}")
    
    # 显示当前环境
    manager.print_current_environment_info()
    
    # 验证配置
    validation = manager.validate_environment_config()
    print(f"\n✅ 配置验证: {'通过' if validation['valid'] else '失败'}")
    if validation['missing_configs']:
        print(f"❌ 缺少配置: {validation['missing_configs']}")
    if validation['warnings']:
        print(f"⚠️ 警告: {validation['warnings']}")
