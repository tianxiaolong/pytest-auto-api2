#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
import sys
from pathlib import Path
from typing import List, Dict, Any, Set
import json
import time

"""
项目清理工具
安全清理缓存、历史数据和无用文件

@Time   : 2023-12-20
@Author : txl
"""


class ProjectCleaner:
    """项目清理器"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.cleaned_files = []
        self.cleaned_dirs = []
        self.saved_space = 0
        self.stats = {
            'cache_files': 0,
            'log_files': 0,
            'report_files': 0,
            'temp_files': 0,
            'duplicate_docs': 0,
            'old_scripts': 0
        }

        # 定义需要清理的文件和目录
        self.cleanup_patterns = {
            'cache_dirs': {
                '__pycache__',
                '.pytest_cache',
                '.mypy_cache',
                'node_modules',
                '.coverage',
                'htmlcov'
            },
            'cache_files': {
                '*.pyc',
                '*.pyo',
                '*.pyd',
                '*.so',
                '.coverage',
                'coverage.xml'
            },
            'temp_files': {
                '*.tmp',
                '*.temp',
                '*.bak',
                '*.swp',
                '*.swo',
                '*~',
                '.DS_Store',
                'Thumbs.db'
            },
            'log_files_old': {
                # 保留最近的日志，删除旧的
                'logs/*-2023-*.log',  # 2023年的日志
                'logs/error-*.log',  # 空的错误日志
                'logs/warning-*.log'  # 空的警告日志
            },
            'report_files_old': {
                'report/tmp/*',  # 临时报告文件
                'report/html/data/attachments/*'  # 旧的附件
            }
        }

        # 需要保留的重要文件
        self.keep_files = {
            'requirements.txt',
            'pytest.ini',
            'pyproject.toml',
            '.flake8',
            '.pre-commit-config.yaml',
            'README.md',
            'run.py'
        }

        # 重复的文档文件（保留最新的）
        self.duplicate_docs = [
            'FINAL_PROJECT_STATUS.md',
            'FINAL_PROJECT_STATUS_COMPLETE.md',
            'FINAL_PROJECT_SUMMARY.md',
            'FINAL_OPTIMIZATION_SUMMARY.md',
            'FINAL_PERFECT_OPTIMIZATION_SUMMARY.md',
            'FINAL_STATUS_REPORT.md',
            'PROJECT_OPTIMIZATION_COMPLETE.md',
            'PROJECT_OPTIMIZATION_SUMMARY.md',
            'PROJECT_SUMMARY.md',
            'OPTIMIZATION_SUMMARY.md',
            'CONFIG_FIX_SUMMARY.md',
            'IMPORT_FIX_SUMMARY.md'
        ]

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
            return f"{size_bytes / 1024:.1f}KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f}MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f}GB"

    def clean_cache_dirs(self) -> List[str]:
        """清理缓存目录"""
        cleaned = []

        for cache_dir in self.cleanup_patterns['cache_dirs']:
            cache_paths = list(self.project_root.rglob(cache_dir))

            for cache_path in cache_paths:
                if cache_path.is_dir():
                    try:
                        # 计算目录大小
                        dir_size = sum(self.get_file_size(f) for f in cache_path.rglob('*') if f.is_file())

                        shutil.rmtree(cache_path)
                        cleaned.append(str(cache_path))
                        self.saved_space += dir_size
                        self.stats['cache_files'] += 1

                        print(f"✅ 删除缓存目录: {cache_path} ({self.format_size(dir_size)})")
                    except Exception as e:
                        print(f"❌ 删除缓存目录失败 {cache_path}: {e}")

        return cleaned

    def clean_cache_files(self) -> List[str]:
        """清理缓存文件"""
        cleaned = []

        for pattern in self.cleanup_patterns['cache_files']:
            if pattern.startswith('*'):
                # 通配符模式
                cache_files = list(self.project_root.rglob(pattern))
            else:
                # 具体文件
                cache_file = self.project_root / pattern
                cache_files = [cache_file] if cache_file.exists() else []

            for cache_file in cache_files:
                if cache_file.is_file():
                    try:
                        file_size = self.get_file_size(cache_file)
                        cache_file.unlink()
                        cleaned.append(str(cache_file))
                        self.saved_space += file_size
                        self.stats['cache_files'] += 1

                        print(f"✅ 删除缓存文件: {cache_file} ({self.format_size(file_size)})")
                    except Exception as e:
                        print(f"❌ 删除缓存文件失败 {cache_file}: {e}")

        return cleaned

    def clean_temp_files(self) -> List[str]:
        """清理临时文件"""
        cleaned = []

        for pattern in self.cleanup_patterns['temp_files']:
            temp_files = list(self.project_root.rglob(pattern))

            for temp_file in temp_files:
                if temp_file.is_file():
                    try:
                        file_size = self.get_file_size(temp_file)
                        temp_file.unlink()
                        cleaned.append(str(temp_file))
                        self.saved_space += file_size
                        self.stats['temp_files'] += 1

                        print(f"✅ 删除临时文件: {temp_file} ({self.format_size(file_size)})")
                    except Exception as e:
                        print(f"❌ 删除临时文件失败 {temp_file}: {e}")

        return cleaned

    def clean_old_logs(self) -> List[str]:
        """清理旧日志文件"""
        cleaned = []
        logs_dir = self.project_root / 'logs'

        if not logs_dir.exists():
            return cleaned

        # 清理2023年的日志文件
        old_logs = list(logs_dir.glob('*-2023-*.log'))

        # 清理空的日志文件
        for log_file in logs_dir.glob('*.log'):
            if log_file.stat().st_size == 0:
                old_logs.append(log_file)

        for log_file in old_logs:
            try:
                file_size = self.get_file_size(log_file)
                log_file.unlink()
                cleaned.append(str(log_file))
                self.saved_space += file_size
                self.stats['log_files'] += 1

                print(f"✅ 删除旧日志: {log_file} ({self.format_size(file_size)})")
            except Exception as e:
                print(f"❌ 删除日志文件失败 {log_file}: {e}")

        return cleaned

    def clean_old_reports(self) -> List[str]:
        """清理旧报告文件"""
        cleaned = []

        # 清理临时报告文件
        report_tmp = self.project_root / 'report' / 'tmp'
        if report_tmp.exists():
            try:
                # 计算目录大小
                dir_size = sum(self.get_file_size(f) for f in report_tmp.rglob('*') if f.is_file())

                # 保留目录，但清空内容
                for item in report_tmp.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)

                cleaned.append(str(report_tmp))
                self.saved_space += dir_size
                self.stats['report_files'] += 1

                print(f"✅ 清理报告临时文件: {report_tmp} ({self.format_size(dir_size)})")
            except Exception as e:
                print(f"❌ 清理报告文件失败 {report_tmp}: {e}")

        return cleaned

    def clean_duplicate_docs(self) -> List[str]:
        """清理重复的文档文件"""
        cleaned = []

        # 保留最重要的文档，删除重复的
        keep_docs = {
            'README.md',
            'PROJECT_STRUCTURE.md',
            'DATA_DRIVER_GUIDE.md',
            'DEPLOYMENT_GUIDE.md',
            'CODE_OPTIMIZATION_FINAL_REPORT.md'
        }

        for doc_file in self.duplicate_docs:
            doc_path = self.project_root / doc_file
            if doc_path.exists() and doc_file not in keep_docs:
                try:
                    file_size = self.get_file_size(doc_path)
                    doc_path.unlink()
                    cleaned.append(str(doc_path))
                    self.saved_space += file_size
                    self.stats['duplicate_docs'] += 1

                    print(f"✅ 删除重复文档: {doc_file} ({self.format_size(file_size)})")
                except Exception as e:
                    print(f"❌ 删除文档失败 {doc_file}: {e}")

        return cleaned

    def clean_old_scripts(self) -> List[str]:
        """清理旧的脚本文件"""
        cleaned = []

        # 清理一些测试和调试脚本
        old_scripts = [
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

        for script in old_scripts:
            script_path = self.project_root / script
            if script_path.exists():
                try:
                    file_size = self.get_file_size(script_path)
                    script_path.unlink()
                    cleaned.append(str(script_path))
                    self.saved_space += file_size
                    self.stats['old_scripts'] += 1

                    print(f"✅ 删除旧脚本: {script} ({self.format_size(file_size)})")
                except Exception as e:
                    print(f"❌ 删除脚本失败 {script}: {e}")

        return cleaned

    def clean_json_reports(self) -> List[str]:
        """清理JSON报告文件"""
        cleaned = []

        json_files = [
            'code_quality_report.json',
            'project_optimization_report.json'
        ]

        for json_file in json_files:
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

    def clean_project(self, confirm: bool = True) -> Dict[str, Any]:
        """清理整个项目"""
        if confirm:
            print("🧹 开始项目清理...")
            print("⚠️  这将删除缓存、临时文件、旧日志和重复文档")
            response = input("确认继续？(y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("❌ 清理已取消")
                return {'cancelled': True}

        print("\n🚀 开始清理项目...")
        start_time = time.time()

        # 执行各种清理
        self.cleaned_files.extend(self.clean_cache_dirs())
        self.cleaned_files.extend(self.clean_cache_files())
        self.cleaned_files.extend(self.clean_temp_files())
        self.cleaned_files.extend(self.clean_old_logs())
        self.cleaned_files.extend(self.clean_old_reports())
        self.cleaned_files.extend(self.clean_duplicate_docs())
        self.cleaned_files.extend(self.clean_old_scripts())
        self.cleaned_files.extend(self.clean_json_reports())

        end_time = time.time()

        # 生成清理报告
        report = {
            'total_files_cleaned': len(self.cleaned_files),
            'space_saved': self.format_size(self.saved_space),
            'space_saved_bytes': self.saved_space,
            'cleanup_time': f"{end_time - start_time:.2f}秒",
            'stats': self.stats,
            'cleaned_files': self.cleaned_files[:20]  # 只显示前20个
        }

        return report

    def generate_cleanup_summary(self, report: Dict[str, Any]):
        """生成清理摘要"""
        print(f"\n📊 清理完成摘要:")
        print(f"   清理文件数: {report['total_files_cleaned']}")
        print(f"   节省空间: {report['space_saved']}")
        print(f"   清理时间: {report['cleanup_time']}")

        print(f"\n📋 清理统计:")
        for category, count in report['stats'].items():
            if count > 0:
                print(f"   {category}: {count}")

        if report['cleaned_files']:
            print(f"\n📝 清理的文件 (前20个):")
            for file_path in report['cleaned_files']:
                print(f"   - {file_path}")

        print(f"\n💡 建议:")
        print("   1. 运行测试确保功能正常:")
        print("      python -m pytest test_case/Login/test_login.py -v")
        print("   2. 重新生成报告:")
        print("      python -m pytest test_case/ --alluredir=./report/tmp")
        print("   3. 定期清理以保持项目整洁")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="项目清理工具")
    parser.add_argument("--auto", action="store_true", help="自动清理，不需要确认")
    parser.add_argument("--dry-run", action="store_true", help="模拟运行，不实际删除文件")

    args = parser.parse_args()

    cleaner = ProjectCleaner()

    if args.dry_run:
        print("🔍 模拟运行模式 - 不会实际删除文件")
        # 这里可以添加模拟运行的逻辑
        return

    report = cleaner.clean_project(confirm=not args.auto)

    if not report.get('cancelled'):
        cleaner.generate_cleanup_summary(report)


if __name__ == "__main__":
    main()
