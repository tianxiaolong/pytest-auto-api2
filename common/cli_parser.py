#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
命令行参数解析器

提供统一的命令行参数处理功能，支持环境切换、数据驱动类型选择等
"""

import argparse
import os
import sys
from typing import Dict, Any, List, Optional
from pathlib import Path


class CLIParser:
    """命令行参数解析器"""
    
    def __init__(self):
        """初始化解析器"""
        self.parser = argparse.ArgumentParser(
            description='pytest-auto-api2 自动化测试框架',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
使用示例:
  # 在测试环境运行，使用YAML数据驱动
  python run.py --env test --data-driver yaml
  
  # 在预发环境运行，使用Excel数据驱动，发送钉钉通知
  python run.py --env staging --data-driver excel --notification dingtalk
  
  # 强制重新生成测试用例
  python run.py --force-generate
  
  # 运行指定的测试模块
  python run.py --test-path test_case/Login
  
  # Jenkins集成示例
  python run.py --env ${ENV} --data-driver ${DATA_DRIVER} --notification ${NOTIFICATION}
            """
        )
        self._setup_arguments()
    
    def _setup_arguments(self):
        """设置命令行参数"""
        
        # 环境相关参数
        env_group = self.parser.add_argument_group('环境配置')
        env_group.add_argument(
            '--env', '--environment',
            choices=['test', 'staging', 'prod'],
            default=None,
            help='指定运行环境 (test: 测试环境, staging: 预发环境, prod: 生产环境)'
        )
        env_group.add_argument(
            '--host',
            help='指定主机地址，会覆盖环境配置中的host'
        )
        env_group.add_argument(
            '--app-host',
            help='指定应用主机地址，会覆盖环境配置中的app_host'
        )
        
        # 数据驱动相关参数
        data_group = self.parser.add_argument_group('数据驱动配置')
        data_group.add_argument(
            '--data-driver', '--driver',
            choices=['yaml', 'excel'],
            default=None,
            help='指定数据驱动类型 (yaml: YAML文件驱动, excel: Excel文件驱动)'
        )
        data_group.add_argument(
            '--yaml-path',
            help='指定YAML数据文件路径'
        )
        data_group.add_argument(
            '--excel-path', 
            help='指定Excel数据文件路径'
        )
        
        # 测试执行相关参数
        test_group = self.parser.add_argument_group('测试执行配置')
        test_group.add_argument(
            '--test-path', '--path',
            help='指定测试用例路径，支持文件或目录'
        )
        test_group.add_argument(
            '--markers', '-m',
            help='指定pytest标记，例如: smoke, regression'
        )
        test_group.add_argument(
            '--parallel', '-n',
            type=int,
            help='并行执行的进程数'
        )
        test_group.add_argument(
            '--reruns',
            type=int,
            default=0,
            help='失败用例重试次数'
        )
        test_group.add_argument(
            '--reruns-delay',
            type=int,
            default=1,
            help='重试间隔时间(秒)'
        )
        
        # 报告和通知相关参数
        report_group = self.parser.add_argument_group('报告和通知配置')
        report_group.add_argument(
            '--notification', '--notify',
            choices=['dingtalk', 'wechat', 'email', 'lark', 'all'],
            help='指定通知方式'
        )
        report_group.add_argument(
            '--excel-report',
            action='store_true',
            help='生成Excel错误报告'
        )
        report_group.add_argument(
            '--no-allure-serve',
            action='store_true',
            help='不启动Allure报告服务'
        )
        report_group.add_argument(
            '--allure-port',
            type=int,
            default=9999,
            help='Allure报告服务端口'
        )
        
        # 测试用例生成相关参数
        generate_group = self.parser.add_argument_group('测试用例生成配置')
        generate_group.add_argument(
            '--force-generate', '--force',
            action='store_true',
            help='强制重新生成所有测试用例'
        )
        generate_group.add_argument(
            '--no-generate',
            action='store_true',
            help='跳过测试用例生成'
        )
        generate_group.add_argument(
            '--clean-obsolete',
            action='store_true',
            help='清理过时的测试文件'
        )
        
        # 其他参数
        other_group = self.parser.add_argument_group('其他配置')
        other_group.add_argument(
            '--config',
            help='指定配置文件路径'
        )
        other_group.add_argument(
            '--verbose', '-v',
            action='count',
            default=0,
            help='详细输出模式，可重复使用增加详细程度'
        )
        other_group.add_argument(
            '--quiet', '-q',
            action='store_true',
            help='静默模式，减少输出'
        )
        other_group.add_argument(
            '--dry-run',
            action='store_true',
            help='模拟运行，不执行实际测试'
        )
        other_group.add_argument(
            '--version',
            action='version',
            version='pytest-auto-api2 v2.0.0'
        )
    
    def parse_args(self, args: List[str] = None) -> argparse.Namespace:
        """
        解析命令行参数
        
        Args:
            args: 参数列表，默认从sys.argv获取
            
        Returns:
            解析后的参数对象
        """
        return self.parser.parse_args(args)
    
    def apply_args_to_environment(self, args: argparse.Namespace) -> Dict[str, Any]:
        """
        将命令行参数应用到环境变量
        
        Args:
            args: 解析后的参数对象
            
        Returns:
            应用的环境变量字典
        """
        applied_vars = {}
        
        # 环境相关
        if args.env:
            os.environ['TEST_ENV'] = args.env
            applied_vars['TEST_ENV'] = args.env
            
        if args.host:
            os.environ['HOST'] = args.host
            applied_vars['HOST'] = args.host
            
        if args.app_host:
            os.environ['APP_HOST'] = args.app_host
            applied_vars['APP_HOST'] = args.app_host
        
        # 数据驱动相关
        if args.data_driver:
            os.environ['DATA_DRIVER_TYPE'] = args.data_driver
            applied_vars['DATA_DRIVER_TYPE'] = args.data_driver
            
        if args.yaml_path:
            os.environ['YAML_DATA_PATH'] = args.yaml_path
            applied_vars['YAML_DATA_PATH'] = args.yaml_path
            
        if args.excel_path:
            os.environ['EXCEL_DATA_PATH'] = args.excel_path
            applied_vars['EXCEL_DATA_PATH'] = args.excel_path
        
        # 通知相关
        if args.notification:
            notification_mapping = {
                'dingtalk': '1',
                'wechat': '2', 
                'email': '3',
                'lark': '4',
                'all': '1,2,3,4'
            }
            notification_value = notification_mapping.get(args.notification, '0')
            os.environ['NOTIFICATION_TYPE'] = notification_value
            applied_vars['NOTIFICATION_TYPE'] = notification_value
        
        # Excel报告
        if args.excel_report:
            os.environ['EXCEL_REPORT'] = 'True'
            applied_vars['EXCEL_REPORT'] = 'True'
        
        return applied_vars
    
    def build_pytest_args(self, args: argparse.Namespace) -> List[str]:
        """
        构建pytest命令行参数
        
        Args:
            args: 解析后的参数对象
            
        Returns:
            pytest参数列表
        """
        pytest_args = []
        
        # 基础参数
        pytest_args.extend([
            "-s",
            "-W", "ignore:Module already imported:pytest.PytestWarning",
            "--alluredir", "./report/tmp",
            "--clean-alluredir"
        ])
        
        # 测试路径
        if args.test_path:
            pytest_args.append(args.test_path)
        
        # 标记
        if args.markers:
            pytest_args.extend(["-m", args.markers])
        
        # 并行执行
        if args.parallel:
            pytest_args.extend(["-n", str(args.parallel)])
        
        # 重试配置
        if args.reruns > 0:
            pytest_args.extend(["--reruns", str(args.reruns)])
            if args.reruns_delay > 0:
                pytest_args.extend(["--reruns-delay", str(args.reruns_delay)])
        
        # 详细程度
        if args.verbose > 0:
            pytest_args.append("-" + "v" * args.verbose)
        elif args.quiet:
            pytest_args.append("-q")
        
        return pytest_args
    
    def print_configuration_summary(self, args: argparse.Namespace, applied_vars: Dict[str, Any]):
        """
        打印配置摘要
        
        Args:
            args: 解析后的参数对象
            applied_vars: 应用的环境变量
        """
        print("\n🔧 运行配置摘要:")
        print("=" * 50)
        
        # 环境配置
        print(f"🌍 运行环境: {args.env or '默认'}")
        if args.host:
            print(f"🔗 主机地址: {args.host}")
        
        # 数据驱动配置
        print(f"📊 数据驱动: {args.data_driver or '默认'}")
        
        # 测试配置
        if args.test_path:
            print(f"📁 测试路径: {args.test_path}")
        if args.markers:
            print(f"🏷️ 测试标记: {args.markers}")
        if args.parallel:
            print(f"⚡ 并行进程: {args.parallel}")
        
        # 通知配置
        if args.notification:
            print(f"📢 通知方式: {args.notification}")
        
        # 其他配置
        if args.force_generate:
            print("🔄 强制重新生成测试用例")
        if args.excel_report:
            print("📊 生成Excel报告")
        if args.dry_run:
            print("🧪 模拟运行模式")
        
        # 应用的环境变量
        if applied_vars:
            print(f"\n📝 应用的环境变量:")
            for key, value in applied_vars.items():
                print(f"  {key}={value}")


# 全局CLI解析器实例
cli_parser = CLIParser()


def get_cli_parser() -> CLIParser:
    """
    获取CLI解析器实例
    
    Returns:
        CLI解析器实例
    """
    return cli_parser


def parse_command_line_args(args: List[str] = None) -> argparse.Namespace:
    """
    解析命令行参数的便捷函数
    
    Args:
        args: 参数列表，默认从sys.argv获取
        
    Returns:
        解析后的参数对象
    """
    return cli_parser.parse_args(args)


if __name__ == "__main__":
    # 测试CLI解析器
    parser = CLIParser()
    
    # 模拟一些参数
    test_args = [
        '--env', 'test',
        '--data-driver', 'yaml', 
        '--notification', 'dingtalk',
        '--force-generate',
        '--verbose'
    ]
    
    args = parser.parse_args(test_args)
    applied_vars = parser.apply_args_to_environment(args)
    parser.print_configuration_summary(args, applied_vars)
    
    print(f"\n🧪 构建的pytest参数:")
    pytest_args = parser.build_pytest_args(args)
    print(f"  {' '.join(pytest_args)}")
