#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mysql Control Module

This module provides mysql control functionality.
"""

"""
MySQL数据库操作控制模块
提供数据库连接、查询、更新等功能，支持测试用例中的数据库断言

主要功能：
- 数据库连接管理（自动连接和断开）
- SQL查询操作（单条/多条查询）
- SQL执行操作（增删改操作）
- 前置SQL数据处理
- 断言SQL数据处理
- 数据类型转换（Decimal、DateTime等）

@Time   : 2021/11/26 18:27
@Author : txl
@Update : 2023-12-20 优化注释和异常处理
"""
import ast
import datetime
import decimal
from typing import Dict, List, Text, Union
from warnings import filterwarnings

import pymysql

from utils import config
from utils.logging_tool.log_control import ERROR
from utils.other_tools.exceptions import DataAcquisitionFailed, ValueTypeError
from utils.read_files_tools.regular_control import cache_regular, sql_regular

filterwarnings("ignore", category=pymysql.Warning)


class MysqlDB:
    """
    MySQL数据库操作基础类

    提供数据库连接、查询、执行等基础功能。
    只有在配置文件中开启数据库开关时才会建立连接。

    特性：
    - 自动连接管理
    - 字典格式返回查询结果
    - 事务支持
    - 异常处理和日志记录
    """

    if config.mysql_db.switch:

        def __init__(self) -> None:
            """
            初始化数据库连接

            根据配置文件中的数据库配置建立连接，使用字典游标返回查询结果。

            Raises:
                AttributeError: 当数据库配置错误或连接失败时抛出
            """
            try:
                # 建立数据库连接
                self.conn = pymysql.connect(
                    host=config.mysql_db.host,
                    user=config.mysql_db.user,
                    password=config.mysql_db.password,
                    port=config.mysql_db.port,
                )

                # 使用字典游标，查询结果以字典形式返回，便于数据处理
                self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
            except AttributeError as error:
                ERROR.logger.error("数据库连接失败，失败原因 %s", error)
                raise

        def __del__(self):
            try:
                # 关闭游标
                self.cur.close()
                # 关闭连接
                self.conn.close()
            except AttributeError as error:
                ERROR.logger.error("数据库连接失败，失败原因 %s", error)

        def query(self, sql, state="all"):
            """
            查询
            :param sql:
            :param state:  all 是默认查询全部
            :return:
            """
            try:
                self.cur.execute(sql)

                if state == "all":
                    # 查询全部
                    data = self.cur.fetchall()
                else:
                    # 查询单条
                    data = self.cur.fetchone()
                return data
            except AttributeError as error_data:
                ERROR.logger.error("数据库连接失败，失败原因 %s", error_data)
                raise

        def execute(self, sql: Text):
            """
            更新 、 删除、 新增
            :param sql:
            :return:
            """
            try:
                # 使用 execute 操作 sql
                rows = self.cur.execute(sql)
                # 提交事务
                self.conn.commit()
                return rows
            except AttributeError as error:
                ERROR.logger.error("数据库连接失败，失败原因 %s", error)
                # 如果事务异常，则回滚数据
                self.conn.rollback()
                raise

        @classmethod
        def sql_data_handler(cls, query_data, data):
            """
            处理部分类型sql查询出来的数据格式
            @param query_data: 查询出来的sql数据
            @param data: 数据池
            @return:
            """
            # 将sql 返回的所有内容全部放入对象中
            for key, value in query_data.items():
                if isinstance(value, decimal.Decimal):
                    data[key] = float(value)
                elif isinstance(value, datetime.datetime):
                    data[key] = str(value)
                else:
                    data[key] = value
            return data


class SetUpMySQL(MysqlDB):
    """处理前置sql"""

    def setup_sql_data(self, sql: Union[List, None]) -> Dict:
        """
        处理前置请求sql
        :param sql:
        :return:
        """
        sql = ast.literal_eval(cache_regular(str(sql)))
        try:
            data = {}
            if sql is not None:
                for i in sql:
                    # 判断断言类型为查询类型的时候，
                    if i[0:6].upper() == "SELECT":
                        sql_date = self.query(sql=i)[0]
                        for key, value in sql_date.items():
                            data[key] = value
                    else:
                        self.execute(sql=i)
            return data
        except IndexError as exc:
            raise DataAcquisitionFailed("sql 数据查询失败，请检查setup_sql语句是否正确") from exc


class AssertExecution(MysqlDB):
    """处理断言sql数据"""

    def assert_execution(self, sql: list, resp) -> dict:
        """
         执行 sql, 负责处理 yaml 文件中的断言需要执行多条 sql 的场景，最终会将所有数据以对象形式返回
        :param resp: 接口响应数据
        :param sql: sql
        :return:
        """
        try:
            if isinstance(sql, list):

                data = {}
                _sql_type = ["UPDATE", "update", "DELETE", "delete", "INSERT", "insert"]
                if any(i in sql for i in _sql_type) is False:
                    for i in sql:
                        # 判断sql中是否有正则，如果有则通过jsonpath提取相关的数据
                        sql = sql_regular(i, resp)
                        if sql is not None:
                            # for 循环逐条处理断言 sql
                            query_data = self.query(sql)[0]
                            data = self.sql_data_handler(query_data, data)
                        else:
                            raise DataAcquisitionFailed(f"该条sql未查询出任何数据, {sql}")
                else:
                    raise DataAcquisitionFailed("断言的 sql 必须是查询的 sql")
            else:
                raise ValueTypeError("sql数据类型不正确，接受的是list")
            return data
        except Exception as error_data:
            ERROR.logger.error("数据库连接失败，失败原因 %s", error_data)
            raise error_data


if __name__ == "__main__":
    a = MysqlDB()
    b = a.query(sql="select * from `test_obp_configure`.lottery_prize where activity_id = 3")
    print(b)
