#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ding Talk Module

This module provides ding talk functionality.
"""

# @Time   : 2022/3/28 15:30
# @Author : txl
"""
钉钉通知封装
"""
import base64
import hashlib
import hmac
import time
import urllib.parse
from typing import Any, Text

from dingtalkchatbot.chatbot import DingtalkChatbot, FeedLink

from utils import config
from utils.other_tools.allure_data.allure_report_data import AllureFileClean, TestMetrics
from utils.other_tools.get_local_ip import get_host_ip


class DingTalkSendMsg:
    """发送钉钉通知"""

    def __init__(self, metrics: TestMetrics):
        self.metrics = metrics
        self.timeStamp = str(round(time.time() * 1000))

    def xiao_ding(self):
        """
        创建钉钉机器人实例

        根据配置信息和签名创建钉钉聊天机器人实例。

        Returns:
            DingtalkChatbot: 钉钉机器人实例
        """
        sign = self.get_sign()
        # 从yaml文件中获取钉钉配置信息
        webhook = config.ding_talk.webhook + "&timestamp=" + self.timeStamp + "&sign=" + sign
        return DingtalkChatbot(webhook)

    def get_sign(self) -> Text:
        """
        根据时间戳 + "sign" 生成密钥
        :return:
        """
        string_to_sign = f"{self.timeStamp}\n{config.ding_talk.secret}".encode("utf-8")
        hmac_code = hmac.new(config.ding_talk.secret.encode("utf-8"), string_to_sign, digestmod=hashlib.sha256).digest()

        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return sign

    def send_text(self, msg: Text, mobiles=None) -> None:
        """
        发送文本信息
        :param msg: 文本内容
        :param mobiles: 艾特用户电话
        :return:
        """
        if not mobiles:
            self.xiao_ding().send_text(msg=msg, is_at_all=True)
        else:
            if isinstance(mobiles, list):
                self.xiao_ding().send_text(msg=msg, at_mobiles=mobiles)
            else:
                raise TypeError("mobiles类型错误 不是list类型.")

    def send_link(self, title: Text, text: Text, message_url: Text, pic_url: Text) -> None:
        """
        发送link通知
        :return:
        """
        self.xiao_ding().send_link(title=title, text=text, message_url=message_url, pic_url=pic_url)

    def send_markdown(self, title: Text, msg: Text, mobiles=None, is_at_all=False) -> None:
        """

        :param is_at_all:
        :param mobiles:
        :param title:
        :param msg:
        markdown 格式
        """

        if mobiles is None:
            self.xiao_ding().send_markdown(title=title, text=msg, is_at_all=is_at_all)
        else:
            if isinstance(mobiles, list):
                self.xiao_ding().send_markdown(title=title, text=msg, at_mobiles=mobiles)
            else:
                raise TypeError("mobiles类型错误 不是list类型.")

    @staticmethod
    def feed_link(title: Text, message_url: Text, pic_url: Text) -> Any:
        """FeedLink 二次封装"""
        return FeedLink(title=title, message_url=message_url, pic_url=pic_url)

    def send_feed_link(self, *arg) -> None:
        """发送 feed_lik"""

        self.xiao_ding().send_feed_card(list(arg))

    def send_ding_notification(self, use_enhanced_format: bool = True):
        """
        发送钉钉报告通知

        Args:
            use_enhanced_format: 是否使用增强格式，默认True
        """
        if use_enhanced_format:
            # 使用增强格式
            self._send_enhanced_notification()
        else:
            # 使用原始格式（保持向后兼容）
            self._send_legacy_notification()

    def _send_enhanced_notification(self):
        """发送增强格式的钉钉通知"""
        try:
            from utils.notify.enhanced_notification_formatter import format_simple_notification

            # 判断如果有失败的用例，@所有人
            is_at_all = False
            if self.metrics.failed + self.metrics.broken > 0:
                is_at_all = True

            # 使用增强格式化器，并转换为钉钉markdown格式
            enhanced_content = format_simple_notification(self.metrics)
            dingtalk_content = self._convert_to_dingtalk_markdown(enhanced_content)

            self.send_markdown(title="【接口自动化通知】", msg=dingtalk_content, is_at_all=is_at_all)

        except ImportError as e:
            # 如果导入失败，回退到原始格式
            print(f"⚠️ 增强格式化器导入失败，使用原始格式: {e}")
            self._send_legacy_notification()
        except Exception as e:
            # 如果增强格式化失败，回退到原始格式
            print(f"⚠️ 增强格式化失败，使用原始格式: {e}")
            self._send_legacy_notification()

    def _convert_to_dingtalk_markdown(self, content: str) -> str:
        """
        将通用markdown格式转换为钉钉支持的markdown格式

        Args:
            content: 通用markdown内容

        Returns:
            钉钉格式的markdown内容
        """
        # 钉钉markdown格式调整
        dingtalk_content = content.replace("# ", "#### ")  # 钉钉使用####作为标题
        dingtalk_content = dingtalk_content.replace("## ", "> **")  # 二级标题转换
        dingtalk_content = dingtalk_content.replace("**", "")  # 移除加粗标记，钉钉不支持

        # 添加钉钉特有的图片
        dingtalk_content += (
            "\n\n ![screenshot]("
            "https://img.alicdn.com/tfs/TB1NwmBEL9TBuNjy1zbXXXpepXa-2400-1218.png"
            ")"
        )

        return dingtalk_content

    def _send_legacy_notification(self):
        """发送原始格式的钉钉通知（保持向后兼容）"""
        # 判断如果有失败的用例，@所有人
        is_at_all = False
        if self.metrics.failed + self.metrics.broken > 0:
            is_at_all = True

        # 获取本地IP和端口，提供多个访问方式
        local_ip = get_host_ip()
        report_urls = [
            f"http://{local_ip}:9999/index.html",
            f"http://localhost:9999/index.html",
            f"http://127.0.0.1:9999/index.html"
        ]

        # 构建报告链接文本
        report_links = "\n".join([f"> 📊 [测试报告链接{i+1}]({url})" for i, url in enumerate(report_urls)])

        text = (
            f"#### {config.project_name}自动化通知  "
            f"\n\n>Python脚本任务: {config.project_name}"
            "\n\n>环境: TEST\n\n>"
            f"执行人: {config.tester_name}"
            f"\n\n>执行结果: {self.metrics.pass_rate}% "
            f"\n\n>总用例数: {self.metrics.total} "
            f"\n\n>成功用例数: {self.metrics.passed}"
            f" \n\n>失败用例数: {self.metrics.failed} "
            f" \n\n>异常用例数: {self.metrics.broken} "
            f"\n\n>跳过用例数: {self.metrics.skipped}"
            f"\n\n>用例执行时长: {self.metrics.time} s"
            " ![screenshot]("
            "https://img.alicdn.com/tfs/TB1NwmBEL9TBuNjy1zbXXXpepXa-2400-1218.png"
            ")\n\n"
            f"{report_links}"
            "\n\n> 💡 **报告访问说明**："
            "\n> - 如果链接1无法访问，请尝试链接2或链接3"
            "\n> - 或复制链接到浏览器中打开"
            "\n> - 报告文件位置：./report/html/index.html"
            "\n\n>非相关负责人员可忽略此消息。"
        )
        self.send_markdown(title="【接口自动化通知】", msg=text, is_at_all=is_at_all)


if __name__ == "__main__":
    DingTalkSendMsg(AllureFileClean().get_case_count()).send_ding_notification()
