#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Jenkins集成运行脚本

专门为Jenkins CI/CD流水线设计的运行脚本，支持环境变量传递和参数化构建
"""

import os
import sys
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def setup_jenkins_environment():
    """设置Jenkins环境变量"""
    
    # Jenkins常用环境变量映射
    jenkins_env_mapping = {
        # Jenkins内置变量
        'BUILD_NUMBER': 'BUILD_NUMBER',
        'BUILD_URL': 'BUILD_URL', 
        'JOB_NAME': 'JOB_NAME',
        'WORKSPACE': 'WORKSPACE',
        'NODE_NAME': 'NODE_NAME',
        
        # 自定义参数（在Jenkins中配置）
        'ENV': 'TEST_ENV',                    # 环境选择
        'DATA_DRIVER': 'DATA_DRIVER_TYPE',    # 数据驱动类型
        'NOTIFICATION': 'NOTIFICATION_TYPE',   # 通知类型
        'TEST_PATH': 'TEST_PATH',             # 测试路径
        'PARALLEL': 'PARALLEL_COUNT',         # 并行数量
        'RERUNS': 'RERUNS_COUNT',             # 重试次数
        'MARKERS': 'TEST_MARKERS',            # 测试标记
    }
    
    # 应用环境变量映射
    applied_vars = {}
    for jenkins_var, env_var in jenkins_env_mapping.items():
        value = os.getenv(jenkins_var)
        if value:
            os.environ[env_var] = value
            applied_vars[env_var] = value
    
    return applied_vars


def build_run_command():
    """构建运行命令"""
    
    # 基础命令
    cmd = [sys.executable, 'run.py']
    
    # 环境参数
    env = os.getenv('ENV', os.getenv('TEST_ENV'))
    if env:
        cmd.extend(['--env', env])
    
    # 数据驱动类型
    data_driver = os.getenv('DATA_DRIVER', os.getenv('DATA_DRIVER_TYPE'))
    if data_driver:
        cmd.extend(['--data-driver', data_driver])
    
    # 通知类型
    notification = os.getenv('NOTIFICATION', os.getenv('NOTIFICATION_TYPE'))
    if notification:
        # 转换数字类型到名称
        notification_mapping = {
            '1': 'dingtalk',
            '2': 'wechat', 
            '3': 'email',
            '4': 'lark'
        }
        notification_name = notification_mapping.get(notification, notification)
        cmd.extend(['--notification', notification_name])
    
    # 测试路径
    test_path = os.getenv('TEST_PATH')
    if test_path:
        cmd.extend(['--test-path', test_path])
    
    # 测试标记
    markers = os.getenv('MARKERS', os.getenv('TEST_MARKERS'))
    if markers:
        cmd.extend(['--markers', markers])
    
    # 并行执行
    parallel = os.getenv('PARALLEL', os.getenv('PARALLEL_COUNT'))
    if parallel:
        cmd.extend(['--parallel', parallel])
    
    # 重试次数
    reruns = os.getenv('RERUNS', os.getenv('RERUNS_COUNT'))
    if reruns:
        cmd.extend(['--reruns', reruns])
    
    # Jenkins特定参数
    cmd.extend(['--no-allure-serve'])  # Jenkins中不启动报告服务
    
    # 如果是强制重新生成
    if os.getenv('FORCE_GENERATE', '').lower() in ('true', '1', 'yes'):
        cmd.append('--force-generate')
    
    # Excel报告
    if os.getenv('EXCEL_REPORT', '').lower() in ('true', '1', 'yes'):
        cmd.append('--excel-report')
    
    return cmd


def print_jenkins_info():
    """打印Jenkins构建信息"""
    
    print("🏗️ Jenkins构建信息:")
    print("=" * 60)
    
    jenkins_vars = [
        'BUILD_NUMBER', 'BUILD_URL', 'JOB_NAME', 
        'WORKSPACE', 'NODE_NAME', 'BUILD_TAG'
    ]
    
    for var in jenkins_vars:
        value = os.getenv(var, 'N/A')
        print(f"  {var}: {value}")
    
    print("\n🔧 测试配置:")
    print("=" * 60)
    
    test_vars = [
        ('环境', 'ENV', 'TEST_ENV'),
        ('数据驱动', 'DATA_DRIVER', 'DATA_DRIVER_TYPE'),
        ('通知方式', 'NOTIFICATION', 'NOTIFICATION_TYPE'),
        ('测试路径', 'TEST_PATH', None),
        ('测试标记', 'MARKERS', 'TEST_MARKERS'),
        ('并行数量', 'PARALLEL', 'PARALLEL_COUNT'),
        ('重试次数', 'RERUNS', 'RERUNS_COUNT'),
    ]
    
    for name, jenkins_var, env_var in test_vars:
        value = os.getenv(jenkins_var) or (os.getenv(env_var) if env_var else None)
        print(f"  {name}: {value or 'N/A'}")


def run_tests():
    """运行测试"""
    
    try:
        # 1. 设置环境
        print("🔧 设置Jenkins环境...")
        applied_vars = setup_jenkins_environment()
        
        # 2. 打印构建信息
        print_jenkins_info()
        
        # 3. 构建运行命令
        cmd = build_run_command()
        print(f"\n🚀 执行命令: {' '.join(cmd)}")
        
        # 4. 切换到项目根目录
        os.chdir(project_root)
        
        # 5. 执行测试
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        # 6. 处理结果
        if result.returncode == 0:
            print("\n✅ 测试执行成功")
            return 0
        else:
            print(f"\n❌ 测试执行失败，退出码: {result.returncode}")
            return result.returncode
            
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断执行")
        return 1
    except Exception as e:
        print(f"\n❌ Jenkins运行脚本异常: {e}")
        return 1


def main():
    """主函数"""
    
    print("🏗️ Jenkins自动化测试运行器")
    print("=" * 60)
    
    # 验证Python环境
    print(f"🐍 Python版本: {sys.version}")
    print(f"📁 工作目录: {os.getcwd()}")
    print(f"📂 项目根目录: {project_root}")
    
    # 运行测试
    exit_code = run_tests()
    
    # 退出
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
