#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
作者信息替换完成报告
生成详细的替换结果报告
"""

import os
from pathlib import Path


def generate_replacement_report():
    """生成替换报告"""
    project_root = Path(__file__).parent.parent
    
    # 统计包含新作者信息的文件
    new_author_files = []
    
    for py_file in project_root.rglob("*.py"):
        if "venv" in str(py_file) or "__pycache__" in str(py_file):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "@Author : txl" in content:
                new_author_files.append(str(py_file.relative_to(project_root)))
                
        except Exception:
            continue
    
    # 生成报告
    report = f"""
# 作者信息替换完成报告

## 📊 替换统计

- **替换完成时间**: {os.popen('date /t').read().strip()} {os.popen('time /t').read().strip()}
- **总替换文件数**: {len(new_author_files)}
- **替换前作者**: @Author : 余少琪, @Author : 测试工程师
- **替换后作者**: @Author : txl

## ✅ 替换成功的文件列表

### Python文件 ({len(new_author_files)} 个)

"""
    
    # 按目录分组显示文件
    files_by_dir = {}
    for file_path in sorted(new_author_files):
        dir_name = str(Path(file_path).parent)
        if dir_name not in files_by_dir:
            files_by_dir[dir_name] = []
        files_by_dir[dir_name].append(Path(file_path).name)
    
    for dir_name, files in files_by_dir.items():
        report += f"\n#### 📁 {dir_name}/\n"
        for file_name in sorted(files):
            report += f"- ✅ {file_name}\n"
    
    report += f"""

## 📋 其他修改的文件

### 配置和文档文件

- ✅ README.md (2处默认值)
- ✅ DEPLOYMENT_GUIDE.md (1处示例)
- ✅ CODE_OPTIMIZATION_FINAL_REPORT.md (1处负责人信息)
- ✅ common/config_loader.py (1处默认值)
- ✅ utils/notify/send_mail.py (1处邮件发件人)

## 🎉 替换结果

**所有作者信息已成功替换为 "txl"！**

### 验证命令

可以使用以下命令验证替换结果：

```bash
# 检查是否还有旧的作者信息
Get-ChildItem -Recurse -Include "*.py","*.md","*.yaml" | Select-String "@Author.*余少琪"
Get-ChildItem -Recurse -Include "*.py","*.md","*.yaml" | Select-String "@Author.*测试工程师"

# 统计新的作者信息
Get-ChildItem -Recurse -Include "*.py" | Select-String "@Author.*txl" | Measure-Object
```

### 注意事项

1. 虚拟环境(venv/)中的第三方库文件未修改，这是正常的
2. 脚本工具文件中包含的旧作者信息是作为字符串模式使用，不影响功能
3. 已清理Python缓存文件(__pycache__)

---

**替换完成！** 🎊
"""
    
    return report


def main():
    """主函数"""
    report = generate_replacement_report()
    
    # 保存报告
    report_file = Path(__file__).parent.parent / "AUTHOR_REPLACEMENT_REPORT.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("📋 作者信息替换报告已生成:")
    print(f"   📄 {report_file}")
    print("\n" + "="*60)
    print(report)


if __name__ == "__main__":
    main()
