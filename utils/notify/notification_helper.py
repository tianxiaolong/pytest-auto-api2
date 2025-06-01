#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
通知助手模块

提供统一的通知模板生成和报告链接管理功能
"""

from typing import List, Dict, Any
from utils.other_tools.get_local_ip import get_host_ip
from utils.times_tool.time_control import now_time
from utils import config


class NotificationHelper:
    """通知助手类"""
    
    def __init__(self):
        self.local_ip = get_host_ip()
        self.report_port = 9999
        
    def get_report_urls(self) -> List[str]:
        """
        获取测试报告的多个访问URL
        
        Returns:
            报告URL列表
        """
        return [
            f"http://{self.local_ip}:{self.report_port}/index.html",
            f"http://localhost:{self.report_port}/index.html",
            f"http://127.0.0.1:{self.report_port}/index.html"
        ]
    
    def get_report_info(self) -> Dict[str, Any]:
        """
        获取报告相关信息
        
        Returns:
            包含报告信息的字典
        """
        urls = self.get_report_urls()
        return {
            'urls': urls,
            'primary_url': urls[0],
            'local_path': './report/html/index.html',
            'access_tips': [
                "如果链接1无法访问，请尝试链接2或链接3",
                "或复制链接到浏览器中打开",
                "报告文件位置：./report/html/index.html"
            ]
        }
    
    def format_dingtalk_links(self) -> str:
        """
        格式化钉钉通知的报告链接
        
        Returns:
            格式化后的链接文本
        """
        urls = self.get_report_urls()
        links = "\n".join([f"> 📊 [测试报告链接{i+1}]({url})" for i, url in enumerate(urls)])
        
        tips = (
            "\n\n> 💡 **报告访问说明**："
            "\n> - 如果链接1无法访问，请尝试链接2或链接3"
            "\n> - 或复制链接到浏览器中打开"
            "\n> - 报告文件位置：./report/html/index.html"
        )
        
        return links + tips
    
    def format_wechat_links(self) -> str:
        """
        格式化企业微信通知的报告链接
        
        Returns:
            格式化后的链接文本
        """
        urls = self.get_report_urls()
        links = "\n".join([f">📊 [测试报告链接{i+1}]({url})" for i, url in enumerate(urls)])
        
        tips = (
            "\n>\n>💡 **报告访问说明**："
            "\n>- 如果链接1无法访问，请尝试链接2或链接3"
            "\n>- 或复制链接到浏览器中打开"
            "\n>- 报告文件位置：./report/html/index.html"
        )
        
        return links + tips
    
    def format_email_links(self) -> str:
        """
        格式化邮件通知的报告链接
        
        Returns:
            格式化后的链接文本
        """
        urls = self.get_report_urls()
        links = "\n".join([f"        测试报告链接{i+1}: {url}" for i, url in enumerate(urls)])
        
        tips = (
            "\n        \n        报告访问说明："
            "\n        - 如果链接1无法访问，请尝试链接2或链接3"
            "\n        - 或复制链接到浏览器中打开"
            "\n        - 报告文件位置：./report/html/index.html"
        )
        
        return links + tips
    
    def format_lark_links(self) -> List[Dict[str, str]]:
        """
        格式化飞书通知的报告链接
        
        Returns:
            飞书格式的链接列表
        """
        urls = self.get_report_urls()
        links = []
        
        for i, url in enumerate(urls):
            links.append({"tag": "a", "text": f"测试报告链接{i+1}", "href": url})
            if i < len(urls) - 1:
                links.append({"tag": "text", "text": " | "})
        
        return links
    
    def get_basic_info(self) -> Dict[str, str]:
        """
        获取基本信息
        
        Returns:
            基本信息字典
        """
        return {
            'project_name': config.project_name,
            'tester_name': config.tester_name,
            'environment': 'TEST',
            'current_time': now_time(),
            'local_ip': self.local_ip
        }
    
    def create_summary_text(self, metrics) -> str:
        """
        创建测试结果摘要文本
        
        Args:
            metrics: 测试指标对象
            
        Returns:
            摘要文本
        """
        return (
            f"成功率: {metrics.pass_rate}%\n"
            f"总用例数: {metrics.total}\n"
            f"成功用例数: {metrics.passed}\n"
            f"失败用例数: {metrics.failed}\n"
            f"异常用例数: {metrics.broken}\n"
            f"跳过用例数: {metrics.skipped}\n"
            f"执行时长: {metrics.time}s"
        )
    
    def should_at_all(self, metrics) -> bool:
        """
        判断是否需要@所有人
        
        Args:
            metrics: 测试指标对象
            
        Returns:
            是否需要@所有人
        """
        return (metrics.failed + metrics.broken) > 0


# 全局实例
notification_helper = NotificationHelper()


def get_notification_helper() -> NotificationHelper:
    """
    获取通知助手实例
    
    Returns:
        NotificationHelper实例
    """
    return notification_helper
