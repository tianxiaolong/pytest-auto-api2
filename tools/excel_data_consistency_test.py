#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Excel数据驱动一致性测试

验证Excel数据驱动模式下的数据一致性，确保：
1. Excel数据驱动正常工作
2. 各模块数据文件正确读取
3. 数据格式符合预期
"""

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any


class ExcelDataConsistencyTester:
    """Excel数据驱动一致性测试器"""
    
    def __init__(self):
        """初始化测试器"""
        self.project_root = Path(__file__).parent.parent
        
    def test_excel_data_reading(self) -> Dict[str, Any]:
        """测试Excel数据读取"""
        print("📊 测试Excel数据读取...")
        
        result = {
            'status': 'success',
            'modules': {},
            'total_cases': 0,
            'errors': []
        }
        
        try:
            from utils.read_files_tools.data_driver_control import switch_data_driver, get_test_data
            
            # 切换到Excel驱动
            switch_data_driver('excel')
            
            # 检查各个模块
            modules_to_check = ['Login', 'UserInfo', 'Collect']
            
            for module_name in modules_to_check:
                try:
                    # 测试不指定文件名的情况
                    data = get_test_data(module_name)
                    case_count = len(data)
                    
                    result['modules'][module_name] = {
                        'status': 'success',
                        'case_count': case_count,
                        'sample_case': data[0] if data else None
                    }
                    result['total_cases'] += case_count
                    print(f"  ✅ {module_name}模块: {case_count} 个用例")
                    
                except Exception as e:
                    result['modules'][module_name] = {
                        'status': 'error',
                        'error': str(e)
                    }
                    result['errors'].append(f"{module_name}: {str(e)}")
                    print(f"  ❌ {module_name}模块: 错误 - {str(e)[:50]}...")
            
            # 恢复到YAML驱动
            switch_data_driver('yaml')
            
        except Exception as e:
            result['status'] = 'error'
            result['errors'].append(f"Excel数据驱动测试失败: {str(e)}")
            print(f"❌ Excel数据驱动测试失败: {e}")
        
        return result
    
    def test_excel_pytest_collection(self) -> Dict[str, Any]:
        """测试Excel模式下的pytest收集"""
        print("🔍 测试Excel模式下的pytest收集...")
        
        result = {
            'status': 'success',
            'collection_count': 0,
            'errors': []
        }
        
        # 创建临时测试脚本
        test_script = '''
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.read_files_tools.data_driver_control import switch_data_driver

# 切换到Excel数据驱动
switch_data_driver('excel')
print("已切换到Excel数据驱动")
'''
        
        try:
            # 写入临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(test_script)
                temp_file = f.name
            
            # 执行切换脚本
            subprocess.run([sys.executable, temp_file], 
                         capture_output=True, text=True, timeout=30, cwd=self.project_root)
            
            # 运行pytest收集
            pytest_result = subprocess.run(
                [sys.executable, '-m', 'pytest', '--collect-only', '-q'],
                capture_output=True, text=True, timeout=60, cwd=self.project_root
            )
            
            if pytest_result.returncode == 0:
                # 解析收集结果
                output_lines = pytest_result.stdout.splitlines()
                for line in output_lines:
                    if "tests collected" in line:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part.isdigit() and i + 1 < len(parts) and parts[i + 1] == "tests":
                                result['collection_count'] = int(part)
                                break
                
                print(f"  ✅ Excel模式收集用例数: {result['collection_count']}")
            else:
                result['status'] = 'error'
                result['errors'].append(f"pytest收集失败: {pytest_result.stderr}")
                print(f"  ❌ pytest收集失败: {pytest_result.stderr[:100]}...")
            
            # 清理临时文件
            Path(temp_file).unlink(missing_ok=True)
            
            # 恢复到YAML模式
            restore_script = '''
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.read_files_tools.data_driver_control import switch_data_driver

# 恢复到YAML数据驱动
switch_data_driver('yaml')
print("已恢复到YAML数据驱动")
'''
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(restore_script)
                restore_file = f.name
            
            subprocess.run([sys.executable, restore_file], 
                         capture_output=True, text=True, timeout=30, cwd=self.project_root)
            Path(restore_file).unlink(missing_ok=True)
            
        except Exception as e:
            result['status'] = 'error'
            result['errors'].append(f"Excel pytest收集测试失败: {str(e)}")
            print(f"❌ Excel pytest收集测试失败: {e}")
        
        return result
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """运行全面测试"""
        print("\n" + "=" * 60)
        print("📊 Excel数据驱动一致性测试")
        print("=" * 60)
        
        # 1. 测试Excel数据读取
        excel_result = self.test_excel_data_reading()
        
        # 2. 测试pytest收集
        collection_result = self.test_excel_pytest_collection()
        
        # 3. 汇总结果
        overall_result = {
            'excel_data_test': excel_result,
            'pytest_collection_test': collection_result,
            'summary': {
                'excel_total_cases': excel_result.get('total_cases', 0),
                'pytest_collection_count': collection_result.get('collection_count', 0),
                'all_tests_passed': (
                    excel_result.get('status') == 'success' and 
                    collection_result.get('status') == 'success'
                )
            }
        }
        
        return overall_result
    
    def print_summary(self, result: Dict[str, Any]):
        """打印测试摘要"""
        print(f"\n📈 Excel数据驱动测试摘要:")
        
        excel_test = result['excel_data_test']
        collection_test = result['pytest_collection_test']
        summary = result['summary']
        
        print(f"  Excel数据读取: {'✅ 成功' if excel_test['status'] == 'success' else '❌ 失败'}")
        print(f"  Excel总用例数: {summary['excel_total_cases']}")
        
        print(f"  pytest收集测试: {'✅ 成功' if collection_test['status'] == 'success' else '❌ 失败'}")
        print(f"  pytest收集用例数: {summary['pytest_collection_count']}")
        
        if summary['all_tests_passed']:
            print(f"\n🎉 Excel数据驱动一致性测试全部通过！")
        else:
            print(f"\n⚠️ Excel数据驱动测试发现问题：")
            for error in excel_test.get('errors', []):
                print(f"    - {error}")
            for error in collection_test.get('errors', []):
                print(f"    - {error}")


def main():
    """主函数"""
    tester = ExcelDataConsistencyTester()
    result = tester.run_comprehensive_test()
    tester.print_summary(result)
    
    # 返回适当的退出码
    if result['summary']['all_tests_passed']:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
