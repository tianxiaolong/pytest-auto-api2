#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Create Excel Template Module

This module provides create excel template functionality.
"""

"""
Excel数据模板创建脚本
创建标准的Excel测试数据模板文件

@Time   : 2023-12-20
@Author : txl
"""
import json
from pathlib import Path

import pandas as pd


def create_excel_template(output_path: str, module_name: str = "Login"):
    """
    创建Excel测试数据模板

    Args:
        output_path: 输出文件路径
        module_name: 模块名称
    """
    # 创建输出目录
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 公共配置数据
    common_config_data = {
        "key": ["allureEpic", "allureFeature", "allureStory"],
        "value": ["开发平台接口", f"{module_name}模块", f"{module_name}功能测试"],
    }

    # 测试用例数据
    test_cases_data = {
        "case_id": ["login_001", "login_002", "login_003"],
        "detail": ["正常登录测试", "用户名错误测试", "密码错误测试"],
        "url": ["/api/login", "/api/login", "/api/login"],
        "method": ["POST", "POST", "POST"],
        "headers": [
            '{"Content-Type": "application/json"}',
            '{"Content-Type": "application/json"}',
            '{"Content-Type": "application/json"}',
        ],
        "requestType": ["json", "json", "json"],
        "data": [
            '{"username": "test_user", "password": "123456"}',
            '{"username": "wrong_user", "password": "123456"}',
            '{"username": "test_user", "password": "wrong_password"}',
        ],
        "assert": [
            '{"status_code": 200, "jsonpath": "$.code", "type": "==", "value": 0}',
            '{"status_code": 200, "jsonpath": "$.code", "type": "==", "value": -1}',
            '{"status_code": 200, "jsonpath": "$.code", "type": "==", "value": -1}',
        ],
        "is_run": [True, True, True],
        "dependence_case": [False, False, False],
        "dependence_case_data": [None, None, None],
        "sql": [None, None, None],
        "setup_sql": [None, None, None],
        "teardown_sql": [None, None, None],
        "teardown": [None, None, None],
        "current_request_set_cache": [None, None, None],
        "sleep": [None, None, None],
    }

    # 创建DataFrame
    common_df = pd.DataFrame(common_config_data)
    test_cases_df = pd.DataFrame(test_cases_data)

    # 写入Excel文件
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        common_df.to_excel(writer, sheet_name="case_common", index=False)
        test_cases_df.to_excel(writer, sheet_name="test_cases", index=False)

    print(f"✅ Excel模板已创建: {output_file}")

    # 创建说明文档
    readme_content = """# {module_name} 模块 Excel 数据说明

## 文件结构

### 1. case_common Sheet
公共配置信息，包含Allure报告的标签配置：
- allureEpic: 史诗级别标签
- allureFeature: 功能级别标签
- allureStory: 用户故事标签

### 2. test_cases Sheet
测试用例数据，包含以下字段：

| 字段名 | 说明 | 必填 | 数据类型 | 示例 |
|--------|------|------|----------|------|
| case_id | 用例ID | 是 | 字符串 | login_001 |
| detail | 用例描述 | 是 | 字符串 | 正常登录测试 |
| url | 接口地址 | 是 | 字符串 | /api/login |
| method | 请求方法 | 是 | 字符串 | POST |
| headers | 请求头 | 否 | JSON字符串 | {{"Content-Type": "application/json"}} |
| requestType | 请求类型 | 是 | 字符串 | json |
| data | 请求数据 | 否 | JSON字符串 | {{"username": "test", "password": "123456"}} |
| assert | 断言配置 | 是 | JSON字符串 | {{"status_code": 200}} |
| is_run | 是否执行 | 否 | 布尔值 | True |
| dependence_case | 是否有依赖 | 否 | 布尔值 | False |
| dependence_case_data | 依赖数据 | 否 | JSON字符串 | null |
| sql | SQL查询 | 否 | JSON字符串 | null |
| setup_sql | 前置SQL | 否 | JSON字符串 | null |
| teardown_sql | 后置SQL | 否 | JSON字符串 | null |
| teardown | 后置处理 | 否 | JSON字符串 | null |
| current_request_set_cache | 缓存设置 | 否 | JSON字符串 | null |
| sleep | 等待时间 | 否 | 数字 | null |

## 数据格式说明

### JSON字符串格式
对于复杂数据类型（如headers、data、assert等），需要使用JSON字符串格式：

```json
// 正确格式
{{"Content-Type": "application/json", "Authorization": "Bearer token"}}

// 错误格式
Content-Type: application/json
```

### 布尔值格式
- True: 表示真
- False: 表示假
- 空值: null 或留空

### 断言配置格式
```json
{{
  "status_code": 200,
  "jsonpath": "$.code",
  "type": "==",
  "value": 0
}}
```

## 使用方式

1. 在配置文件中设置 `data_driver_type: excel`
2. 将Excel文件放在 `data/excel_data/项目名/模块名/` 目录下
3. 运行测试用例即可自动读取Excel数据

## 注意事项

1. 所有JSON字符串必须是有效的JSON格式
2. 布尔值请使用True/False（注意大小写）
3. 空值请使用null或留空
4. case_id必须唯一
5. 必填字段不能为空
"""

    readme_file = output_file.parent / "README.md"
    with open(readme_file, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"✅ 说明文档已创建: {readme_file}")


def create_multiple_templates():
    """创建多个模块的Excel模板"""
    modules = [("Login", "登录"), ("UserInfo", "用户信息"), ("Collect", "收藏"), ("Tool", "工具")]

    base_path = "data/excel_data/pytest-auto-api2"

    for module_en, module_cn in modules:
        output_path = f"{base_path}/{module_en}/{module_en.lower()}_test_data.xlsx"
        create_excel_template(output_path, module_en)
        print(f"📁 {module_cn}模块模板创建完成")

    print("\n🎉 所有Excel模板创建完成！")
    print(f"📂 模板位置: {base_path}")
    print("\n📋 后续步骤:")
    print("1. 根据实际需求修改Excel文件中的测试数据")
    print("2. 在配置文件中设置 data_driver_type: excel")
    print("3. 运行测试用例验证Excel数据驱动功能")


if __name__ == "__main__":
    try:
        create_multiple_templates()
    except ImportError:
        print("❌ 需要安装pandas和openpyxl库:")
        print("pip install pandas openpyxl")
    except Exception as e:
        print(f"❌ 创建模板失败: {e}")
