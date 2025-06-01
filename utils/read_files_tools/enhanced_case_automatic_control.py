#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
增强版测试用例自动生成器

支持YAML和Excel双数据驱动的智能测试用例生成器。
提供增量更新、变化检测、智能映射等功能。
"""

import os
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from common.setting import ensure_path_sep
from utils import config
from utils.logging_tool.log_control import INFO, ERROR
from utils.read_files_tools.data_driver_control import DataDriverManager, get_test_data
from utils.read_files_tools.get_all_files_path import get_all_files
from utils.read_files_tools.testcase_template import write_testcase_file
from utils.read_files_tools.yaml_control import GetYamlData


class EnhancedTestCaseGenerator:
    """
    增强版测试用例自动生成器

    主要功能：
    1. 支持YAML和Excel双数据驱动
    2. 智能检测数据文件变化
    3. 增量更新测试代码
    4. 文件变化追踪
    5. 智能文件名映射
    """

    def __init__(self):
        """初始化生成器"""
        self.project_root = Path.cwd()
        self.data_driver = DataDriverManager()
        self.change_tracking_file = self.project_root / ".test_case_tracking.json"
        self.file_changes = self._load_change_tracking()

    def _load_change_tracking(self) -> Dict[str, Any]:
        """加载文件变化追踪信息"""
        if self.change_tracking_file.exists():
            try:
                with open(self.change_tracking_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                INFO.logger.warning(f"加载变化追踪文件失败: {e}")

        return {
            "last_update": None,
            "file_hashes": {},
            "generated_files": {},
            "data_driver_type": None
        }

    def _save_change_tracking(self):
        """保存文件变化追踪信息"""
        try:
            with open(self.change_tracking_file, 'w', encoding='utf-8') as f:
                json.dump(self.file_changes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            ERROR.logger.error(f"保存变化追踪文件失败: {e}")

    def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def _get_data_files(self) -> List[Path]:
        """获取当前数据驱动类型对应的数据文件"""
        current_driver_type = getattr(config, 'data_driver_type', 'yaml')
        data_path = Path(self.data_driver.config.current_data_path)

        if not data_path.exists():
            return []

        data_files = []
        if current_driver_type == 'yaml':
            data_files.extend(data_path.rglob("*.yaml"))
            data_files.extend(data_path.rglob("*.yml"))
        elif current_driver_type == 'excel':
            data_files.extend(data_path.rglob("*.xlsx"))
            data_files.extend(data_path.rglob("*.xls"))

        return data_files

    def _detect_changes(self) -> Tuple[List[Path], List[Path], bool]:
        """
        检测文件变化

        Returns:
            (新增文件列表, 修改文件列表, 数据驱动类型是否变化)
        """
        current_driver_type = getattr(config, 'data_driver_type', 'yaml')
        driver_type_changed = self.file_changes.get("data_driver_type") != current_driver_type

        data_files = self._get_data_files()
        new_files = []
        modified_files = []

        current_hashes = {}

        for file_path in data_files:
            # 确保使用绝对路径
            abs_file_path = file_path.resolve()
            try:
                file_key = str(abs_file_path.relative_to(self.project_root.resolve()))
            except ValueError:
                # 如果文件不在项目根目录下，使用文件的绝对路径作为key
                file_key = str(abs_file_path)

            current_hash = self._calculate_file_hash(abs_file_path)
            current_hashes[file_key] = current_hash

            old_hash = self.file_changes["file_hashes"].get(file_key)

            if old_hash is None:
                new_files.append(file_path)
                INFO.logger.info(f"检测到新数据文件: {file_key}")
            elif old_hash != current_hash:
                modified_files.append(file_path)
                INFO.logger.info(f"检测到数据文件变化: {file_key}")

        # 更新哈希记录
        self.file_changes["file_hashes"] = current_hashes
        self.file_changes["data_driver_type"] = current_driver_type

        return new_files, modified_files, driver_type_changed

    def _get_module_info_from_path(self, data_file_path: Path) -> Tuple[str, str]:
        """
        从数据文件路径提取模块信息

        Args:
            data_file_path: 数据文件路径

        Returns:
            (模块名, 推荐的测试文件名)
        """
        # 获取相对于数据根目录的路径
        try:
            data_root = Path(self.data_driver.config.current_data_path)
            relative_path = data_file_path.relative_to(data_root)

            # 提取模块名（第一级目录）
            module_name = relative_path.parts[0] if relative_path.parts else "Unknown"

            # 生成测试文件名
            file_stem = data_file_path.stem
            if file_stem.endswith('_test_data'):
                file_stem = file_stem[:-10]  # 移除 '_test_data' 后缀

            test_file_name = f"test_{file_stem}.py"

            return module_name, test_file_name

        except ValueError:
            # 如果路径不在数据根目录下，使用文件名推断
            module_name = data_file_path.parent.name
            test_file_name = f"test_{data_file_path.stem}.py"
            return module_name, test_file_name

    def _get_yaml_file_for_module(self, module_name: str, test_file_name: str) -> str:
        """
        根据模块名和测试文件名推断对应的YAML文件名

        Args:
            module_name: 模块名
            test_file_name: 测试文件名

        Returns:
            对应的YAML文件名
        """
        # 文件名映射表
        file_mapping = {
            'Login': {
                'test_login.py': 'login.yaml'
            },
            'UserInfo': {
                'test_get_user_info.py': 'get_user_info.yaml'
            },
            'Collect': {
                'test_collect_addtool.py': 'collect_addtool.yaml',
                'test_collect_delete_tool.py': 'collect_delete_tool.yaml',
                'test_collect_tool_list.py': 'collect_tool_list.yaml',
                'test_collect_update_tool.py': 'collect_update_tool.yaml'
            }
        }

        # 查找精确映射
        module_mapping = file_mapping.get(module_name, {})
        yaml_file = module_mapping.get(test_file_name)

        if yaml_file:
            return yaml_file

        # 通用推断
        base_name = test_file_name.replace('test_', '').replace('.py', '')
        return f"{base_name}.yaml"

    def _should_generate_or_update(self, data_file_path: Path, force_update: bool = False) -> bool:
        """
        判断是否应该生成或更新测试文件

        Args:
            data_file_path: 数据文件路径
            force_update: 是否强制更新

        Returns:
            是否应该生成或更新
        """
        config_data = GetYamlData(ensure_path_sep("\\common\\config.yaml")).get_yaml_data()
        real_time_update = config_data.get("real_time_update_test_cases", False)

        module_name, test_file_name = self._get_module_info_from_path(data_file_path)
        test_file_path = Path("test_case") / module_name / test_file_name

        # 如果强制更新或实时更新开启，则更新
        if force_update or real_time_update:
            return True

        # 如果测试文件不存在，则生成
        if not test_file_path.exists():
            return True

        # 如果数据文件是新增或修改的，则更新
        file_key = str(data_file_path.relative_to(self.project_root))
        if file_key not in self.file_changes.get("generated_files", {}):
            return True

        return False

    def generate_test_case_for_file(self, data_file_path: Path, force_update: bool = False) -> bool:
        """
        为单个数据文件生成测试用例

        Args:
            data_file_path: 数据文件路径
            force_update: 是否强制更新

        Returns:
            是否成功生成
        """
        try:
            if not self._should_generate_or_update(data_file_path, force_update):
                return True

            module_name, test_file_name = self._get_module_info_from_path(data_file_path)
            yaml_file_name = self._get_yaml_file_for_module(module_name, test_file_name)

            # 获取测试数据以验证数据文件有效性
            try:
                test_data = get_test_data(module_name, yaml_file_name)
                if not test_data:
                    INFO.logger.warning(f"数据文件 {data_file_path} 没有有效的测试数据，跳过生成")
                    return True
            except Exception as e:
                ERROR.logger.error(f"读取数据文件 {data_file_path} 失败: {e}")
                return False

            # 从第一个测试数据中提取公共信息
            first_case = test_data[0] if test_data else {}
            case_data = list(first_case.values())[0] if first_case else {}

            # 构建生成参数
            generation_params = {
                'allure_epic': getattr(config, 'project_name', 'API测试项目'),
                'allure_feature': module_name,
                'allure_story': f"{module_name}模块测试",
                'class_title': self._generate_class_name(test_file_name),
                'func_title': test_file_name.replace('test_', '').replace('.py', ''),
                'case_path': self._get_test_file_path(module_name, test_file_name),
                'case_ids': list(first_case.keys()) if first_case else [],
                'file_name': yaml_file_name
            }

            # 创建目录
            test_file_path = Path(generation_params['case_path'])
            test_file_path.parent.mkdir(parents=True, exist_ok=True)

            # 生成测试文件
            write_testcase_file(**generation_params)

            # 记录生成信息
            abs_data_file_path = data_file_path.resolve()
            try:
                file_key = str(abs_data_file_path.relative_to(self.project_root.resolve()))
            except ValueError:
                file_key = str(abs_data_file_path)

            if "generated_files" not in self.file_changes:
                self.file_changes["generated_files"] = {}

            self.file_changes["generated_files"][file_key] = {
                "test_file": str(test_file_path),
                "module_name": module_name,
                "generated_at": datetime.now().isoformat(),
                "yaml_file": yaml_file_name
            }

            INFO.logger.info(f"成功生成测试文件: {test_file_path}")
            return True

        except Exception as e:
            ERROR.logger.error(f"生成测试文件失败 {data_file_path}: {e}")
            return False

    def _generate_class_name(self, test_file_name: str) -> str:
        """生成类名"""
        base_name = test_file_name.replace('test_', '').replace('.py', '')
        parts = base_name.split('_')
        return ''.join(word.capitalize() for word in parts)

    def _get_test_file_path(self, module_name: str, test_file_name: str) -> str:
        """获取测试文件路径"""
        return str(Path("test_case") / module_name / test_file_name)

    def generate_all_test_cases(self, force_update: bool = False, check_changes: bool = True) -> Dict[str, Any]:
        """
        生成所有测试用例

        Args:
            force_update: 是否强制更新所有文件
            check_changes: 是否检查文件变化

        Returns:
            生成结果统计
        """
        INFO.logger.info("开始智能测试用例生成...")

        result = {
            "total_files": 0,
            "new_files": 0,
            "modified_files": 0,
            "generated_files": 0,
            "failed_files": 0,
            "skipped_files": 0,
            "driver_type_changed": False,
            "errors": []
        }

        try:
            # 检测变化
            if check_changes:
                new_files, modified_files, driver_type_changed = self._detect_changes()
                result["driver_type_changed"] = driver_type_changed

                if driver_type_changed:
                    INFO.logger.info(f"检测到数据驱动类型变化，将重新生成所有测试文件")
                    force_update = True
            else:
                new_files = modified_files = self._get_data_files()
                driver_type_changed = False

            # 获取所有数据文件
            all_data_files = self._get_data_files()
            result["total_files"] = len(all_data_files)
            result["new_files"] = len(new_files) if check_changes else 0
            result["modified_files"] = len(modified_files) if check_changes else 0

            if not all_data_files:
                INFO.logger.warning("未找到数据文件，请检查数据目录配置")
                return result

            # 处理需要生成的文件
            files_to_process = all_data_files if force_update or driver_type_changed else (new_files + modified_files)

            if not files_to_process and check_changes:
                INFO.logger.info("没有检测到文件变化，跳过生成")
                result["skipped_files"] = result["total_files"]
                return result

            # 生成测试文件
            for data_file in files_to_process:
                try:
                    if self.generate_test_case_for_file(data_file, force_update):
                        result["generated_files"] += 1
                    else:
                        result["failed_files"] += 1
                except Exception as e:
                    result["failed_files"] += 1
                    error_msg = f"处理文件 {data_file} 失败: {str(e)}"
                    result["errors"].append(error_msg)
                    ERROR.logger.error(error_msg)

            # 更新时间戳
            self.file_changes["last_update"] = datetime.now().isoformat()

            # 保存变化追踪
            self._save_change_tracking()

            # 输出结果
            self._print_generation_summary(result)

        except Exception as e:
            error_msg = f"测试用例生成过程出错: {str(e)}"
            result["errors"].append(error_msg)
            ERROR.logger.error(error_msg)

        return result

    def _print_generation_summary(self, result: Dict[str, Any]):
        """打印生成结果摘要"""
        print("\n" + "=" * 60)
        print("📊 智能自动测试用例生成结果")
        print("=" * 60)

        print(f"\n📈 统计信息:")
        print(f"  总数据文件数: {result['total_files']}")
        print(f"  新增文件数: {result['new_files']}")
        print(f"  修改文件数: {result['modified_files']}")
        print(f"  成功生成数: {result['generated_files']}")
        print(f"  生成失败数: {result['failed_files']}")
        print(f"  跳过文件数: {result['skipped_files']}")

        if result["driver_type_changed"]:
            print(f"  🔄 数据驱动类型已变化")

        if result["errors"]:
            print(f"\n❌ 错误信息:")
            for error in result["errors"]:
                print(f"  - {error}")

        if result["generated_files"] > 0:
            print(f"\n✅ 成功生成 {result['generated_files']} 个测试文件")
        elif result["skipped_files"] > 0:
            print(f"\n⏭️ 没有变化，跳过了 {result['skipped_files']} 个文件")

        current_driver = getattr(config, 'data_driver_type', 'yaml')
        print(f"\n🔧 当前数据驱动类型: {current_driver}")

    def clean_obsolete_files(self) -> List[str]:
        """
        清理过时的测试文件

        Returns:
            被清理的文件列表
        """
        cleaned_files = []

        try:
            generated_files = self.file_changes.get("generated_files", {})
            current_data_files = {str(f.relative_to(self.project_root)) for f in self._get_data_files()}

            for data_file_key, file_info in list(generated_files.items()):
                if data_file_key not in current_data_files:
                    # 数据文件已被删除，清理对应的测试文件
                    test_file_path = Path(file_info["test_file"])
                    if test_file_path.exists():
                        try:
                            test_file_path.unlink()
                            cleaned_files.append(str(test_file_path))
                            INFO.logger.info(f"清理过时测试文件: {test_file_path}")
                        except Exception as e:
                            ERROR.logger.error(f"清理文件失败 {test_file_path}: {e}")

                    # 从追踪记录中移除
                    del generated_files[data_file_key]

            if cleaned_files:
                self._save_change_tracking()

        except Exception as e:
            ERROR.logger.error(f"清理过时文件时出错: {e}")

        return cleaned_files


def main():
    """主函数 - 提供命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description='增强版测试用例生成器')
    parser.add_argument('--force', '-f', action='store_true', help='强制重新生成所有测试文件')
    parser.add_argument('--no-check', action='store_true', help='不检查文件变化，处理所有文件')
    parser.add_argument('--clean', action='store_true', help='清理过时的测试文件')

    args = parser.parse_args()

    generator = EnhancedTestCaseGenerator()

    if args.clean:
        cleaned_files = generator.clean_obsolete_files()
        if cleaned_files:
            print(f"✅ 清理了 {len(cleaned_files)} 个过时文件")
        else:
            print("ℹ️ 没有发现过时文件")

    result = generator.generate_all_test_cases(
        force_update=args.force,
        check_changes=not args.no_check
    )

    # 返回适当的退出码
    if result["failed_files"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
