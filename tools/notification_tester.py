#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
通知功能测试工具

用于测试各种通知渠道的参数替换和发送功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utils import config
from utils.other_tools.allure_data.allure_report_data import TestMetrics
from utils.notify.notification_helper import get_notification_helper


def create_test_metrics():
    """创建测试用的metrics数据"""
    return TestMetrics(
        passed=8,
        failed=1,
        broken=0,
        skipped=1,
        total=10,
        pass_rate=90.0,
        time=15.5
    )


def preview_dingtalk_notification():
    """预览钉钉通知内容"""
    print("\n📱 钉钉通知内容预览:")
    print("-" * 60)
    
    helper = get_notification_helper()
    metrics = create_test_metrics()
    basic_info = helper.get_basic_info()
    
    text = (
        f"#### {basic_info['project_name']}自动化通知  "
        f"\n\n>Python脚本任务: {basic_info['project_name']}"
        f"\n\n>环境: {basic_info['environment']}\n\n>"
        f"执行人: {basic_info['tester_name']}"
        f"\n\n>执行结果: {metrics.pass_rate}% "
        f"\n\n>总用例数: {metrics.total} "
        f"\n\n>成功用例数: {metrics.passed}"
        f" \n\n>失败用例数: {metrics.failed} "
        f" \n\n>异常用例数: {metrics.broken} "
        f"\n\n>跳过用例数: {metrics.skipped}"
        f"\n\n>用例执行时长: {metrics.time} s"
        " ![screenshot]("
        "https://img.alicdn.com/tfs/TB1NwmBEL9TBuNjy1zbXXXpepXa-2400-1218.png"
        ")\n\n"
        f"{helper.format_dingtalk_links()}"
        "\n\n>非相关负责人员可忽略此消息。"
    )
    
    print(text)
    return text


def preview_wechat_notification():
    """预览企业微信通知内容"""
    print("\n💬 企业微信通知内容预览:")
    print("-" * 60)
    
    helper = get_notification_helper()
    metrics = create_test_metrics()
    basic_info = helper.get_basic_info()
    
    text = f"""【{basic_info['project_name']}自动化通知】
>测试环境：<font color="info">{basic_info['environment']}</font>
>测试负责人：@{basic_info['tester_name']}
>
> **执行结果**
><font color="info">成  功  率  : {metrics.pass_rate}%</font>
>用例  总数：<font color="info">{metrics.total}</font>
>成功用例数：<font color="info">{metrics.passed}</font>
>失败用例数：`{metrics.failed}个`
>异常用例数：`{metrics.broken}个`
>跳过用例数：<font color="warning">{metrics.skipped}个</font>
>用例执行时长：<font color="warning">{metrics.time} s</font>
>时间：<font color="comment">{basic_info['current_time']}</font>
>
>非相关负责人员可忽略此消息。
{helper.format_wechat_links()}"""
    
    print(text)
    return text


def preview_email_notification():
    """预览邮件通知内容"""
    print("\n📧 邮件通知内容预览:")
    print("-" * 60)
    
    helper = get_notification_helper()
    metrics = create_test_metrics()
    basic_info = helper.get_basic_info()
    
    subject = f"{basic_info['project_name']}接口自动化报告"
    
    content = f"""
        各位同事, 大家好:
            自动化用例执行完成，执行结果如下:
            用例运行总数: {metrics.total} 个
            通过用例个数: {metrics.passed} 个
            失败用例个数: {metrics.failed} 个
            异常用例个数: {metrics.broken} 个
            跳过用例个数: {metrics.skipped} 个
            成  功   率: {metrics.pass_rate} %
            用例执行时长: {metrics.time} s

        **********************************
        测试报告访问地址：
{helper.format_email_links()}
        
        详细情况可查看测试报告，非相关负责人员可忽略此消息。谢谢。
        """
    
    print(f"📧 邮件主题: {subject}")
    print(f"📝 邮件内容:")
    print(content)
    return subject, content


def show_report_links():
    """显示报告链接信息"""
    print("\n🔗 测试报告链接信息:")
    print("-" * 60)
    
    helper = get_notification_helper()
    report_info = helper.get_report_info()
    
    print(f"📊 可用的报告链接:")
    for i, url in enumerate(report_info['urls'], 1):
        print(f"  {i}. {url}")
    
    print(f"\n📁 本地报告文件: {report_info['local_path']}")
    
    print(f"\n💡 访问说明:")
    for tip in report_info['access_tips']:
        print(f"  - {tip}")


def show_config_info():
    """显示配置信息"""
    print("\n⚙️ 当前配置信息:")
    print("-" * 60)
    
    helper = get_notification_helper()
    basic_info = helper.get_basic_info()
    
    print(f"📋 项目信息:")
    print(f"  项目名称: {basic_info['project_name']}")
    print(f"  测试人员: {basic_info['tester_name']}")
    print(f"  测试环境: {basic_info['environment']}")
    print(f"  当前时间: {basic_info['current_time']}")
    print(f"  本地IP: {basic_info['local_ip']}")
    
    print(f"\n🔔 通知配置:")
    print(f"  通知类型: {config.notification_type}")
    
    # 检查各种通知配置
    if hasattr(config, 'ding_talk') and hasattr(config.ding_talk, 'webhook'):
        webhook_status = "✅ 已配置" if config.ding_talk.webhook else "❌ 未配置"
        print(f"  钉钉通知: {webhook_status}")
    
    if hasattr(config, 'wechat') and hasattr(config.wechat, 'webhook'):
        webhook_status = "✅ 已配置" if config.wechat.webhook else "❌ 未配置"
        print(f"  企业微信: {webhook_status}")
    
    if hasattr(config, 'email') and hasattr(config.email, 'send_list'):
        email_status = "✅ 已配置" if config.email.send_list else "❌ 未配置"
        print(f"  邮件通知: {email_status}")


def main():
    """主函数"""
    print("🧪 通知功能测试工具")
    print("=" * 80)
    
    while True:
        print("\n请选择要执行的操作:")
        print("1. 📱 预览钉钉通知内容")
        print("2. 💬 预览企业微信通知内容")
        print("3. 📧 预览邮件通知内容")
        print("4. 🔗 查看报告链接信息")
        print("5. ⚙️ 查看配置信息")
        print("6. 📊 查看所有预览")
        print("0. 退出")
        
        try:
            choice = input("\n请输入选择 (0-6): ").strip()
            
            if choice == '0':
                print("\n👋 再见！")
                break
            elif choice == '1':
                preview_dingtalk_notification()
            elif choice == '2':
                preview_wechat_notification()
            elif choice == '3':
                preview_email_notification()
            elif choice == '4':
                show_report_links()
            elif choice == '5':
                show_config_info()
            elif choice == '6':
                show_config_info()
                show_report_links()
                preview_dingtalk_notification()
                preview_wechat_notification()
                preview_email_notification()
            else:
                print("\n❌ 无效选择，请重新输入")
                continue
                
            input("\n按回车键继续...")
            
        except KeyboardInterrupt:
            print("\n\n👋 用户取消，再见！")
            break
        except Exception as e:
            print(f"\n❌ 执行出错: {e}")
            input("按回车键继续...")


if __name__ == "__main__":
    main()
