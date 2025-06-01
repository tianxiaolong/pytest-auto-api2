#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Report Manager Tool

This module provides report management functionality.
"""

"""
报告管理工具
管理带时间戳的Allure报告，提供清理、查看、归档等功能
@Author : txl
"""

import os
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class ReportManager:
    """报告管理器"""
    
    def __init__(self, report_base_dir: str = "./report"):
        """
        初始化报告管理器
        
        Args:
            report_base_dir: 报告基础目录
        """
        self.report_base_dir = Path(report_base_dir)
        self.html_pattern = "html_"
    
    def list_timestamped_reports(self) -> List[Dict[str, Any]]:
        """
        列出所有带时间戳的报告
        
        Returns:
            报告信息列表
        """
        reports = []
        
        if not self.report_base_dir.exists():
            return reports
        
        for item in self.report_base_dir.iterdir():
            if item.is_dir() and item.name.startswith(self.html_pattern):
                timestamp_str = item.name[len(self.html_pattern):]
                
                try:
                    # 解析时间戳
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    
                    # 获取报告信息
                    index_file = item / "index.html"
                    size = self._get_directory_size(item)
                    
                    reports.append({
                        "name": item.name,
                        "path": str(item),
                        "timestamp": timestamp,
                        "timestamp_str": timestamp_str,
                        "formatted_time": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        "exists": index_file.exists(),
                        "size_mb": round(size / (1024 * 1024), 2),
                        "age_days": (datetime.now() - timestamp).days
                    })
                except ValueError:
                    # 时间戳格式不正确，跳过
                    continue
        
        # 按时间戳排序（最新的在前）
        reports.sort(key=lambda x: x["timestamp"], reverse=True)
        return reports
    
    def clean_old_reports(self, keep_days: int = 7, keep_count: int = 10) -> Dict[str, Any]:
        """
        清理旧的报告
        
        Args:
            keep_days: 保留天数
            keep_count: 最少保留数量
            
        Returns:
            清理结果
        """
        reports = self.list_timestamped_reports()
        
        if not reports:
            return {
                "success": True,
                "message": "没有找到带时间戳的报告",
                "deleted_count": 0,
                "kept_count": 0
            }
        
        # 计算需要删除的报告
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        to_delete = []
        to_keep = []
        
        for report in reports:
            if len(to_keep) < keep_count:
                # 保留最新的N个报告
                to_keep.append(report)
            elif report["timestamp"] > cutoff_date:
                # 保留指定天数内的报告
                to_keep.append(report)
            else:
                # 标记为删除
                to_delete.append(report)
        
        # 执行删除
        deleted_count = 0
        deleted_size = 0
        errors = []
        
        for report in to_delete:
            try:
                report_path = Path(report["path"])
                if report_path.exists():
                    deleted_size += self._get_directory_size(report_path)
                    shutil.rmtree(report_path)
                    deleted_count += 1
                    print(f"🗑️ 已删除报告: {report['name']} ({report['formatted_time']})")
            except Exception as e:
                error_msg = f"删除报告失败 {report['name']}: {e}"
                errors.append(error_msg)
                print(f"❌ {error_msg}")
        
        return {
            "success": len(errors) == 0,
            "message": f"清理完成，删除 {deleted_count} 个报告，保留 {len(to_keep)} 个报告",
            "deleted_count": deleted_count,
            "kept_count": len(to_keep),
            "deleted_size_mb": round(deleted_size / (1024 * 1024), 2),
            "errors": errors
        }
    
    def get_latest_report(self) -> Dict[str, Any]:
        """
        获取最新的报告信息
        
        Returns:
            最新报告信息
        """
        reports = self.list_timestamped_reports()
        
        if not reports:
            return {
                "exists": False,
                "message": "没有找到带时间戳的报告"
            }
        
        latest = reports[0]
        latest["exists"] = True
        return latest
    
    def archive_old_reports(self, archive_dir: str = "./report/archive", keep_days: int = 30) -> Dict[str, Any]:
        """
        归档旧报告
        
        Args:
            archive_dir: 归档目录
            keep_days: 归档天数阈值
            
        Returns:
            归档结果
        """
        reports = self.list_timestamped_reports()
        archive_path = Path(archive_dir)
        archive_path.mkdir(parents=True, exist_ok=True)
        
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        archived_count = 0
        errors = []
        
        for report in reports:
            if report["timestamp"] < cutoff_date:
                try:
                    source_path = Path(report["path"])
                    target_path = archive_path / report["name"]
                    
                    if source_path.exists():
                        shutil.move(str(source_path), str(target_path))
                        archived_count += 1
                        print(f"📦 已归档报告: {report['name']} -> {target_path}")
                        
                except Exception as e:
                    error_msg = f"归档报告失败 {report['name']}: {e}"
                    errors.append(error_msg)
                    print(f"❌ {error_msg}")
        
        return {
            "success": len(errors) == 0,
            "message": f"归档完成，归档 {archived_count} 个报告",
            "archived_count": archived_count,
            "archive_dir": str(archive_path),
            "errors": errors
        }
    
    def _get_directory_size(self, path: Path) -> int:
        """
        获取目录大小
        
        Args:
            path: 目录路径
            
        Returns:
            目录大小（字节）
        """
        total_size = 0
        try:
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception:
            pass
        return total_size


def show_reports_list():
    """显示报告列表"""
    manager = ReportManager()
    reports = manager.list_timestamped_reports()
    
    if not reports:
        print("📋 没有找到带时间戳的报告")
        return
    
    print(f"📋 找到 {len(reports)} 个带时间戳的报告:")
    print("-" * 80)
    print(f"{'序号':<4} {'报告名称':<20} {'生成时间':<20} {'大小(MB)':<10} {'天数':<6} {'状态'}")
    print("-" * 80)
    
    for i, report in enumerate(reports, 1):
        status = "✅ 正常" if report["exists"] else "❌ 缺失"
        print(f"{i:<4} {report['name']:<20} {report['formatted_time']:<20} "
              f"{report['size_mb']:<10} {report['age_days']:<6} {status}")


def clean_reports_interactive():
    """交互式清理报告"""
    manager = ReportManager()
    
    print("🧹 报告清理工具")
    print("=" * 50)
    
    try:
        keep_days = int(input("请输入保留天数 [默认: 7]: ") or "7")
        keep_count = int(input("请输入最少保留数量 [默认: 10]: ") or "10")
        
        print(f"\n📊 清理策略:")
        print(f"  保留天数: {keep_days} 天")
        print(f"  最少保留: {keep_count} 个")
        
        confirm = input("\n确认执行清理? (y/N): ").lower().strip()
        if confirm == 'y':
            result = manager.clean_old_reports(keep_days, keep_count)
            print(f"\n✅ {result['message']}")
            if result['errors']:
                print("❌ 错误信息:")
                for error in result['errors']:
                    print(f"  {error}")
        else:
            print("❌ 已取消清理操作")
            
    except ValueError:
        print("❌ 输入格式错误，请输入数字")
    except KeyboardInterrupt:
        print("\n❌ 操作已取消")


def main():
    """主函数"""
    print("📊 Allure报告管理工具")
    print("=" * 50)
    
    while True:
        print("\n请选择操作:")
        print("1. 📋 查看报告列表")
        print("2. 🧹 清理旧报告")
        print("3. 📦 归档旧报告")
        print("4. 📈 获取最新报告")
        print("5. 📊 报告统计")
        print("0. 退出")
        
        try:
            choice = input("\n请输入选择 (0-5): ").strip()
            
            if choice == '0':
                print("👋 再见！")
                break
            elif choice == '1':
                show_reports_list()
            elif choice == '2':
                clean_reports_interactive()
            elif choice == '3':
                manager = ReportManager()
                result = manager.archive_old_reports()
                print(f"✅ {result['message']}")
            elif choice == '4':
                manager = ReportManager()
                latest = manager.get_latest_report()
                if latest["exists"]:
                    print(f"📈 最新报告: {latest['name']}")
                    print(f"   生成时间: {latest['formatted_time']}")
                    print(f"   报告路径: {latest['path']}/index.html")
                else:
                    print("❌ 没有找到报告")
            elif choice == '5':
                manager = ReportManager()
                reports = manager.list_timestamped_reports()
                if reports:
                    total_size = sum(r['size_mb'] for r in reports)
                    avg_age = sum(r['age_days'] for r in reports) / len(reports)
                    print(f"📊 报告统计:")
                    print(f"   总报告数: {len(reports)}")
                    print(f"   总大小: {total_size:.2f} MB")
                    print(f"   平均天数: {avg_age:.1f} 天")
                    print(f"   最新报告: {reports[0]['formatted_time']}")
                    print(f"   最旧报告: {reports[-1]['formatted_time']}")
                else:
                    print("📊 暂无报告统计数据")
            else:
                print("❌ 无效选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")


if __name__ == "__main__":
    main()
