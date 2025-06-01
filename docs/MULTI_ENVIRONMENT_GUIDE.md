# 多环境和命令行使用指南

## 🌍 **多环境支持**

框架现在支持三种环境的无缝切换：

- **test**: 测试环境
- **staging**: 预发环境
- **prod**: 生产环境

## 🚀 **快速开始**

### **1. 本地运行**

```bash
# 默认运行（测试环境，YAML数据驱动）
python run.py

# 指定环境运行
python run.py --env test
python run.py --env staging
python run.py --env prod

# 指定数据驱动类型
python run.py --data-driver yaml
python run.py --data-driver excel

# 指定通知方式
python run.py --notification dingtalk
python run.py --notification wechat
python run.py --notification email
python run.py --notification all
```

### **2. 组合使用**

```bash
# 在预发环境使用Excel数据驱动，发送企业微信通知
python run.py --env staging --data-driver excel --notification wechat

# 强制重新生成测试用例，运行指定模块
python run.py --force-generate --test-path test_case/Login

# 并行执行，失败重试
python run.py --parallel 4 --reruns 2 --reruns-delay 3

# 运行指定标记的用例
python run.py --markers smoke
python run.py --markers "smoke and login"
```

## 🏗️ **Jenkins集成**

### **1. Jenkins参数化构建**

在Jenkins中配置以下参数：

| 参数名            | 类型      | 默认值    | 描述                                    |
|----------------|---------|--------|---------------------------------------|
| ENV            | Choice  | test   | 运行环境 (test/staging/prod)              |
| DATA_DRIVER    | Choice  | yaml   | 数据驱动类型 (yaml/excel)                   |
| NOTIFICATION   | Choice  | wechat | 通知方式 (dingtalk/wechat/email/lark/all) |
| TEST_PATH      | String  |        | 测试路径（可选）                              |
| MARKERS        | String  |        | 测试标记（可选）                              |
| PARALLEL       | String  | 1      | 并行进程数                                 |
| RERUNS         | String  | 0      | 失败重试次数                                |
| FORCE_GENERATE | Boolean | false  | 强制重新生成测试用例                            |
| EXCEL_REPORT   | Boolean | false  | 生成Excel报告                             |

### **2. Jenkins Pipeline脚本**

```groovy
pipeline {
    agent any
    
    parameters {
        choice(
            name: 'ENV',
            choices: ['test', 'staging', 'prod'],
            description: '选择运行环境'
        )
        choice(
            name: 'DATA_DRIVER', 
            choices: ['yaml', 'excel'],
            description: '选择数据驱动类型'
        )
        choice(
            name: 'NOTIFICATION',
            choices: ['dingtalk', 'wechat', 'email', 'lark', 'all'],
            description: '选择通知方式'
        )
        string(
            name: 'TEST_PATH',
            defaultValue: '',
            description: '测试路径（可选）'
        )
        string(
            name: 'MARKERS',
            defaultValue: '',
            description: '测试标记（可选）'
        )
        string(
            name: 'PARALLEL',
            defaultValue: '1',
            description: '并行进程数'
        )
        booleanParam(
            name: 'FORCE_GENERATE',
            defaultValue: false,
            description: '强制重新生成测试用例'
        )
        booleanParam(
            name: 'EXCEL_REPORT',
            defaultValue: false,
            description: '生成Excel报告'
        )
    }
    
    stages {
        stage('环境准备') {
            steps {
                echo "准备${params.ENV}环境..."
                // 设置环境变量
                script {
                    env.ENV = params.ENV
                    env.DATA_DRIVER = params.DATA_DRIVER
                    env.NOTIFICATION = params.NOTIFICATION
                    env.TEST_PATH = params.TEST_PATH
                    env.MARKERS = params.MARKERS
                    env.PARALLEL = params.PARALLEL
                    env.FORCE_GENERATE = params.FORCE_GENERATE
                    env.EXCEL_REPORT = params.EXCEL_REPORT
                }
            }
        }
        
        stage('安装依赖') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        
        stage('执行测试') {
            steps {
                script {
                    // 使用Jenkins专用运行脚本
                    sh 'python scripts/jenkins_runner.py'
                }
            }
        }
        
        stage('发布报告') {
            steps {
                // 发布Allure报告
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
            // 清理工作空间
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

### **3. 简化的Jenkins构建脚本**

```bash
#!/bin/bash
# Jenkins构建脚本

# 设置环境变量
export ENV=${ENV:-test}
export DATA_DRIVER=${DATA_DRIVER:-yaml}
export NOTIFICATION=${NOTIFICATION:-wechat}

# 执行测试
python scripts/jenkins_runner.py
```

## ⚙️ **环境配置**

### **1. 环境配置文件**

每个环境都有独立的配置文件：

```
config/environments/
├── test.env      # 测试环境配置
├── staging.env   # 预发环境配置
└── prod.env      # 生产环境配置
```

### **2. 使用环境配置文件**

```bash
# 加载测试环境配置
source config/environments/test.env
python run.py

# 加载预发环境配置
source config/environments/staging.env
python run.py

# 加载生产环境配置
source config/environments/prod.env
python run.py
```

### **3. 环境变量优先级**

1. **命令行参数** (最高优先级)
2. **环境变量**
3. **配置文件**
4. **默认值** (最低优先级)

## 📝 **命令行参数完整列表**

### **环境配置**

- `--env {test,staging,prod}`: 指定运行环境
- `--host HOST`: 指定主机地址
- `--app-host APP_HOST`: 指定应用主机地址

### **数据驱动配置**

- `--data-driver {yaml,excel}`: 指定数据驱动类型
- `--yaml-path PATH`: 指定YAML数据文件路径
- `--excel-path PATH`: 指定Excel数据文件路径

### **测试执行配置**

- `--test-path PATH`: 指定测试用例路径
- `--markers MARKERS`: 指定pytest标记
- `--parallel N`: 并行执行的进程数
- `--reruns N`: 失败用例重试次数
- `--reruns-delay N`: 重试间隔时间(秒)

### **报告和通知配置**

- `--notification {dingtalk,wechat,email,lark,all}`: 指定通知方式
- `--excel-report`: 生成Excel错误报告
- `--no-allure-serve`: 不启动Allure报告服务
- `--allure-port PORT`: Allure报告服务端口

### **测试用例生成配置**

- `--force-generate`: 强制重新生成所有测试用例
- `--no-generate`: 跳过测试用例生成
- `--clean-obsolete`: 清理过时的测试文件

### **其他配置**

- `--config CONFIG`: 指定配置文件路径
- `--verbose, -v`: 详细输出模式
- `--quiet, -q`: 静默模式
- `--dry-run`: 模拟运行，不执行实际测试
- `--version`: 显示版本信息

## 🔧 **高级用法**

### **1. 环境管理器**

```python
from common.environment_manager import get_environment_manager

# 获取环境管理器
env_manager = get_environment_manager()

# 切换环境
env_manager.set_environment('staging')

# 获取当前环境配置
config = env_manager.get_environment_config()
host = env_manager.get_host()

# 验证环境配置
validation = env_manager.validate_environment_config()
```

### **2. 程序化调用**

```python
from run import run

# 程序化调用，传递参数
args = ['--env', 'test', '--data-driver', 'excel', '--notification', 'dingtalk']
run(args)
```

## 🚨 **注意事项**

1. **生产环境**: 生产环境配置请谨慎修改，建议使用只读数据库权限
2. **敏感信息**: 不要在配置文件中硬编码敏感信息，使用环境变量
3. **权限控制**: 不同环境应该有不同的访问权限和通知配置
4. **备份策略**: 重要环境的配置文件应该有备份和版本控制

## 🆘 **故障排除**

### **常见问题**

1. **环境切换失败**
   ```bash
   # 检查环境配置
   python -c "from common.environment_manager import get_environment_manager; get_environment_manager().print_current_environment_info()"
   ```

2. **配置文件不生效**
   ```bash
   # 检查环境变量
   python -c "import os; print({k:v for k,v in os.environ.items() if 'TEST' in k})"
   ```

3. **命令行参数不识别**
   ```bash
   # 查看帮助信息
   python run.py --help
   ```
