# coding=utf-8
"""
Address Detection Module

This module provides address detection functionality.
"""

"""
@project: pytest-auto-api2
@Author：七月
@file： address_detection.py
@date：2022/11/9 11:42
@blogs: https://blog.csdn.net/weixin_43865008
"""
import copy
from typing import Dict, List

from utils.mysql_tool.mysql_control import MysqlDB


class AddressDetection(MysqlDB):
    """
    地址检测工具类

    用于检测和修复店铺地址数据的一致性问题。
    继承自MysqlDB，具备数据库操作能力。

    主要功能：
    - 获取店铺地址信息
    - 验证地址代码的正确性
    - 检测地址数据不一致问题
    - 生成地址修复建议

    使用场景：
    - 数据质量检查
    - 地址信息校验
    - 数据修复建议
    """

    def get_shop_address_entity_str(self) -> List[Dict]:
        """
        获取所有已经上线并且未删除的店铺地址信息

        排除自定店铺，因为自营店铺没有地址信息。

        Returns:
            店铺信息列表，包含店铺ID、名称、属性等信息
        """
        shop_info = self.query(
            "SELECT id, name, attribute, shop_type, sub_shop_type "
            "FROM `test_obp_supplier`.`supplier_shop` "
            "where status = 2 and delete_flag = 0 and sub_shop_type > 300 "
            "and sub_shop_type = 300"
        )
        return shop_info

    def get_logistics_address_library(self):
        """
        获取平台地址库中的省份code
        :return:
        """

        code = self.query(
            "select name, code from `test_obp_order`.`logistics_address_library` " "where parent_code > 0"
        )

        area_code = {}
        for i in code:
            area_code[i["code"]] = i["name"]
        return area_code

    def get_error_shop(self):
        """
        获取错误的店铺数据
        :return:
        """
        # 获取区域code
        get_logistics_address_library = self.get_logistics_address_library()
        num = 0
        for i in self.get_shop_address_entity_str():
            # 获取店铺地址
            shop_address_entity_str = eval(i["attribute"])["shopAddressEntityStr"]

            if (
                shop_address_entity_str["countiesName"]
                == get_logistics_address_library[str(shop_address_entity_str["countiesCode"])]
            ):
                pass
            else:
                area_name = self.query(
                    "SELECT name, code FROM `test_obp_order`.`logistics_address_library`"
                    f" where parent_code = {shop_address_entity_str['cityCode']} and name = '{shop_address_entity_str['countiesName']}'"
                )
                num += 1

                new_shop_address_entity_str = copy.deepcopy(shop_address_entity_str)
                new_shop_address_entity_str["countiesCode"] = area_name[0]["code"]
                # print(str(f'update obp_supplier.supplier_shop set attribute = json_set(attribute,"$.shopAddressEntityStr.countiesCode",{area_name[0]["code"]}) where id = {i["id"]};'))
                print(
                    f"店铺名称: {i['name']}, 店铺id: {i['id']}, "
                    f"店铺地址：{shop_address_entity_str['cityName']}{shop_address_entity_str['provinceName']}{shop_address_entity_str['countiesName']}"
                    f"\n当前实际数据:{shop_address_entity_str}"
                    f"\n{shop_address_entity_str['countiesName']}的实际code码为 {area_name}"
                    f"\n更改后的数据： {new_shop_address_entity_str}"
                )
                print("*" * 100)

        print(num)


AddressDetection().get_error_shop()
