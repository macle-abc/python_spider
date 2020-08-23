# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import sqlite3
from twisted.enterprise import adbapi
from sqlite3 import connect
import re


class ReportSpiderPipeline:
    """
    用于预处理爬取到的信息，过滤掉部分无用的字词
    """

    @staticmethod
    def handling_item_value(value: str, needed_replace_keyword: str):
        return re.sub(needed_replace_keyword, "", value)

    def process_item(self, item, spider):
        """
        处理由爬虫代码中yield中的item
        :param item: 爬虫代码中yield中的item
        :param spider: 未使用
        :return: item，用于给下一个pipeline继续处理
        """
        if "title" in item:
            item['title'] = self.handling_item_value(item['title'], r"报告人|报告摘要")
        if "speaker" in item:
            item['speaker'] = self.handling_item_value(item['speaker'], r"主持人|教授|副教授|博士")
        if "place" in item:
            item['place'] = self.handling_item_value(item['place'], r"报告摘要|欢迎广大师生踊跃参加.*")
        return item


class Sqlite3TwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        """
        创建数据库连接池
        :param settings: settings.py
        :return: 连接池对象
        """
        dbparms = dict(
            database=settings["DBNAME"],
            check_same_thread=False,
        )
        dbpool = adbapi.ConnectionPool("sqlite3", **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 异步执行插入
        query = self.dbpool.runInteraction(self.do_insert, item)
        # 异步处理错误信息
        query.addErrback(self.handle_error, item, spider)
        return item

    def handle_error(self, failure, item, spider):
        """
        数据库操作错误信息处理函数
        :param failure: 具体错误
        :param item: item
        :param spider: 未使用
        :return: None
        """
        if failure:
            print(failure)

    def do_insert(self, cursor, item):
        """
        执行数据库记录插入操作
        :param cursor: 连接池自动创建的数据库操作游标
        :param item: item
        :return: None
        """
        # 根据items.py中基类定义的get_insert_sql获取插入语句，及其参数
        insert_sql, params = item.get_insert_sql()
        try:
            # 执行插入
            cursor.execute(insert_sql, params)
        except Exception as e:
            print(type(e), e, "Error!")
