#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests

from utils import config
from utils.logging_tool.log_control import ERROR
from utils.other_tools.allure_data.allure_report_data import AllureFileClean, TestMetrics
from utils.other_tools.exceptions import SendMessageError, ValueTypeError
from utils.other_tools.get_local_ip import get_host_ip
from utils.times_tool.time_control import now_time

"""
# @Time   : 2022/3/29 14:59
# @Author : txl
描述: 发送企业微信通知
"""


class WeChatSend:
    """
    企业微信消息通知
    """

    def __init__(self, metrics: TestMetrics):
        self.metrics = metrics
        self.headers = {"Content-Type": "application/json"}

    def send_text(self, content, mentioned_mobile_list=None):
        """
        发送文本类型通知
        :param content: 文本内容，最长不超过2048个字节，必须是utf8编码
        :param mentioned_mobile_list: 手机号列表，提醒手机号对应的群成员(@某个成员)，@all表示提醒所有人
        :return:
        """
        _data = {
            "msgtype": "text",
            "text": {"content": content, "mentioned_list": None, "mentioned_mobile_list": mentioned_mobile_list},
        }

        if mentioned_mobile_list is None or isinstance(mentioned_mobile_list, list):
            # 判断手机号码列表中得数据类型，如果为int类型，发送得消息会乱码
            if len(mentioned_mobile_list) >= 1:
                for i in mentioned_mobile_list:
                    if isinstance(i, str):
                        res = requests.post(url=config.wechat.webhook, json=_data, headers=self.headers)
                        if res.json()["errcode"] != 0:
                            ERROR.logger.error(res.json())
                            raise SendMessageError("企业微信「文本类型」消息发送失败")

                    else:
                        raise ValueTypeError("手机号码必须是字符串类型.")
        else:
            raise ValueTypeError("手机号码列表必须是list类型.")

    def send_markdown(self, content):
        """
        发送 MarkDown 类型消息
        :param content: 消息内容，markdown形式
        :return:
        """
        _data = {"msgtype": "markdown", "markdown": {"content": content}}
        res = requests.post(url=config.wechat.webhook, json=_data, headers=self.headers)
        if res.json()["errcode"] != 0:
            ERROR.logger.error(res.json())
            raise SendMessageError("企业微信「MarkDown类型」消息发送失败")

    def _upload_file(self, file):
        """
        先将文件上传到临时媒体库
        """
        key = config.wechat.webhook.split("key=")[1]
        url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={key}&type=file"
        data = {"file": open(file, "rb")}
        res = requests.post(url, files=data).json()
        return res["media_id"]

    def send_file_msg(self, file):
        """
        发送文件类型的消息
        @return:
        """

        _data = {"msgtype": "file", "file": {"media_id": self._upload_file(file)}}
        res = requests.post(url=config.wechat.webhook, json=_data, headers=self.headers)
        if res.json()["errcode"] != 0:
            ERROR.logger.error(res.json())
            raise SendMessageError("企业微信「file类型」消息发送失败")

    def send_wechat_notification(self, use_enhanced_format: bool = True):
        """
        发送企业微信通知

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
        """发送增强格式的企业微信通知"""
        try:
            from utils.notify.enhanced_notification_formatter import format_simple_notification

            # 使用增强格式化器
            enhanced_content = format_simple_notification(self.metrics)
            self.send_markdown(enhanced_content)

        except ImportError as e:
            # 如果导入失败，回退到原始格式
            print(f"⚠️ 增强格式化器导入失败，使用原始格式: {e}")
            self._send_legacy_notification()
        except Exception as e:
            # 如果增强格式化失败，回退到原始格式
            print(f"⚠️ 增强格式化失败，使用原始格式: {e}")
            self._send_legacy_notification()

    def _send_legacy_notification(self):
        """发送原始格式的企业微信通知（保持向后兼容）"""
        # 获取本地IP和端口，提供多个访问方式
        local_ip = get_host_ip()
        report_urls = [
            f"http://{local_ip}:9999/index.html",
            f"http://localhost:9999/index.html",
            f"http://127.0.0.1:9999/index.html"
        ]

        # 构建报告链接文本
        report_links = "\n".join([f">📊 [测试报告链接{i + 1}]({url})" for i, url in enumerate(report_urls)])

        text = f"""【{config.project_name}自动化通知】
        >测试环境：<font color="info">TEST</font>
        >测试负责人：@{config.tester_name}
        >
        > **执行结果**
        ><font color="info">成  功  率  : {self.metrics.pass_rate}%</font>
        >用例  总数：<font color="info">{self.metrics.total}</font>
        >成功用例数：<font color="info">{self.metrics.passed}</font>
        >失败用例数：`{self.metrics.failed}个`
        >异常用例数：`{self.metrics.broken}个`
        >跳过用例数：<font color="warning">{self.metrics.skipped}个</font>
        >用例执行时长：<font color="warning">{self.metrics.time} s</font>
        >时间：<font color="comment">{now_time()}</font>
        >
        >非相关负责人员可忽略此消息。
        {report_links}
        >
        >💡 **报告访问说明**：
        >- 如果链接1无法访问，可以尝试链接2或链接3
        >- 或复制链接到浏览器中打开
        >- 报告文件位置：./report/html/index.html"""

        self.send_markdown(text)


if __name__ == "__main__":
    WeChatSend(AllureFileClean().get_case_count()).send_wechat_notification()
