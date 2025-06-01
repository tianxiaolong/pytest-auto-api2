# pytest-auto-api2

<div align="center">

🚀 **企业级接口自动化测试框架**

*基于 Python + pytest + allure + 双数据驱动的现代化接口测试解决方案*

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![pytest](https://img.shields.io/badge/pytest-7.1%2B-green.svg)](https://pytest.org/)
[![allure](https://img.shields.io/badge/allure-2.9%2B-orange.svg)](https://docs.qameta.io/allure/)
[![Docker](https://img.shields.io/badge/Docker-支持-blue.svg)](https://www.docker.com/)
[![Jenkins](https://img.shields.io/badge/Jenkins-集成-brightgreen.svg)](https://www.jenkins.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[快速开始](#-快速开始) • [功能特色](#-框架特色) • [使用指南](#-使用指南) • [API文档](#-api文档) • [贡献指南](#-贡献指南)

</div>

---

## 🆕 最新更新

### 🎉 **v2.1.0 新功能亮点**

- **📈 历史趋势分析**: 智能对比历史数据，显示成功率变化趋势和改进建议
- **📅 带时间戳报告**: 每次执行生成独立的时间戳报告，便于历史追溯和版本对比
- **🎨 增强通知格式**: 企业级美观通知，包含智能告警级别和性能指标评估
- **⏰ 图标优化升级**: 优化通知图标体系，解决企业微信显示问题，提升视觉效果
- **🔄 数据一致性修复**: 解决通知系统与Allure报告成功率不一致问题
- **🛠️ 专业报告管理**: 提供报告清理、归档、统计等企业级管理功能
- **🚨 5级智能告警**: 自动判断测试质量，从🔴特别严重到🟢正常的告警体系

## 🌟 框架特色

**pytest-auto-api2** 是一个功能完整、生产就绪的企业级接口自动化测试框架，专为现代化测试团队设计：

### 🎯 **双数据驱动架构**

- **YAML数据驱动**: 开发友好的结构化数据格式，支持复杂数据结构
- **Excel数据驱动**: 业务友好的表格格式，测试人员零代码维护
- **智能切换**: 运行时动态切换数据源，无需修改测试代码
- **数据一致性**: 自动验证和同步两种数据源的一致性

### 🏗️ **多环境支持**

- **环境隔离**: 支持test/staging/prod多环境配置
- **动态切换**: 命令行参数一键切换运行环境
- **配置管理**: 独立的环境配置文件，支持敏感信息加密
- **CI/CD集成**: 完美支持Jenkins参数化构建

### 🔧 **企业级功能**

- **接口依赖**: 支持复杂的接口依赖关系和数据传递
- **智能断言**: JSON响应断言、数据库断言、自定义断言引擎
- **失败重试**: 可配置的自动重试机制，提高测试稳定性
- **并发执行**: 支持多进程并发测试，大幅提升执行效率
- **缓存机制**: 智能缓存接口响应，支持跨用例数据共享

### 📊 **完善的报告体系**

- **📅 带时间戳报告**: 每次执行生成独立的时间戳报告，便于历史追溯和版本对比
- **🔄 双报告策略**: 同时生成默认报告和时间戳报告，保持向后兼容
- **📈 Allure报告**: 美观的HTML测试报告，支持历史趋势分析
- **📝 实时日志**: 彩色分级日志输出，支持文件和控制台双输出
- **📊 Excel报告**: 失败用例详细分析报告，便于问题追踪
- **📋 统计分析**: 用例成功率、执行时长、性能指标等详细统计
- **🛠️ 报告管理**: 专业的报告管理工具，支持清理、归档、统计功能

### 🔔 **智能通知系统**

- **🎨 增强通知格式**: 企业级美观通知，包含智能告警级别、趋势分析、性能指标
- **⏰ 优化图标体系**: 精心设计的图标系统，解决企业微信显示问题，提升视觉识别度
- **📊 智能告警级别**: 5级告警体系（🔴特别严重 → 🟢正常），自动判断测试质量
- **📈 历史趋势分析**: 自动对比历史数据，显示成功率变化趋势和改进建议
- **⚡ 性能监控**: 响应时间评估，从🚀优秀到🔥很慢的性能分级
- **🔄 数据一致性**: 通知系统与Allure报告成功率完全一致，解决数据不一致问题
- **📱 多渠道支持**: 钉钉、企业微信、邮箱、飞书四大通知平台
- **🛡️ 向后兼容**: 支持原始格式和增强格式无缝切换

## ✨ 核心功能

### 🔥 **智能数据驱动**

- **双数据源**: YAML和Excel两种数据源，满足不同角色需求
- **统一接口**: 提供统一的数据获取API，无需修改测试代码
- **自动转换**: 智能处理数据类型转换和格式标准化
- **模板支持**: 提供标准的Excel测试数据模板和YAML示例
- **数据验证**: 自动验证数据完整性和格式正确性
- **增量更新**: 智能检测数据变化，仅更新修改的测试用例

### 🛠️ **开发效率提升**

- **智能生成**: 根据数据文件自动生成pytest测试代码
- **变化检测**: 智能检测文件变化，避免重复生成
- **代理录制**: 支持mitmproxy代理录制，生成YAML格式测试用例
- **Swagger转换**: 支持swagger接口文档转换为测试用例
- **零代码维护**: 测试人员无需编写代码，只需维护数据文件
- **模块化设计**: 清晰的模块划分，便于维护和扩展

### 📈 **监控与分析**

- **📊 历史趋势分析**: 自动保存测试历史，智能分析成功率变化趋势
- **🚨 智能告警系统**: 5级告警体系，自动判断测试质量并提供改进建议
- **⚡ 性能监控**: 实时统计接口响应时间和成功率，支持性能分级评估
- **📝 多级日志**: 支持DEBUG、INFO、WARNING、ERROR多级日志
- **📱 智能通知**: 支持测试结果的多渠道通知推送，包含趋势分析
- **📋 报告生成**: 自动生成详细的测试报告和统计信息
- **📈 数据一致性**: 确保通知系统与Allure报告数据完全一致
- **🔍 异常追踪**: 详细的错误日志和异常堆栈信息

### ⚡ **性能与扩展**

- **并发执行**: 支持pytest-xdist多进程并发执行
- **缓存机制**: 智能缓存机制，提升测试执行效率
- **环境隔离**: 支持多环境配置和数据隔离
- **插件扩展**: 支持自定义插件和扩展功能
- **Docker支持**: 提供Docker镜像，支持容器化部署
- **CI/CD集成**: 完美支持Jenkins、GitLab CI等CI/CD平台

### 🔒 **安全与稳定性**

- **数据加密**: 支持敏感数据加密存储
- **权限控制**: 不同环境的访问权限控制
- **异常处理**: 完善的异常处理和错误恢复机制
- **健康检查**: 内置健康检查和自诊断功能

## 🚀 快速开始

### 📋 **系统要求**

| 组件     | 版本要求                | 说明              |
|--------|---------------------|-----------------|
| Python | 3.8+                | 推荐使用Python 3.9+ |
| 操作系统   | Windows/Linux/macOS | 跨平台支持           |
| 内存     | 4GB+                | 推荐8GB以上         |
| 磁盘空间   | 2GB+                | 用于依赖和报告存储       |

### 1️⃣ **环境准备**

```bash
# 检查Python版本
python --version  # 确保 >= 3.8

# 克隆项目
git clone https://github.com/your-repo/pytest-auto-api2.git
cd pytest-auto-api2

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 验证安装
python -c "import pytest, allure_pytest; print('✅ 安装成功')"
```

### 2️⃣ **配置项目**

```yaml
# common/config.yaml - 基础配置
project_name: ${PROJECT_NAME:your-project-name}
env: ${TEST_ENV:test}
tester_name: ${TESTER_NAME:txl}

# 数据驱动配置
data_driver_type: ${DATA_DRIVER_TYPE:yaml}  # yaml 或 excel

# 服务地址配置
host: ${HOST:https://api.example.com}
app_host: ${APP_HOST:}

# 通知配置
notification_type: ${NOTIFICATION_TYPE:2}  # 0:不通知 1:钉钉 2:企业微信 3:邮箱 4:飞书
```

### 3️⃣ **创建测试数据**

#### 🔸 **YAML格式** (开发人员推荐)

```yaml
# data/yaml_data/your-project/Login/login.yaml
case_common:
  allureEpic: 接口测试
  allureFeature: 登录模块
  allureStory: 用户登录

login_success:
  url: /api/v1/login
  method: POST
  detail: 正常登录测试
  headers:
    Content-Type: application/json
  data:
    username: test_user
    password: 123456
  assert:
    status_code: 200
    response_data:
      jsonpath: $.code
      type: ==
      value: 0
      message: 登录成功验证失败

login_invalid_password:
  url: /api/v1/login
  method: POST
  detail: 错误密码登录测试
  data:
    username: test_user
    password: wrong_password
  assert:
    status_code: 200
    response_data:
      jsonpath: $.code
      type: ==
      value: 1001
      message: 密码错误验证失败
```

#### 🔸 **Excel格式** (测试人员推荐)

| case_id       | detail | url           | method | headers                             | data                                   | assert                                                                             |
|---------------|--------|---------------|--------|-------------------------------------|----------------------------------------|------------------------------------------------------------------------------------|
| login_success | 正常登录   | /api/v1/login | POST   | {"Content-Type":"application/json"} | {"username":"test","password":"123"}   | {"status_code":200,"response_data":{"jsonpath":"$.code","type":"==","value":0}}    |
| login_fail    | 密码错误   | /api/v1/login | POST   | {"Content-Type":"application/json"} | {"username":"test","password":"wrong"} | {"status_code":200,"response_data":{"jsonpath":"$.code","type":"==","value":1001}} |

### 4️⃣ **运行测试**

#### 🔸 **基础运行**

```bash
# 默认运行（测试环境，YAML数据驱动）
python run.py

# 查看帮助信息
python run.py --help

# 模拟运行（不执行实际测试）
python run.py --dry-run
```

#### 🔸 **多环境运行**

```bash
# 指定环境运行
python run.py --env test      # 测试环境
python run.py --env staging   # 预发环境
python run.py --env prod      # 生产环境

# 指定数据驱动类型
python run.py --data-driver yaml   # YAML数据驱动
python run.py --data-driver excel  # Excel数据驱动

# 组合使用
python run.py --env staging --data-driver excel --notification wechat
```

#### 🔸 **高级运行**

```bash
# 并行执行
python run.py --parallel 4

# 失败重试
python run.py --reruns 2 --reruns-delay 3

# 运行指定模块
python run.py --test-path test_case/Login

# 运行指定标记
python run.py --markers smoke
python run.py --markers "smoke and api"

# 强制重新生成测试用例
python run.py --force-generate

# 生成Excel报告
python run.py --excel-report
```

## 📁 项目结构

```
pytest-auto-api2/                    # 🏠 项目根目录
├── 📂 common/                       # ⚙️ 核心配置模块
│   ├── config.yaml                  # 🔧 主配置文件
│   ├── config_loader.py             # 📥 配置加载器
│   ├── environment_manager.py       # 🌍 环境管理器
│   ├── cli_parser.py               # 💻 命令行解析器
│   └── setting.py                  # 📍 路径设置
├── 📂 config/                       # 🔐 环境配置
│   └── environments/               # 🌐 多环境配置
│       ├── test.env                # 🧪 测试环境
│       ├── staging.env             # 🚀 预发环境
│       └── prod.env                # 🏭 生产环境
├── 📂 data/                         # 📊 测试数据中心
│   ├── yaml_data/                  # 📄 YAML数据驱动
│   │   └── pytest-auto-api2/       # 📁 项目数据
│   │       ├── Login/              # 🔑 登录模块数据
│   │       ├── UserInfo/           # 👤 用户信息数据
│   │       └── Collect/            # ⭐ 收藏模块数据
│   └── excel_data/                 # 📊 Excel数据驱动
│       └── pytest-auto-api2/       # 📁 项目数据
│           ├── Login/              # 🔑 登录模块数据
│           └── ...                 # 📁 其他模块
├── 📂 test_case/                    # 🧪 测试用例代码
│   ├── conftest.py                 # ⚙️ pytest全局配置
│   ├── Login/                      # 🔑 登录模块测试
│   │   └── test_login.py           # 🧪 登录测试用例
│   ├── UserInfo/                   # 👤 用户信息测试
│   │   └── test_get_user_info.py   # 🧪 用户信息测试用例
│   └── Collect/                    # ⭐ 收藏模块测试
│       ├── test_collect_addtool.py # 🧪 添加收藏测试
│       └── ...                     # 🧪 其他测试用例
├── 📂 utils/                        # 🛠️ 核心工具库
│   ├── assertion/                  # ✅ 智能断言引擎
│   │   ├── assert_control.py       # 🎯 断言控制器
│   │   └── assert_type.py          # 📋 断言类型定义
│   ├── logging_tool/               # 📝 日志系统
│   │   ├── log_control.py          # 📊 日志控制器
│   │   └── log_decorator.py        # 🎨 日志装饰器
│   ├── read_files_tools/           # 📖 文件处理工具
│   │   ├── enhanced_case_automatic_control.py  # 🤖 智能用例生成器
│   │   ├── data_driver_control.py  # 🔄 数据驱动控制器
│   │   ├── excel_control.py        # 📊 Excel处理器
│   │   └── yaml_control.py         # 📄 YAML处理器
│   ├── requests_tool/              # 🌐 HTTP请求工具
│   │   ├── request_control.py      # 🎯 请求控制器
│   │   ├── dependent_case.py       # 🔗 依赖用例处理
│   │   └── set_current_request_cache.py  # 💾 请求缓存
│   ├── notify/                     # 📢 智能通知系统
│   │   ├── ding_talk.py           # 📱 钉钉通知
│   │   ├── wechat_send.py         # 💬 企业微信通知
│   │   ├── send_mail.py           # 📧 邮件通知
│   │   ├── lark.py                # 🐦 飞书通知
│   │   ├── enhanced_notification_formatter.py  # 🎨 增强通知格式化器
│   │   ├── alert_level_manager.py  # 🚨 告警级别管理器
│   │   └── history_data_manager.py # 📊 历史数据管理器
│   ├── mysql_tool/                 # 🗄️ 数据库工具
│   ├── cache_process/              # 💾 缓存处理
│   ├── other_tools/                # 🔧 其他工具
│   │   ├── allure_data/           # 📊 Allure数据处理
│   │   ├── models.py              # 📋 数据模型
│   │   └── exceptions.py          # ❌ 异常定义
│   └── times_tool/                 # ⏰ 时间工具
├── 📂 scripts/                      # 🤖 自动化脚本
│   ├── jenkins_runner.py           # 🏗️ Jenkins集成脚本
│   ├── code_quality_checker.py     # 🔍 代码质量检查
│   └── ...                        # 🛠️ 其他脚本
├── 📂 tools/                        # 🔧 项目工具集
│   ├── project_health_checker.py   # 🏥 项目健康检查
│   ├── data_driver_checker.py      # 📊 数据驱动检查
│   ├── report_manager.py           # 📋 报告管理工具
│   └── ...                        # 🛠️ 其他工具
├── 📂 deploy/                       # 🚀 部署配置
│   ├── Dockerfile                  # 🐳 Docker镜像配置
│   └── docker-compose.yml          # 🐳 Docker编排配置
├── 📂 docs/                         # 📚 文档中心
│   ├── MULTI_ENVIRONMENT_GUIDE.md  # 🌍 多环境使用指南
│   └── ...                        # 📖 其他文档
├── 📂 logs/                         # 📝 日志文件
│   ├── info-YYYY-MM-DD.log         # ℹ️ 信息日志
│   ├── error-YYYY-MM-DD.log        # ❌ 错误日志
│   ├── warning-YYYY-MM-DD.log      # ⚠️ 警告日志
│   └── history/                    # 📊 历史数据
│       └── pytest-auto-api2_history.json  # 📈 测试历史记录
├── 📂 report/                       # 📊 测试报告
│   ├── tmp/                        # 🗂️ Allure临时文件
│   ├── html/                       # 🌐 默认HTML报告
│   ├── html_YYYYMMDD_HHMMSS/       # 📅 带时间戳的报告
│   └── archive/                    # 📦 归档报告（可选）
├── 📄 requirements.txt              # 📦 Python依赖列表
├── 📄 pytest.ini                   # ⚙️ pytest配置文件
├── 📄 pyproject.toml               # 🔧 项目配置文件
├── 📄 run.py                       # 🚀 主运行入口
└── 📄 README.md                    # 📖 项目说明文档
```

### 🔍 **核心目录说明**

| 目录           | 功能     | 重要文件                                    |
|--------------|--------|-----------------------------------------|
| `common/`    | 核心配置管理 | `config.yaml`, `environment_manager.py` |
| `data/`      | 测试数据存储 | YAML/Excel数据文件                          |
| `test_case/` | 测试用例代码 | 自动生成的pytest测试文件                         |
| `utils/`     | 核心工具库  | 断言、请求、智能通知等工具                           |
| `scripts/`   | 自动化脚本  | Jenkins集成、代码检查等                         |
| `tools/`     | 项目工具集  | 健康检查、报告管理等                              |
| `logs/`      | 日志和历史  | 运行日志、历史趋势数据                             |
| `report/`    | 测试报告   | Allure报告、时间戳报告                          |
| `deploy/`    | 部署配置   | Docker配置文件                              |
| `docs/`      | 文档中心   | 使用指南和API文档                              |

## 🔧 配置说明

### 🌍 **多环境配置**

框架支持三种环境的独立配置：

#### **环境配置文件**

```bash
# config/environments/test.env - 测试环境
TEST_ENV=test
ENV_NAME=测试环境
TEST_HOST=https://test-api.example.com
NOTIFICATION_TYPE=2
MYSQL_SWITCH=True

# config/environments/staging.env - 预发环境
TEST_ENV=staging
ENV_NAME=预发环境
STAGING_HOST=https://staging-api.example.com
NOTIFICATION_TYPE=1,2
EXCEL_REPORT=True

# config/environments/prod.env - 生产环境
TEST_ENV=prod
ENV_NAME=生产环境
PROD_HOST=https://api.example.com
NOTIFICATION_TYPE=1,2,3
MYSQL_SWITCH=False
```

#### **环境变量优先级**

1. **命令行参数** (最高优先级)
2. **环境变量**
3. **配置文件**
4. **默认值** (最低优先级)

### ⚙️ **核心配置项**

```yaml
# common/config.yaml
# 项目基本信息
project_name: ${PROJECT_NAME:pytest-auto-api2}
env: ${TEST_ENV:test}
tester_name: ${TESTER_NAME:txl}

# 数据驱动配置
data_driver_type: ${DATA_DRIVER_TYPE:yaml}  # yaml | excel
real_time_update_test_cases: ${REAL_TIME_UPDATE:False}

# 多环境服务地址
environments:
  test:
    name: "测试环境"
    host: ${TEST_HOST:https://test-api.example.com}
  staging:
    name: "预发环境"
    host: ${STAGING_HOST:https://staging-api.example.com}
  prod:
    name: "生产环境"
    host: ${PROD_HOST:https://api.example.com}

# 通知配置
notification_type: ${NOTIFICATION_TYPE:2}  # 0:不通知 1:钉钉 2:企业微信 3:邮箱 4:飞书
excel_report: ${EXCEL_REPORT:False}
enhanced_notification: ${ENHANCED_NOTIFICATION:True}  # 增强通知格式
generate_default_report: ${GENERATE_DEFAULT_REPORT:True}  # 生成默认报告

# 钉钉通知配置
ding_talk:
  webhook: ${DING_TALK_WEBHOOK:}
  secret: ${DING_TALK_SECRET:}

# 企业微信通知配置
wechat:
  webhook: ${WECHAT_WEBHOOK:}

# 邮箱通知配置
email:
  send_user: ${EMAIL_SEND_USER:}
  email_host: ${EMAIL_HOST:smtp.qq.com}
  stamp_key: ${EMAIL_STAMP_KEY:}
  send_list: ${EMAIL_SEND_LIST:}

# 飞书通知配置
lark:
  webhook: ${LARK_WEBHOOK:}

# 数据库配置
mysql_db:
  switch: ${MYSQL_SWITCH:False}
  host: ${MYSQL_HOST:localhost}
  user: ${MYSQL_USER:root}
  password: ${MYSQL_PASSWORD:123456}
  port: ${MYSQL_PORT:3306}
  database: ${MYSQL_DATABASE:test}
```

### 🔄 **数据驱动切换**

#### **命令行切换**

```bash
# 切换到YAML数据驱动
python run.py --data-driver yaml

# 切换到Excel数据驱动
python run.py --data-driver excel

# 环境变量切换
export DATA_DRIVER_TYPE=excel
python run.py
```

#### **代码中切换**

```python
from utils.read_files_tools.data_driver_control import DataDriverManager

# 获取数据驱动管理器
driver_manager = DataDriverManager()

# 切换到YAML数据驱动
driver_manager.switch_driver('yaml')

# 切换到Excel数据驱动
driver_manager.switch_driver('excel')

# 获取当前数据驱动类型
current_driver = driver_manager.get_current_driver()
print(f"当前数据驱动: {current_driver}")
```

### 📊 **通知配置详解**

| 通知类型 | 配置项                                                     | 说明                |
|------|---------------------------------------------------------|-------------------|
| 钉钉   | `DING_TALK_WEBHOOK`, `DING_TALK_SECRET`                 | 钉钉机器人webhook和加签密钥 |
| 企业微信 | `WECHAT_WEBHOOK`                                        | 企业微信机器人webhook    |
| 邮箱   | `EMAIL_SEND_USER`, `EMAIL_STAMP_KEY`, `EMAIL_SEND_LIST` | SMTP邮箱配置          |
| 飞书   | `LARK_WEBHOOK`                                          | 飞书机器人webhook      |

#### **多通知配置**

```bash
# 同时发送钉钉和企业微信通知
NOTIFICATION_TYPE=1,2

# 发送所有类型通知
NOTIFICATION_TYPE=1,2,3,4

# 命令行指定
python run.py --notification all
```

## 📖 使用指南

### 🎯 **数据驱动详细使用**

#### 🔸 **YAML数据格式详解**

```yaml
# data/yaml_data/pytest-auto-api2/Login/login.yaml

# 公共配置 - 所有用例共享
case_common:
  allureEpic: 接口自动化测试        # Allure Epic标签
  allureFeature: 用户登录模块       # Allure Feature标签
  allureStory: 登录功能测试         # Allure Story标签
  headers: # 公共请求头
    Content-Type: application/json
    User-Agent: pytest-auto-api2

# 成功登录用例
login_success:
  url: /api/v1/auth/login          # 接口路径（会自动拼接host）
  method: POST                     # 请求方法
  detail: 用户正常登录测试           # 用例描述
  headers: # 请求头（会与公共头合并）
    X-Request-ID: login-001
  data: # 请求体数据
    username: test_user
    password: "123456"
    remember_me: true
  assert: # 断言配置
    status_code: 200              # HTTP状态码断言
    response_time: 3000           # 响应时间断言（毫秒）
    response_data: # 响应数据断言
      - jsonpath: $.code          # JSONPath表达式
        type: ==                  # 断言类型
        value: 0                  # 期望值
        message: 登录成功码验证失败  # 失败消息
      - jsonpath: $.data.token    # 验证token存在
        type: not_null
        message: 登录token不能为空
  extract: # 数据提取（用于接口依赖）
    login_token: # 提取变量名
      jsonpath: $.data.token      # 提取路径
    user_id:
      jsonpath: $.data.user_id
```

#### 🔸 **Excel数据格式详解**

| 列名      | 说明          | 示例                                    | 必填 |
|---------|-------------|---------------------------------------|----|
| case_id | 用例唯一标识      | login_success                         | ✅  |
| detail  | 用例描述        | 用户正常登录测试                              | ✅  |
| url     | 接口路径        | /api/v1/auth/login                    | ✅  |
| method  | HTTP方法      | POST                                  | ✅  |
| headers | 请求头(JSON)   | {"Content-Type":"application/json"}   | ❌  |
| data    | 请求体(JSON)   | {"username":"test","password":"123"}  | ❌  |
| params  | URL参数(JSON) | {"page":1,"size":10}                  | ❌  |
| assert  | 断言配置(JSON)  | {"status_code":200}                   | ✅  |
| extract | 数据提取(JSON)  | {"token":{"jsonpath":"$.data.token"}} | ❌  |

### 🔗 **接口依赖处理**

#### **数据提取和引用**

```yaml
# 第一个接口：登录并提取token
login:
  url: /api/v1/auth/login
  method: POST
  data:
    username: test_user
    password: "123456"
  extract:
    login_token:
      jsonpath: $.data.token
    user_id:
      jsonpath: $.data.user_id

# 第二个接口：使用提取的token
get_user_profile:
  url: /api/v1/user/profile
  method: GET
  headers:
    Authorization: Bearer $cache{login_token}  # 引用提取的token
  params:
    user_id: $cache{user_id}                  # 引用提取的user_id
  assert:
    status_code: 200
```

#### **依赖用例配置**

```yaml
# 复杂依赖场景
dependence_case: true
dependence_case_data:
  - case_id: login_case
    dependent_data:
      - dependent_type: response
        jsonpath: $.data.token
        set_cache: auth_token
      - dependent_type: response
        jsonpath: $.data.user_id
        set_cache: current_user_id

# 在当前用例中使用缓存数据
headers:
  Authorization: Bearer $cache{auth_token}
params:
  user_id: $cache{current_user_id}
```

### ✅ **断言配置详解**

#### **支持的断言类型**

| 断言类型           | 说明    | 示例                                           |
|----------------|-------|----------------------------------------------|
| `==`           | 等于    | `{"type": "==", "value": 0}`                 |
| `!=`           | 不等于   | `{"type": "!=", "value": -1}`                |
| `>`            | 大于    | `{"type": ">", "value": 0}`                  |
| `>=`           | 大于等于  | `{"type": ">=", "value": 1}`                 |
| `<`            | 小于    | `{"type": "<", "value": 100}`                |
| `<=`           | 小于等于  | `{"type": "<=", "value": 99}`                |
| `contains`     | 包含    | `{"type": "contains", "value": "success"}`   |
| `not_contains` | 不包含   | `{"type": "not_contains", "value": "error"}` |
| `in`           | 在列表中  | `{"type": "in", "value": [0, 1, 2]}`         |
| `not_in`       | 不在列表中 | `{"type": "not_in", "value": [-1, -2]}`      |
| `is_null`      | 为空    | `{"type": "is_null"}`                        |
| `not_null`     | 不为空   | `{"type": "not_null"}`                       |
| `regex`        | 正则匹配  | `{"type": "regex", "value": "^\\d+$"}`       |

#### **复合断言配置**

```yaml
assert:
  # HTTP状态码断言
  status_code: 200

  # 响应时间断言（毫秒）
  response_time: 3000

  # 多个响应数据断言
  response_data:
    - jsonpath: $.code
      type: ==
      value: 0
      message: 返回码验证失败
    - jsonpath: $.data.list
      type: not_null
      message: 数据列表不能为空
    - jsonpath: $.data.total
      type: ">="
      value: 0
      message: 总数必须大于等于0

  # 数据库断言
  sql_data:
    - sql: "SELECT count(*) as count FROM users WHERE status=1"
      jsonpath: $.count
      type: ">"
      value: 0
      message: 活跃用户数量验证失败

  # 响应头断言
  response_headers:
    - header: Content-Type
      type: contains
      value: application/json
      message: 响应类型验证失败
```

## 🧪 测试示例

### 🔸 **自动生成的测试代码**

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
登录模块测试用例
此文件由 pytest-auto-api2 框架自动生成，请勿手动修改
"""

import allure
import pytest
from utils.assertion.assert_control import Assert
from utils.requests_tool.request_control import RequestControl
from utils.read_files_tools.data_driver_control import DataDriverManager

# 获取测试数据
data_driver = DataDriverManager()
test_data = data_driver.get_test_data("Login", "login")


@allure.epic("接口自动化测试")
@allure.feature("用户登录模块")
class TestLogin:
    """登录功能测试类"""

    @allure.story("登录功能测试")
    @pytest.mark.parametrize('case_data', test_data, ids=[case['detail'] for case in test_data])
    def test_login(self, case_data, case_skip):
        """
        登录接口测试

        Args:
            case_data: 测试用例数据
            case_skip: 用例跳过控制器
        """
        # 发送HTTP请求
        response = RequestControl(case_data).http_request()

        # 执行断言
        Assert(
            assert_data=case_data.get('assert', {}),
            sql_data=response.sql_data,
            request_data=response.request_data,
            response_data=response.response_data,
            status_code=response.status_code,
            response_time=response.response_time
        ).assert_type_handle()

        # 数据提取和缓存
        if 'extract' in case_data:
            response.extract_data(case_data['extract'])
```

### 🔸 **手动编写测试用例**

```python
import pytest
import allure
from utils.requests_tool.request_control import RequestControl
from utils.assertion.assert_control import Assert


class TestCustomAPI:
    """自定义API测试"""

    @allure.story("自定义登录测试")
    def test_custom_login(self):
        """手动编写的登录测试"""

        # 构造测试数据
        test_data = {
            "url": "/api/v1/auth/login",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json"
            },
            "data": {
                "username": "admin",
                "password": "123456"
            }
        }

        # 发送请求
        response = RequestControl(test_data).http_request()

        # 自定义断言
        assert response.status_code == 200
        assert response.response_data['code'] == 0
        assert 'token' in response.response_data['data']

        # 提取token用于后续测试
        token = response.response_data['data']['token']

        # 使用token进行后续请求
        profile_data = {
            "url": "/api/v1/user/profile",
            "method": "GET",
            "headers": {
                "Authorization": f"Bearer {token}"
            }
        }

        profile_response = RequestControl(profile_data).http_request()
        assert profile_response.status_code == 200
```

### 🔸 **并发测试**

```bash
# 使用pytest-xdist进行并发测试
python run.py --parallel auto    # 自动检测CPU核心数
python run.py --parallel 4       # 指定4个进程
python run.py --parallel 8       # 指定8个进程

# 传统pytest命令
pytest -n auto                   # 自动检测
pytest -n 4                      # 指定进程数
```

### 🔸 **性能测试**

```bash
# 压力测试
python run.py --parallel 10 --reruns 3

# 长时间稳定性测试
python run.py --count 100 --parallel 4
```

## 📊 报告与通知

### 🔸 **智能测试报告系统**

框架提供企业级的智能测试报告系统，包含带时间戳的历史报告和实时趋势分析。

#### **📅 带时间戳报告**

```bash
# 自动生成带时间戳报告（推荐）
python run.py                           # 自动生成双报告

# 报告位置：
# ./report/html/index.html              # 默认报告（向后兼容）
# ./report/html_20250530_185246/index.html  # 带时间戳报告

# 管理历史报告
python tools/report_manager.py          # 启动报告管理工具
```

#### **🎨 增强通知格式**

```bash
# 启用增强通知格式（默认开启）
enhanced_notification: True

# 通知内容包含：
# - 🚨 智能告警级别（5级告警体系）
# - 📈 历史趋势分析（对比上次结果）
# - ⚡ 性能指标评估
# - 📅 带时间戳报告链接
```

#### **📊 报告功能特色**

- **📅 历史追溯**: 每次执行生成独立的时间戳报告
- **📈 趋势分析**: 智能对比历史数据，显示成功率变化趋势
- **🚨 智能告警**: 5级告警体系，自动判断测试质量
- **📊 统计信息**: 用例成功率、执行时长、性能指标统计
- **🔍 详细日志**: 每个用例的详细执行日志
- **📱 响应式设计**: 支持移动端查看
- **🔗 接口详情**: 请求/响应数据完整展示
- **⚡ 性能分析**: 接口响应时间分析和分级评估
- **🛠️ 报告管理**: 专业的报告清理、归档、统计工具

### 🔸 **多渠道通知系统**

框架支持多种通知方式，可以同时配置多个通知渠道，确保测试结果及时传达给相关人员。

#### **钉钉通知**

```bash
# 环境变量配置
export DING_TALK_WEBHOOK="https://oapi.dingtalk.com/robot/send?access_token=your_token"
export DING_TALK_SECRET="your_secret"

# 命令行使用
python run.py --notification dingtalk
```

**增强通知内容包含：**

- 🚨 **智能告警级别**: 5级告警体系（🔴特别严重 → 🟢正常）
- 📈 **历史趋势分析**: 对比上次结果，显示成功率变化趋势
- ⚡ **性能指标评估**: 响应时间分级（🚀优秀 → 🔥很慢）
- 📊 **详细统计信息**: 成功/失败/跳过用例数，数据一致性保证
- 🔗 **多种报告链接**: 默认报告 + 带时间戳报告
- 💡 **智能建议**: 基于测试结果的改进建议
- 👤 **执行信息**: 执行人员、环境、时间等

#### **企业微信通知**

```bash
# 环境变量配置
export WECHAT_WEBHOOK="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_key"

# 命令行使用
python run.py --notification wechat
```

#### **邮箱通知**

```bash
# 环境变量配置
export EMAIL_SEND_USER="your_email@example.com"
export EMAIL_STAMP_KEY="your_password"
export EMAIL_HOST="smtp.example.com"
export EMAIL_SEND_LIST="team@example.com,manager@example.com"

# 命令行使用
python run.py --notification email
```

#### **飞书通知**

```bash
# 环境变量配置
export LARK_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/your_hook"

# 命令行使用
python run.py --notification lark
```

#### **多通知配置**

```bash
# 同时发送多种通知
python run.py --notification all                    # 发送所有配置的通知
export NOTIFICATION_TYPE="1,2,3"                   # 钉钉+企业微信+邮箱
python run.py

# Jenkins中的配置
python run.py --env ${ENV} --notification ${NOTIFICATION_TYPE}
```

### 🔸 **Excel错误报告**

当测试用例失败时，框架可以生成详细的Excel错误报告，便于问题分析和追踪。

```bash
# 生成Excel报告
python run.py --excel-report

# 环境变量配置
export EXCEL_REPORT=True
python run.py
```

**Excel报告包含：**

- 📋 失败用例详细信息
- 🔍 错误原因分析
- 📊 请求/响应数据对比
- 📈 失败趋势统计

## 🏗️ CI/CD集成

### 🔸 **Jenkins集成**

框架提供完整的Jenkins集成支持，包括参数化构建和Pipeline脚本。

#### **参数化构建配置**

在Jenkins中配置以下构建参数：

| 参数名            | 类型      | 默认值    | 描述                                    |
|----------------|---------|--------|---------------------------------------|
| ENV            | Choice  | test   | 运行环境 (test/staging/prod)              |
| DATA_DRIVER    | Choice  | yaml   | 数据驱动类型 (yaml/excel)                   |
| NOTIFICATION   | Choice  | wechat | 通知方式 (dingtalk/wechat/email/lark/all) |
| TEST_PATH      | String  |        | 测试路径（可选）                              |
| PARALLEL       | String  | 1      | 并行进程数                                 |
| FORCE_GENERATE | Boolean | false  | 强制重新生成测试用例                            |

#### **Jenkins Pipeline示例**

```groovy
pipeline {
    agent any

    parameters {
        choice(name: 'ENV', choices: ['test', 'staging', 'prod'], description: '选择运行环境')
        choice(name: 'DATA_DRIVER', choices: ['yaml', 'excel'], description: '选择数据驱动类型')
        choice(name: 'NOTIFICATION', choices: ['dingtalk', 'wechat', 'email', 'all'], description: '选择通知方式')
        string(name: 'TEST_PATH', defaultValue: '', description: '测试路径（可选）')
        string(name: 'PARALLEL', defaultValue: '2', description: '并行进程数')
        booleanParam(name: 'FORCE_GENERATE', defaultValue: false, description: '强制重新生成测试用例')
    }

    environment {
        ENV = "${params.ENV}"
        DATA_DRIVER = "${params.DATA_DRIVER}"
        NOTIFICATION = "${params.NOTIFICATION}"
        TEST_PATH = "${params.TEST_PATH}"
        PARALLEL = "${params.PARALLEL}"
        FORCE_GENERATE = "${params.FORCE_GENERATE}"
    }

    stages {
        stage('环境准备') {
            steps {
                echo "准备${params.ENV}环境..."
                sh 'python --version'
                sh 'pip install -r requirements.txt'
            }
        }

        stage('执行测试') {
            steps {
                script {
                    sh 'python scripts/jenkins_runner.py'
                }
            }
        }

        stage('发布报告') {
            steps {
                allure([
                    includeProperties: false,
                    jdk: '',
                    properties: [],
                    reportBuildPolicy: 'ALWAYS',
                    results: [[path: 'report/tmp']]
                ])
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'logs/*.log', allowEmptyArchive: true
            cleanWs()
        }
        failure {
            echo '测试执行失败'
        }
        success {
            echo '测试执行成功'
        }
    }
}
```

#### **简化构建脚本**

```bash
#!/bin/bash
# Jenkins构建脚本

# 设置环境变量
export ENV=${ENV:-test}
export DATA_DRIVER=${DATA_DRIVER:-yaml}
export NOTIFICATION=${NOTIFICATION:-wechat}

# 执行测试
python scripts/jenkins_runner.py

# 检查结果
if [ $? -eq 0 ]; then
    echo "✅ 测试执行成功"
else
    echo "❌ 测试执行失败"
    exit 1
fi
```

### 🔸 **GitLab CI集成**

```yaml
# .gitlab-ci.yml
stages:
  - test
  - report

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip/
    - venv/

before_script:
  - python -m venv venv
  - source venv/bin/activate
  - pip install -r requirements.txt

test:
  stage: test
  script:
    - python run.py --env test --data-driver yaml --notification email --no-allure-serve
  artifacts:
    when: always
    paths:
      - report/
      - logs/
    expire_in: 1 week
  only:
    - main
    - develop

test_staging:
  stage: test
  script:
    - python run.py --env staging --data-driver excel --notification wechat --no-allure-serve
  artifacts:
    when: always
    paths:
      - report/
      - logs/
    expire_in: 1 week
  only:
    - staging

report:
  stage: report
  script:
    - echo "生成测试报告"
  artifacts:
    reports:
      junit: report/junit.xml
  only:
    - main
```

### 🔸 **GitHub Actions集成**

```yaml
# .github/workflows/api-test.yml
name: API自动化测试

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # 每天凌晨2点执行

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [ 3.8, 3.9, '3.10' ]
        env: [ test, staging ]
        data-driver: [ yaml, excel ]

    steps:
      - uses: actions/checkout@v3

      - name: 设置Python环境
        uses: actions/setup-python@v3
        with:
          python-version: ${{ matrix.python-version }}

      - name: 安装依赖
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: 执行测试
        run: |
          python run.py --env ${{ matrix.env }} --data-driver ${{ matrix.data-driver }} --notification email --no-allure-serve
        env:
          EMAIL_SEND_USER: ${{ secrets.EMAIL_SEND_USER }}
          EMAIL_STAMP_KEY: ${{ secrets.EMAIL_STAMP_KEY }}
          EMAIL_SEND_LIST: ${{ secrets.EMAIL_SEND_LIST }}

      - name: 上传测试报告
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-report-${{ matrix.env }}-${{ matrix.data-driver }}
          path: |
            report/
            logs/

      - name: 发布Allure报告
        uses: simple-elf/allure-report-action@master
        if: always()
        with:
          allure_results: report/tmp
          allure_history: allure-history
```

### 🔸 **Docker集成**

```bash
# 使用Docker运行测试
docker build -t pytest-auto-api2 .
docker run -e ENV=test -e DATA_DRIVER=yaml pytest-auto-api2

# 使用docker-compose
docker-compose up --build
```

## 🔧 项目工具

框架提供了丰富的项目管理和维护工具：

### 🔸 **报告管理工具**

```bash
# 启动报告管理工具
python tools/report_manager.py

# 功能菜单：
# 1. 📋 查看报告列表
# 2. 🧹 清理旧报告
# 3. 📦 归档旧报告
# 4. 📈 获取最新报告
# 5. 📊 报告统计
```

### 🔸 **功能测试工具**

```bash
# 历史趋势分析测试
python test_history_trend.py           # 测试历史趋势分析功能

# 功能演示
python demo_trend_analysis.py          # 演示趋势分析功能

# 带时间戳报告测试
python test_timestamped_reports.py     # 测试带时间戳报告功能

# 成功率修复验证
python verify_success_rate_fix.py      # 验证成功率计算修复
```

### 🔸 **项目检查工具**

```bash
# 项目健康检查
python tools/project_health_checker.py

# 数据驱动一致性检查
python tools/data_driver_checker.py

# 智能用例生成
python tools/case_generator.py
```

## 🤝 贡献指南

我们欢迎并感谢任何形式的贡献！无论是报告bug、提出新功能建议，还是提交代码改进。

### 🔸 **如何贡献**

1. **Fork项目** 到您的GitHub账户
2. **创建功能分支** (`git checkout -b feature/AmazingFeature`)
3. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
4. **推送到分支** (`git push origin feature/AmazingFeature`)
5. **创建Pull Request**

### 🔸 **开发环境搭建**

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/pytest-auto-api2.git
cd pytest-auto-api2

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 3. 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖（如果有）

# 4. 安装pre-commit钩子
pre-commit install

# 5. 运行测试验证环境
python run.py --dry-run
```

### 🔸 **代码规范**

- **Python代码**: 遵循PEP 8规范
- **注释**: 使用中文注释，保持代码可读性
- **文档**: 更新相关文档和README
- **测试**: 为新功能添加相应的测试用例

### 🔸 **提交规范**

使用语义化提交信息：

```
feat: 添加新功能
fix: 修复bug
docs: 更新文档
style: 代码格式调整
refactor: 代码重构
test: 添加测试
chore: 构建过程或辅助工具的变动
```

### 🔸 **问题反馈**

如果您遇到问题或有建议，请：

1. 查看[已有Issues](https://github.com/your-repo/pytest-auto-api2/issues)
2. 创建新的Issue，详细描述问题
3. 提供复现步骤和环境信息

## 📄 许可证

本项目采用 **MIT 许可证** - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！

### 🌟 **核心贡献者**

- [@your-name](https://github.com/your-name) - 项目创建者和维护者
- [@contributor1](https://github.com/contributor1) - 核心功能开发
- [@contributor2](https://github.com/contributor2) - 文档和测试

### 🛠️ **技术栈致谢**

- [pytest](https://pytest.org/) - 强大的Python测试框架
- [allure](https://docs.qameta.io/allure/) - 美观的测试报告工具
- [requests](https://requests.readthedocs.io/) - 优雅的HTTP库
- [pydantic](https://pydantic-docs.helpmanual.io/) - 数据验证库
- [click](https://click.palletsprojects.com/) - 命令行工具库

---

<div align="center">

**如果这个项目对您有帮助，请给我们一个 ⭐ Star！**

[![Star History Chart](https://api.star-history.com/svg?repos=your-repo/pytest-auto-api2&type=Date)](https://star-history.com/#your-repo/pytest-auto-api2&Date)

[🏠 首页](https://github.com/your-repo/pytest-auto-api2) • [📖 文档](https://your-repo.github.io/pytest-auto-api2) • [🐛 报告问题](https://github.com/your-repo/pytest-auto-api2/issues) • [💬 讨论](https://github.com/your-repo/pytest-auto-api2/discussions)

</div>
