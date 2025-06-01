#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量替换作者信息脚本
将项目中的作者信息统一替换为 txl
"""

import os
import re
from pathlib import Path


def replace_author_in_file(file_path: Path):
    """替换单个文件中的作者信息"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换 @Author : 余少琪
        content = re.sub(r'# @Author\s*:\s*余少琪', '# @Author : txl', content)
        
        # 替换 @Author  : 余少琪 (注意有两个空格)
        content = re.sub(r'# @Author\s+:\s*余少琪', '# @Author : txl', content)
        
        # 替换 @Author : 测试工程师
        content = re.sub(r'@Author\s*:\s*测试工程师', '@Author : txl', content)
        
        # 替换 @Author  : 测试工程师 (注意有两个空格)
        content = re.sub(r'@Author\s+:\s*测试工程师', '@Author : txl', content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 已更新: {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ 更新失败 {file_path}: {e}")
        return False


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent
    
    # 需要替换的文件列表
    files_to_update = [
        # 余少琪的文件
        "utils/other_tools/install_tool/install_requirements.py",
        "utils/other_tools/get_local_ip.py", 
        "utils/other_tools/jsonpath_date_replace.py",
        "utils/other_tools/thread_tool.py",
        "utils/read_files_tools/case_automatic_control.py",
        "utils/read_files_tools/clean_files.py",
        "utils/read_files_tools/get_all_files_path.py",
        "utils/read_files_tools/get_yaml_data_analysis.py",
        "utils/read_files_tools/regular_control.py",
        "utils/read_files_tools/swagger_for_yaml.py",
        "utils/read_files_tools/testcase_template.py",
        "utils/read_files_tools/yaml_control.py",
        "utils/recording/mitmproxy_control.py",
        "utils/requests_tool/dependent_case.py",
        "utils/requests_tool/encryption_algorithm_control.py",
        "utils/requests_tool/set_current_request_cache.py",
        "utils/requests_tool/teardown_control.py",
        "utils/times_tool/time_control.py",
        
        # 测试工程师的文件
        "common/config_loader.py",
        "scripts/auto_fix_code.py",
        "scripts/check_imports.py",
        "scripts/check_real_issues.py",
        "scripts/code_quality_check.py",
        "scripts/create_excel_template.py",
        "scripts/final_fix.py",
        "scripts/optimize_comments.py",
        "scripts/relaxed_quality_check.py",
        "scripts/restructure_data_directory.py",
        "scripts/update_test_imports.py",
        "scripts/verify_imports.py",
        "tools/advanced_code_optimizer.py",
        "tools/auto_code_formatter.py",
        "tools/batch_optimizer.py",
        "tools/code_quality_checker.py",
        "tools/deep_cleaner.py",
        "tools/project_cleaner.py",
        "tools/project_structure_analyzer.py",
        "tools/smart_quality_checker.py",
        "utils/assertion/assert_control.py",
        "utils/cache_process/cache_control.py",
        "utils/health/health_check.py",
        "utils/logging_tool/encoding_fix.py",
        "utils/logging_tool/log_control.py",
        "utils/mysql_tool/mysql_control.py",
        "utils/other_tools/exceptions.py",
        "utils/performance/performance_monitor.py",
        "utils/read_files_tools/data_driver_control.py",
        "utils/read_files_tools/excel_control.py",
        "utils/requests_tool/request_control.py",
        "utils/security/security_manager.py",
        "utils/common_utils.py",
        "run_tests_ordered.py",
        "test_excel_execution.py",
        "verify_project.py"
    ]
    
    print("🔄 开始批量替换作者信息...")
    print("=" * 60)
    
    success_count = 0
    total_count = len(files_to_update)
    
    for file_path_str in files_to_update:
        file_path = project_root / file_path_str
        if file_path.exists():
            if replace_author_in_file(file_path):
                success_count += 1
        else:
            print(f"⚠️ 文件不存在: {file_path}")
    
    print("=" * 60)
    print(f"🎉 替换完成! 成功: {success_count}/{total_count}")


if __name__ == "__main__":
    main()
