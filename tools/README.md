# 项目检查工具集

这是一套完整的项目检查工具，用于全面评估pytest-auto-api2项目的健康状况。

## 🛠️ 工具列表

### 1. 项目健康检查器 (`project_health_checker.py`)

**功能**: 全面检查项目的整体健康状况

- ✅ 项目结构检查
- ✅ 核心模块检查
- ✅ 数据驱动功能检查
- ✅ 配置文件检查
- ✅ 依赖管理检查
- ✅ 测试执行检查

**使用方法**:

```bash
# 完整检查
python tools/project_health_checker.py

# 指定项目路径
python tools/project_health_checker.py --project-root /path/to/project
```

### 2. 数据驱动检查器 (`data_driver_checker.py`)

**功能**: 专门检查YAML和Excel数据驱动功能

- ✅ YAML数据驱动检查
- ✅ Excel数据驱动检查
- ✅ 数据驱动切换功能检查
- ✅ 用例数量对比分析

**使用方法**:

```bash
# 数据驱动检查
python tools/data_driver_checker.py

# 指定项目路径
python tools/data_driver_checker.py --project-root /path/to/project
```

### 3. 测试执行检查器 (`test_execution_checker.py`)

**功能**: 检查测试用例的执行状态和结果

- ✅ 测试发现检查
- ✅ 测试收集检查
- ✅ 示例执行检查
- ✅ YAML/Excel测试检查

**使用方法**:

```bash
# 测试执行检查
python tools/test_execution_checker.py

# 指定模块检查
python tools/test_execution_checker.py --module Login
```

### 4. 项目检查管理器 (`project_checker_manager.py`)

**功能**: 统一管理所有检查工具，提供一键检查

- ✅ 全面检查（所有工具）
- ✅ 快速检查（核心功能）
- ✅ 单独检查（指定工具）
- ✅ 综合报告生成

**使用方法**:

```bash
# 交互式菜单
python tools/run_checks.py

# 全面检查（推荐）
python tools/project_checker_manager.py --check-type all

# 快速检查
python tools/project_checker_manager.py --check-type quick

# 仅健康检查
python tools/project_checker_manager.py --check-type health

# 仅数据驱动检查
python tools/project_checker_manager.py --check-type data

# 仅测试执行检查
python tools/project_checker_manager.py --check-type test
```

## 📊 报告文件

每个工具都会生成对应的JSON报告文件：

| 工具      | 报告文件                         | 说明       |
|---------|------------------------------|----------|
| 项目健康检查器 | `project_health_report.json` | 项目整体健康状况 |
| 数据驱动检查器 | `data_driver_report.json`    | 数据驱动功能状态 |
| 测试执行检查器 | `test_execution_report.json` | 测试执行结果   |
| 项目检查管理器 | `comprehensive_report.json`  | 综合检查报告   |

## 🎯 使用建议

### 🚀 快速启动（推荐）
```bash
# 交互式菜单
python tools/run_checks.py
```

### 日常使用
```bash
# 项目结构
python tools/project_structure_analyzer.py

# 每日快速检查
python tools/project_checker_manager.py --check-type quick

# 每周全面检查
python tools/project_checker_manager.py --check-type all
```

### 开发调试

```bash
# 检查数据驱动功能
python tools/data_driver_checker.py

# 检查测试执行
python tools/test_execution_checker.py
```

### CI/CD集成

```bash
# 在CI/CD流水线中使用
python tools/project_checker_manager.py --check-type health
```

## 📈 评分标准

### 总体评分

- **90-100分**: A+ (优秀) 🏆
- **80-89分**: A (良好) 🥇
- **70-79分**: B (一般) 🥈
- **60-69分**: C (及格) 🥉
- **0-59分**: D (需改进) ⚠️

### 分类评分

- **项目结构**: 目录和文件完整性
- **核心模块**: 模块导入和功能正常性
- **数据驱动**: YAML和Excel数据源功能
- **配置文件**: 配置文件完整性和可读性
- **依赖管理**: 依赖安装和兼容性
- **测试执行**: 测试发现、收集和执行

## 🔧 自定义扩展

### 添加新的检查项

1. 在对应的检查器类中添加新方法
2. 在`check_all()`方法中调用新检查
3. 更新报告生成逻辑

### 修改评分标准

1. 修改各检查器中的`score`计算逻辑
2. 更新`generate_*_report()`方法中的评分显示

## 🐛 故障排除

### 常见问题

**1. 模块导入失败**

```
❌ 请求控制模块: No module named 'utils.requests_tool.request_control'
```

**解决**: 确保在项目根目录运行工具

**2. 数据驱动切换失败**

```
❌ YAML → Excel: 切换失败
```

**解决**: 检查配置文件和数据文件是否存在

**3. 测试收集超时**

```
❌ 测试收集超时
```

**解决**: 检查测试文件语法和依赖

### 调试模式

在工具中添加调试输出：

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

## 📝 更新日志

### v1.0.0 (2025-05-28)

- ✅ 初始版本发布
- ✅ 项目健康检查器
- ✅ 数据驱动检查器
- ✅ 测试执行检查器
- ✅ 项目检查管理器
- ✅ 综合报告生成

## 🤝 贡献指南

欢迎提交改进建议和新功能！

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 发起Pull Request

---

**如果这些工具对您有帮助，请给项目一个 ⭐ Star！**
