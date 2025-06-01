#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Deep Cleaner Module

This module provides deep cleaner functionality.
"""

"""
深度清理工具
清理项目中的重复文档、测试脚本和无用文件

@Time   : 2023-12-20
@Author : txl
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import time


class DeepCleaner:
    """深度清理器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.cleaned_files = []
        self.saved_space = 0
        
        # 需要删除的重复文档
        self.duplicate_docs = [
            'FINAL_PROJECT_STATUS.md',
            'FINAL_PROJECT_STATUS_COMPLETE.md',
            'FINAL_OPTIMIZATION_SUMMARY.md', 
            'FINAL_PERFECT_OPTIMIZATION_SUMMARY.md',
            'FINAL_STATUS_REPORT.md',
            'PROJECT_OPTIMIZATION_COMPLETE.md',
            'PROJECT_OPTIMIZATION_SUMMARY.md',
            'PROJECT_SUMMARY.md',
            'OPTIMIZATION_SUMMARY.md',
            'CONFIG_FIX_SUMMARY.md',
            'IMPORT_FIX_SUMMARY.md',
            'README_NEW.md'  # 已经合并到README.md
        ]
        
        # 需要删除的测试和调试脚本
        self.test_scripts = [
            'debug_excel_data.py',
            'test_encoding_fix.py',
            'test_excel_data_driver.py',
            'test_excel_execution.py',
            'test_functionality.py',
            'test_log_encoding.py',
            'verify_fixes.py',
            'final_quality_check.py',
            'project_optimization_check.py'
        ]
        
        # 需要删除的JSON报告文件
        self.json_reports = [
            'code_quality_report.json',
            'project_optimization_report.json',
            'performance_report.json'
        ]
        
        # 保留的重要文档
        self.keep_docs = {
            'README.md',
            'PROJECT_STRUCTURE.md',
            'DATA_DRIVER_GUIDE.md',
            'DEPLOYMENT_GUIDE.md',
            'CODE_OPTIMIZATION_FINAL_REPORT.md',
            'FINAL_PROJECT_SUMMARY.md'  # 最终总结保留
        }
    
    def get_file_size(self, file_path: Path) -> int:
        """获取文件大小"""
        try:
            return file_path.stat().st_size
        except:
            return 0
    
    def format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes}B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.1f}KB"
        else:
            return f"{size_bytes/(1024*1024):.1f}MB"
    
    def clean_duplicate_docs(self) -> List[str]:
        """清理重复文档"""
        cleaned = []
        
        print("📝 清理重复文档...")
        
        for doc_file in self.duplicate_docs:
            doc_path = self.project_root / doc_file
            if doc_path.exists():
                try:
                    file_size = self.get_file_size(doc_path)
                    doc_path.unlink()
                    cleaned.append(str(doc_path))
                    self.saved_space += file_size
                    
                    print(f"✅ 删除重复文档: {doc_file} ({self.format_size(file_size)})")
                except Exception as e:
                    print(f"❌ 删除文档失败 {doc_file}: {e}")
        
        return cleaned
    
    def clean_test_scripts(self) -> List[str]:
        """清理测试脚本"""
        cleaned = []
        
        print("\n🧪 清理测试和调试脚本...")
        
        for script in self.test_scripts:
            script_path = self.project_root / script
            if script_path.exists():
                try:
                    file_size = self.get_file_size(script_path)
                    script_path.unlink()
                    cleaned.append(str(script_path))
                    self.saved_space += file_size
                    
                    print(f"✅ 删除测试脚本: {script} ({self.format_size(file_size)})")
                except Exception as e:
                    print(f"❌ 删除脚本失败 {script}: {e}")
        
        return cleaned
    
    def clean_json_reports(self) -> List[str]:
        """清理JSON报告"""
        cleaned = []
        
        print("\n📊 清理JSON报告文件...")
        
        for json_file in self.json_reports:
            json_path = self.project_root / json_file
            if json_path.exists():
                try:
                    file_size = self.get_file_size(json_path)
                    json_path.unlink()
                    cleaned.append(str(json_path))
                    self.saved_space += file_size
                    
                    print(f"✅ 删除JSON报告: {json_file} ({self.format_size(file_size)})")
                except Exception as e:
                    print(f"❌ 删除JSON报告失败 {json_file}: {e}")
        
        return cleaned
    
    def clean_old_logs(self) -> List[str]:
        """清理旧日志"""
        cleaned = []
        
        print("\n📋 清理旧日志文件...")
        
        logs_dir = self.project_root / 'logs'
        if logs_dir.exists():
            # 清理空的日志文件
            for log_file in logs_dir.glob('*.log'):
                if log_file.stat().st_size == 0:
                    try:
                        log_file.unlink()
                        cleaned.append(str(log_file))
                        print(f"✅ 删除空日志: {log_file.name}")
                    except Exception as e:
                        print(f"❌ 删除日志失败 {log_file}: {e}")
        
        return cleaned
    
    def scan_large_files(self) -> List[Dict[str, Any]]:
        """扫描大文件"""
        large_files = []
        
        print("\n🔍 扫描大文件...")
        
        for file_path in self.project_root.rglob('*'):
            if file_path.is_file() and 'venv' not in str(file_path):
                file_size = self.get_file_size(file_path)
                if file_size > 1024 * 1024:  # 大于1MB
                    large_files.append({
                        'path': str(file_path.relative_to(self.project_root)),
                        'size': file_size,
                        'size_str': self.format_size(file_size)
                    })
        
        # 按大小排序
        large_files.sort(key=lambda x: x['size'], reverse=True)
        
        if large_files:
            print("📊 发现的大文件:")
            for file_info in large_files[:10]:  # 显示前10个
                print(f"   {file_info['path']} - {file_info['size_str']}")
        
        return large_files
    
    def clean_project(self) -> Dict[str, Any]:
        """深度清理项目"""
        print("🧹 开始深度清理项目...")
        print("=" * 60)
        
        start_time = time.time()
        
        # 执行各种清理
        self.cleaned_files.extend(self.clean_duplicate_docs())
        self.cleaned_files.extend(self.clean_test_scripts())
        self.cleaned_files.extend(self.clean_json_reports())
        self.cleaned_files.extend(self.clean_old_logs())
        
        # 扫描大文件
        large_files = self.scan_large_files()
        
        end_time = time.time()
        
        # 生成清理报告
        report = {
            'total_files_cleaned': len(self.cleaned_files),
            'space_saved': self.format_size(self.saved_space),
            'space_saved_bytes': self.saved_space,
            'cleanup_time': f"{end_time - start_time:.2f}秒",
            'cleaned_files': self.cleaned_files,
            'large_files': large_files
        }
        
        return report
    
    def generate_cleanup_summary(self, report: Dict[str, Any]):
        """生成清理摘要"""
        print(f"\n📊 深度清理完成摘要:")
        print(f"   清理文件数: {report['total_files_cleaned']}")
        print(f"   节省空间: {report['space_saved']}")
        print(f"   清理时间: {report['cleanup_time']}")
        
        if report['cleaned_files']:
            print(f"\n📝 清理的文件:")
            for file_path in report['cleaned_files']:
                print(f"   - {file_path}")
        
        if report['large_files']:
            print(f"\n📊 大文件提醒 (>1MB):")
            for file_info in report['large_files'][:5]:
                print(f"   {file_info['path']} - {file_info['size_str']}")
        
        print(f"\n✅ 保留的重要文档:")
        for doc in sorted(self.keep_docs):
            doc_path = self.project_root / doc
            if doc_path.exists():
                size = self.format_size(self.get_file_size(doc_path))
                print(f"   ✓ {doc} ({size})")
        
        print(f"\n💡 清理后建议:")
        print("   1. 验证测试功能正常:")
        print("      python -m pytest test_case/Login/test_login.py -v")
        print("   2. 检查项目结构:")
        print("      python tools/project_structure_analyzer.py")
        print("   3. 运行代码质量检查:")
        print("      python tools/smart_quality_checker.py --mode relaxed")


def main():
    """主函数"""
    cleaner = DeepCleaner()
    report = cleaner.clean_project()
    cleaner.generate_cleanup_summary(report)


if __name__ == "__main__":
    main()
