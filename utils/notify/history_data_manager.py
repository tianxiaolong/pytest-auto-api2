#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
History Data Manager Module

This module provides history data management functionality.
"""

"""
历史数据管理器
用于存储和获取测试历史数据，支持趋势分析
@Author : txl
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class HistoryDataManager:
    """历史数据管理器"""
    
    def __init__(self, project_name: str = None):
        """
        初始化历史数据管理器
        
        Args:
            project_name: 项目名称
        """
        self.project_name = project_name or "pytest-auto-api2"
        self.history_dir = Path("logs/history")
        self.history_file = self.history_dir / f"{self.project_name}_history.json"
        
        # 确保目录存在
        self.history_dir.mkdir(parents=True, exist_ok=True)
    
    def save_test_result(self, test_metrics: Any) -> None:
        """
        保存测试结果到历史记录
        
        Args:
            test_metrics: 测试指标对象
        """
        try:
            # 提取当前测试数据
            current_data = {
                "timestamp": datetime.now().isoformat(),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M:%S"),
                "total_cases": getattr(test_metrics, 'total', 0),
                "passed_cases": getattr(test_metrics, 'passed', 0),
                "failed_cases": getattr(test_metrics, 'failed', 0),
                "broken_cases": getattr(test_metrics, 'broken', 0),
                "skipped_cases": getattr(test_metrics, 'skipped', 0),
                "success_rate": getattr(test_metrics, 'pass_rate', 0),
                "execution_time": getattr(test_metrics, 'time', '0'),
                "calculation_method": getattr(test_metrics, 'calculation_method', 'passed only')
            }
            
            # 读取现有历史数据
            history_data = self._load_history_data()
            
            # 添加新记录
            history_data.append(current_data)
            
            # 只保留最近30次记录
            if len(history_data) > 30:
                history_data = history_data[-30:]
            
            # 保存到文件
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)
                
            print(f"📊 历史数据已保存: {self.history_file}")
            
        except Exception as e:
            print(f"⚠️ 保存历史数据失败: {e}")
    
    def get_previous_success_rate(self) -> Optional[float]:
        """
        获取上次测试的成功率
        
        Returns:
            上次测试的成功率，如果没有历史数据则返回None
        """
        try:
            history_data = self._load_history_data()
            
            if len(history_data) >= 2:
                # 返回倒数第二次的成功率（最后一次是当前这次）
                return history_data[-2].get('success_rate', None)
            elif len(history_data) == 1:
                # 只有一次记录，返回None表示首次执行
                return None
            else:
                # 没有历史数据
                return None
                
        except Exception as e:
            print(f"⚠️ 获取历史成功率失败: {e}")
            return None
    
    def get_trend_statistics(self) -> Dict[str, Any]:
        """
        获取趋势统计信息
        
        Returns:
            包含趋势统计的字典
        """
        try:
            history_data = self._load_history_data()
            
            if len(history_data) < 2:
                return {
                    "has_trend": False,
                    "message": "历史数据不足，无法进行趋势分析"
                }
            
            # 计算最近5次的平均成功率
            recent_5 = history_data[-5:] if len(history_data) >= 5 else history_data
            avg_recent = sum(record.get('success_rate', 0) for record in recent_5) / len(recent_5)
            
            # 计算更早期的平均成功率
            if len(history_data) >= 10:
                earlier_5 = history_data[-10:-5]
                avg_earlier = sum(record.get('success_rate', 0) for record in earlier_5) / len(earlier_5)
            else:
                avg_earlier = avg_recent
            
            # 计算趋势
            trend_diff = avg_recent - avg_earlier
            
            return {
                "has_trend": True,
                "current_rate": history_data[-1].get('success_rate', 0),
                "previous_rate": history_data[-2].get('success_rate', 0),
                "avg_recent_5": round(avg_recent, 1),
                "avg_earlier_5": round(avg_earlier, 1),
                "trend_diff": round(trend_diff, 1),
                "total_records": len(history_data),
                "date_range": {
                    "start": history_data[0].get('date', ''),
                    "end": history_data[-1].get('date', '')
                }
            }
            
        except Exception as e:
            print(f"⚠️ 获取趋势统计失败: {e}")
            return {
                "has_trend": False,
                "message": f"趋势分析失败: {e}"
            }
    
    def get_history_summary(self, limit: int = 10) -> Dict[str, Any]:
        """
        获取历史数据摘要
        
        Args:
            limit: 返回的记录数量限制
            
        Returns:
            历史数据摘要
        """
        try:
            history_data = self._load_history_data()
            
            if not history_data:
                return {
                    "total_records": 0,
                    "message": "暂无历史数据"
                }
            
            # 获取最近的记录
            recent_data = history_data[-limit:] if len(history_data) > limit else history_data
            
            # 计算统计信息
            success_rates = [record.get('success_rate', 0) for record in recent_data]
            
            return {
                "total_records": len(history_data),
                "recent_records": len(recent_data),
                "avg_success_rate": round(sum(success_rates) / len(success_rates), 1),
                "max_success_rate": max(success_rates),
                "min_success_rate": min(success_rates),
                "latest_record": history_data[-1],
                "date_range": {
                    "start": recent_data[0].get('date', ''),
                    "end": recent_data[-1].get('date', '')
                }
            }
            
        except Exception as e:
            print(f"⚠️ 获取历史摘要失败: {e}")
            return {
                "total_records": 0,
                "message": f"获取历史摘要失败: {e}"
            }
    
    def _load_history_data(self) -> list:
        """
        加载历史数据
        
        Returns:
            历史数据列表
        """
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return []
        except Exception as e:
            print(f"⚠️ 加载历史数据失败: {e}")
            return []
    
    def clear_history(self) -> bool:
        """
        清空历史数据
        
        Returns:
            是否清空成功
        """
        try:
            if self.history_file.exists():
                os.remove(self.history_file)
            print(f"🗑️ 历史数据已清空: {self.history_file}")
            return True
        except Exception as e:
            print(f"❌ 清空历史数据失败: {e}")
            return False


def get_history_manager(project_name: str = None) -> HistoryDataManager:
    """
    获取历史数据管理器实例
    
    Args:
        project_name: 项目名称
        
    Returns:
        历史数据管理器实例
    """
    if project_name is None:
        try:
            from utils import config
            project_name = config.project_name
        except:
            project_name = "pytest-auto-api2"
    
    return HistoryDataManager(project_name)


if __name__ == "__main__":
    # 测试历史数据管理器
    manager = get_history_manager()
    
    # 模拟测试数据
    class MockMetrics:
        def __init__(self, success_rate):
            self.total = 100
            self.passed = int(success_rate)
            self.failed = 100 - int(success_rate)
            self.broken = 0
            self.skipped = 0
            self.pass_rate = success_rate
            self.time = "120.5"
            self.calculation_method = "passed only"
    
    # 模拟保存几次数据
    for rate in [85.0, 90.0, 88.0, 92.0, 87.0]:
        metrics = MockMetrics(rate)
        manager.save_test_result(metrics)
    
    # 获取趋势统计
    trend_stats = manager.get_trend_statistics()
    print("📈 趋势统计:")
    print(json.dumps(trend_stats, ensure_ascii=False, indent=2))
    
    # 获取历史摘要
    summary = manager.get_history_summary()
    print("\n📊 历史摘要:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
