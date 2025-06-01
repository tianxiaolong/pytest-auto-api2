#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run Module

This module provides run functionality.
"""
from utils.read_files_tools.enhanced_case_automatic_control import EnhancedTestCaseGenerator

"""
run module
Provides functionality for run
"""
import os
import sys
import traceback

import pytest

from utils import config
from utils.logging_tool.log_control import INFO
from utils.notify.ding_talk import DingTalkSendMsg
from utils.notify.lark import FeiShuTalkChatBot
from utils.notify.send_mail import SendEmail
from utils.notify.wechat_send import WeChatSend
from utils.other_tools.allure_data.allure_report_data import AllureFileClean
from utils.other_tools.models import NotificationType

# 导入新的命令行和环境管理模块
from common.cli_parser import get_cli_parser, parse_command_line_args
from common.environment_manager import get_environment_manager

try:
    from utils.other_tools.allure_data.error_case_excel import ErrorCaseExcel
    EXCEL_REPORT_AVAILABLE = True
except ImportError:
    EXCEL_REPORT_AVAILABLE = False
    print("警告: Excel 报告功能不可用，xlwings 依赖缺失")


def run(args=None) -> None:
    """
    主运行函数

    执行完整的自动化测试流程，包括：
    1. 解析命令行参数
    2. 配置运行环境
    3. 显示项目启动信息
    4. 执行pytest测试用例
    5. 生成Allure测试报告
    6. 发送测试结果通知
    7. 生成Excel错误报告（可选）
    8. 异常处理和邮件通知

    支持的通知方式：
    - 钉钉通知
    - 企业微信通知
    - 邮箱通知
    - 飞书通知

    异常处理：
    - 自动捕获运行异常
    - 发送异常邮件通知
    - 保证程序稳定性

    Args:
        args: 命令行参数，用于测试或程序化调用
    """
    try:
        # 1. 解析命令行参数
        cli_parser = get_cli_parser()
        parsed_args = cli_parser.parse_args(args)

        # 2. 应用命令行参数到环境变量
        applied_vars = cli_parser.apply_args_to_environment(parsed_args)

        # 3. 设置环境管理器
        env_manager = get_environment_manager()
        if parsed_args.env:
            env_manager.set_environment(parsed_args.env)

        # 4. 打印配置摘要
        if not parsed_args.quiet:
            cli_parser.print_configuration_summary(parsed_args, applied_vars)
            env_manager.print_current_environment_info()

        # 5. 模拟运行模式
        if parsed_args.dry_run:
            print("\n🧪 模拟运行模式 - 不执行实际测试")
            pytest_args = cli_parser.build_pytest_args(parsed_args)
            print(f"📝 将要执行的pytest命令: pytest {' '.join(pytest_args)}")
            return

        INFO.logger.info(
            """
                             _    _         _      _____         _
              __ _ _ __ (_)  / \\  _   _| |_ __|_   _|__  ___| |_
             / _` | '_ \\| | / _ \\| | | | __/ _ \\| |/ _ \\/ __| __|
            | (_| | |_) | |/ ___ \\ |_| | || (_) | |  __/\\__ \\ |_
             \\__,_| .__/|_/_/   \\_\\__,_|\\__\\___/|_|\\___||___/\\__|
                  |_|
                  开始执行{}项目...
                """.format(
                config.project_name
            )
        )

        # 6. 测试用例生成
        if not parsed_args.no_generate:
            generator = EnhancedTestCaseGenerator()

            # 清理过时文件
            if parsed_args.clean_obsolete:
                cleaned_files = generator.clean_obsolete_files()
                if cleaned_files:
                    INFO.logger.info(f"🧹 清理了 {len(cleaned_files)} 个过时文件")

            # 生成测试用例
            result = generator.generate_all_test_cases(
                force_update=parsed_args.force_generate,
                check_changes=not parsed_args.force_generate
            )

            # 输出生成结果
            if result['generated_files'] > 0:
                INFO.logger.info(f"✅ 生成了 {result['generated_files']} 个测试文件")
            elif result['skipped_files'] > 0:
                INFO.logger.info(f"⏭️ 跳过了 {result['skipped_files']} 个文件（无变化）")
        else:
            INFO.logger.info("⏭️ 跳过测试用例生成")

        # 7. 执行pytest测试
        pytest_args = cli_parser.build_pytest_args(parsed_args)
        INFO.logger.info(f"🧪 执行pytest命令: pytest {' '.join(pytest_args)}")
        pytest.main(pytest_args)

        # 8. 生成Allure报告
        INFO.logger.info("📊 生成Allure测试报告...")

        # 生成带时间戳的报告目录
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamped_report_dir = f"./report/html_{timestamp}"

        # 生成报告到带时间戳的目录
        os.system(f'allure generate ./report/tmp -o {timestamped_report_dir} --clean')

        # 检查是否需要生成默认报告（向后兼容）
        generate_default_report = getattr(config, 'generate_default_report', True)

        if generate_default_report:
            # 同时生成到默认目录（保持向后兼容）
            os.system(r"allure generate ./report/tmp -o ./report/html --clean")
            INFO.logger.info(f"📊 报告已生成:")
            INFO.logger.info(f"   📁 带时间戳: {timestamped_report_dir}/index.html")
            INFO.logger.info(f"   📁 默认位置: ./report/html/index.html")
        else:
            INFO.logger.info(f"📊 报告已生成:")
            INFO.logger.info(f"   📁 带时间戳: {timestamped_report_dir}/index.html")
            INFO.logger.info(f"   ℹ️ 默认报告已禁用 (generate_default_report=False)")

        # 9. 发送通知
        allure_data = AllureFileClean().get_case_count()

        # 检查是否使用增强通知格式
        use_enhanced_format = getattr(config, 'enhanced_notification', True)

        # 为通知系统添加时间戳信息
        if hasattr(allure_data, '__dict__'):
            allure_data.timestamp = timestamp
        else:
            # 如果是其他类型的对象，尝试设置属性
            try:
                setattr(allure_data, 'timestamp', timestamp)
            except:
                pass

        notification_mapping = {
            NotificationType.DING_TALK.value: lambda: DingTalkSendMsg(allure_data).send_ding_notification(use_enhanced_format),
            NotificationType.WECHAT.value: lambda: WeChatSend(allure_data).send_wechat_notification(use_enhanced_format),
            NotificationType.EMAIL.value: SendEmail(allure_data).send_main,
            NotificationType.FEI_SHU.value: FeiShuTalkChatBot(allure_data).post,
        }

        # 根据命令行参数或配置发送通知
        notification_type = config.notification_type
        if parsed_args.notification:
            # 命令行参数优先
            notification_mapping_cli = {
                'dingtalk': NotificationType.DING_TALK.value,
                'wechat': NotificationType.WECHAT.value,
                'email': NotificationType.EMAIL.value,
                'lark': NotificationType.FEI_SHU.value,
                'all': '1,2,3,4'
            }
            notification_type = notification_mapping_cli.get(parsed_args.notification, '0')

        if notification_type != NotificationType.DEFAULT.value:
            notify_types = notification_type.split(",")

            for notify_type in notify_types:
                notify_type_clean = notify_type.strip()
                notification_func = notification_mapping.get(notify_type_clean)

                if notification_func is not None:
                    try:
                        notification_func()
                        # 获取通知类型名称用于日志
                        type_names = {
                            NotificationType.DING_TALK.value: "钉钉",
                            NotificationType.WECHAT.value: "企业微信",
                            NotificationType.EMAIL.value: "邮件",
                            NotificationType.FEI_SHU.value: "飞书"
                        }
                        type_name = type_names.get(notify_type_clean, f"类型{notify_type_clean}")
                        INFO.logger.info(f"✅ {type_name}通知发送成功")
                    except Exception as e:
                        INFO.logger.error(f"❌ 通知发送失败 (类型: {notify_type_clean}): {e}")
                else:
                    print(f"⚠️ 未知的通知类型: '{notify_type_clean}'，跳过通知发送")
                    print(f"   支持的通知类型: 1(钉钉), 2(企业微信), 3(邮件), 4(飞书)")

        # 10. 生成Excel报告（可选）
        if (parsed_args.excel_report or config.excel_report) and EXCEL_REPORT_AVAILABLE:
            INFO.logger.info("📊 生成Excel错误报告...")
            ErrorCaseExcel().write_case()
        elif (parsed_args.excel_report or config.excel_report) and not EXCEL_REPORT_AVAILABLE:
            print("⚠️ 跳过 Excel 报告生成：xlwings 依赖缺失")

        # 11. 启动Allure报告服务（可选）
        if not parsed_args.no_allure_serve:
            port = parsed_args.allure_port
            INFO.logger.info(f"🌐 启动Allure报告服务:")
            INFO.logger.info(f"   🌍 默认报告: http://127.0.0.1:{port}")
            INFO.logger.info(f"   📅 带时间戳报告: {timestamped_report_dir}/index.html")
            os.system(f"allure serve ./report/tmp -h 127.0.0.1 -p {port}")

    except Exception as e:
        # 如有异常，相关异常发送邮件
        error_msg = traceback.format_exc()
        INFO.logger.error(f"❌ 程序执行异常: {error_msg}")

        try:
            send_email = SendEmail(AllureFileClean.get_case_count())
            # send_email.error_mail(error_msg)  # 可以启用邮件通知
        except Exception as email_error:
            INFO.logger.error(f"❌ 邮件通知发送失败: {email_error}")

        raise


def main():
    """主入口函数，支持命令行调用"""
    try:
        run()
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断执行")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 程序执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
