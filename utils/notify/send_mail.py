#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Send Mail Module

This module provides send mail functionality.
"""

"""
# @Time   : 2022/3/29 14:57
# @Author : txl
描述: 发送邮件
"""
import smtplib
from email.mime.text import MIMEText

from utils import config
from utils.other_tools.allure_data.allure_report_data import AllureFileClean, TestMetrics


class SendEmail:
    """发送邮箱"""

    def __init__(self, metrics: TestMetrics):
        self.metrics = metrics
        self.allure_data = AllureFileClean()
        self.CaseDetail = self.allure_data.get_failed_cases_detail()

    @classmethod
    def send_mail(cls, user_list: list, sub, content: str) -> None:
        """

        @param user_list: 发件人邮箱
        @param sub:
        @param content: 发送内容
        @return:
        """
        user = "txl" + "<" + config.email.send_user + ">"
        message = MIMEText(content, _subtype="plain", _charset="utf-8")
        message["Subject"] = sub
        message["From"] = user
        message["To"] = ";".join(user_list)
        server = smtplib.SMTP()
        server.connect(config.email.email_host)
        server.login(config.email.send_user, config.email.stamp_key)
        server.sendmail(user, user_list, message.as_string())
        server.close()

    def error_mail(self, error_message: str) -> None:
        """
        执行异常邮件通知
        @param error_message: 报错信息
        @return:
        """
        email = config.email.send_list
        user_list = email.split(",")  # 多个邮箱发送，config文件中直接添加  '806029174@qq.com'

        sub = config.project_name + "接口自动化执行异常通知"
        content = f"自动化测试执行完毕，程序中发现异常，请悉知。报错信息如下：\n{error_message}"
        self.send_mail(user_list, sub, content)

    def send_main(self) -> None:
        """
        发送邮件
        :return:
        """
        from utils.other_tools.get_local_ip import get_host_ip

        email = config.email.send_list
        user_list = email.split(",")  # 多个邮箱发送，yaml文件中直接添加  '806029174@qq.com'

        sub = config.project_name + "接口自动化报告"

        # 获取本地IP和端口，提供多个访问方式
        local_ip = get_host_ip()
        report_urls = [
            f"http://{local_ip}:9999/index.html",
            f"http://localhost:9999/index.html",
            f"http://127.0.0.1:9999/index.html"
        ]

        # 构建报告链接文本
        report_links = "\n".join([f"        测试报告链接{i+1}: {url}" for i, url in enumerate(report_urls)])

        content = f"""
        各位同事, 大家好:
            自动化用例执行完成，执行结果如下:
            用例运行总数: {self.metrics.total} 个
            通过用例个数: {self.metrics.passed} 个
            失败用例个数: {self.metrics.failed} 个
            异常用例个数: {self.metrics.broken} 个
            跳过用例个数: {self.metrics.skipped} 个
            成  功   率: {self.metrics.pass_rate} %
            用例执行时长: {self.metrics.time} s

        {self.allure_data.get_failed_cases_detail()}

        **********************************
        测试报告访问地址：
{report_links}

        报告访问说明：
        - 如果链接1无法访问，请尝试链接2或链接3
        - 或复制链接到浏览器中打开
        - 报告文件位置：./report/html/index.html

        详细情况可查看测试报告，非相关负责人员可忽略此消息。谢谢。
        """
        self.send_mail(user_list, sub, content)


if __name__ == "__main__":
    SendEmail(AllureFileClean().get_case_count()).send_main()
