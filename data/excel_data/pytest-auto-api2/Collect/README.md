# Collect 模块 Excel 数据说明

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
| headers | 请求头 | 否 | JSON字符串 | {"Content-Type": "application/json"} |
| requestType | 请求类型 | 是 | 字符串 | json |
| data | 请求数据 | 否 | JSON字符串 | {"username": "test", "password": "123456"} |
| assert | 断言配置 | 是 | JSON字符串 | {"status_code": 200} |
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
{"Content-Type": "application/json", "Authorization": "Bearer token"}

// 错误格式
Content-Type: application/json
```

### 布尔值格式
- True: 表示真
- False: 表示假
- 空值: null 或留空

### 断言配置格式
```json
{
  "status_code": 200,
  "jsonpath": "$.code", 
  "type": "==",
  "value": 0
}
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
