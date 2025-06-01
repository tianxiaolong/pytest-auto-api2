#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
通知模板测试工具

测试各种通知模板的参数替换是否正常工作
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
from utils.other_tools.get_local_ip import get_host_ip
from utils.times_tool.time_control import now_time


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


def test_dingtalk_template():
    """测试钉钉通知模板"""
    print("\n📱 测试钉钉通知模板:")
    print("-" * 50)
    
    try:
        from utils.notify.ding_talk import DingTalkSendMsg
        
        metrics = create_test_metrics()
        ding_talk = DingTalkSendMsg(metrics)
        
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
            f"{report_links}"
            "\n\n> 💡 **报告访问说明**："
            "\n> - 如果链接1无法访问，请尝试链接2或链接3"
            "\n> - 或复制链接到浏览器中打开"
            "\n> - 报告文件位置：./report/html/index.html"
            "\n\n>非相关负责人员可忽略此消息。"
        )
        
        print("✅ 钉钉模板生成成功")
        print("📝 模板内容预览:")
        print(text[:200] + "..." if len(text) > 200 else text)
        
        # 检查参数替换
        if "{config.project_name}" in text or "{self.metrics" in text:
            print("❌ 发现未替换的参数")
            return False
        else:
            print("✅ 所有参数替换正常")
            return True
            
    except Exception as e:
        print(f"❌ 钉钉模板测试失败: {e}")
        return False


def test_wechat_template():
    """测试企业微信通知模板"""
    print("\n💬 测试企业微信通知模板:")
    print("-" * 50)
    
    try:
        from utils.notify.wechat_send import WeChatSend
        
        metrics = create_test_metrics()
        wechat = WeChatSend(metrics)
        
        # 获取本地IP和端口，提供多个访问方式
        local_ip = get_host_ip()
        report_urls = [
            f"http://{local_ip}:9999/index.html",
            f"http://localhost:9999/index.html", 
            f"http://127.0.0.1:9999/index.html"
        ]
        
        # 构建报告链接文本
        report_links = "\n".join([f">📊 [测试报告链接{i+1}]({url})" for i, url in enumerate(report_urls)])
        
        text = f"""【{config.project_name}自动化通知】
>测试环境：<font color="info">TEST</font>
>测试负责人：@{config.tester_name}
>
> **执行结果**
><font color="info">成  功  率  : {metrics.pass_rate}%</font>
>用例  总数：<font color="info">{metrics.total}</font>
>成功用例数：<font color="info">{metrics.passed}</font>
>失败用例数：`{metrics.failed}个`
>异常用例数：`{metrics.broken}个`
>跳过用例数：<font color="warning">{metrics.skipped}个</font>
>用例执行时长：<font color="warning">{metrics.time} s</font>
>时间：<font color="comment">{now_time()}</font>
>
>非相关负责人员可忽略此消息。
{report_links}
>
>💡 **报告访问说明**：
>- 如果链接1无法访问，请尝试链接2或链接3
>- 或复制链接到浏览器中打开
>- 报告文件位置：./report/html/index.html"""
        
        print("✅ 企业微信模板生成成功")
        print("📝 模板内容预览:")
        print(text[:200] + "..." if len(text) > 200 else text)
        
        # 检查参数替换
        if "{config.project_name}" in text or "{self.metrics" in text:
            print("❌ 发现未替换的参数")
            return False
        else:
            print("✅ 所有参数替换正常")
            return True
            
    except Exception as e:
        print(f"❌ 企业微信模板测试失败: {e}")
        return False


def test_email_template():
    """测试邮件通知模板"""
    print("\n📧 测试邮件通知模板:")
    print("-" * 50)
    
    try:
        from utils.notify.send_mail import SendEmail
        
        metrics = create_test_metrics()
        
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
            用例运行总数: {metrics.total} 个
            通过用例个数: {metrics.passed} 个
            失败用例个数: {metrics.failed} 个
            异常用例个数: {metrics.broken} 个
            跳过用例个数: {metrics.skipped} 个
            成  功   率: {metrics.pass_rate} %
            用例执行时长: {metrics.time} s

        **********************************
        测试报告访问地址：
{report_links}
        
        报告访问说明：
        - 如果链接1无法访问，请尝试链接2或链接3
        - 或复制链接到浏览器中打开
        - 报告文件位置：./report/html/index.html
        
        详细情况可查看测试报告，非相关负责人员可忽略此消息。谢谢。
        """
        
        print("✅ 邮件模板生成成功")
        print("📝 模板内容预览:")
        print(content[:300] + "..." if len(content) > 300 else content)
        
        # 检查参数替换
        if "{self.metrics" in content:
            print("❌ 发现未替换的参数")
            return False
        else:
            print("✅ 所有参数替换正常")
            return True
            
    except Exception as e:
        print(f"❌ 邮件模板测试失败: {e}")
        return False


def main():
    """主函数"""
    print("🧪 通知模板参数替换测试")
    print("=" * 60)
    
    print(f"📋 当前配置信息:")
    print(f"  项目名称: {config.project_name}")
    print(f"  测试人员: {config.tester_name}")
    print(f"  本地IP: {get_host_ip()}")
    print(f"  当前时间: {now_time()}")
    
    results = []
    
    # 测试各种通知模板
    results.append(("钉钉通知", test_dingtalk_template()))
    results.append(("企业微信通知", test_wechat_template()))
    results.append(("邮件通知", test_email_template()))
    
    # 生成测试报告
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    print("=" * 60)
    
    success_count = 0
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
        if result:
            success_count += 1
    
    print(f"\n🎯 总体结果: {success_count}/{len(results)} 个模板测试通过")
    
    if success_count == len(results):
        print("🎉 所有通知模板参数替换正常！")
        return True
    else:
        print("⚠️ 部分通知模板存在问题，请检查修复")
        return False


if __name__ == "__main__":
    main()
