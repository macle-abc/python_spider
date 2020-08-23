# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst

import datetime


class ReportSpiderLoader(ItemLoader):
    # 由于使用Loader去处理爬虫中parse_detail信息，会导致每一个信息比如标题都是一个list
    # eg: [标题内容], 故使用输出处理，只取第一个元素
    default_output_processor = TakeFirst()


class ReportSpiderItem(scrapy.Item):
    title = scrapy.Field()
    speaker = scrapy.Field()
    holding_time = scrapy.Field()
    place = scrapy.Field()
    university = scrapy.Field()
    detail_link = scrapy.Field()
    release_time = scrapy.Field()

    # 数据库插入语句
    def get_insert_sql(self):
        SQL = '''
           INSERT INTO "main"."REPORT"("title", "speaker", "holding_time", "release_time", "address", "university", "detail_link") VALUES (?, ?, ?, ?, ?, ?, ?)
           '''
        fields = ["title", "speaker", "holding_time", "release_time", "place", "university", "detail_link"]
        params = []
        for field in fields:
            if field in self._values:
                if field == "holding_time":
                    params.append(self._values[field].strftime("%Y-%m-%d %H:%M"))
                elif field == "release_time":
                    params.append(self._values[field].strftime("%Y-%m-%d"))
                else:
                    params.append(self._values[field])
            else:
                params.append(None)
        return SQL, params


def handle_holding_time(value):
    if len(value) != 1:
        return None
    try:
        value = datetime.datetime.strptime(value[0], '%Y%m%d%H:%M')
    except ValueError as e:
        print(type(e), e, "Error!")
        return None
    else:
        return value


def handle_place(value):
    if len(value) != 1:
        return None
    return value


class SCUTSpiderItem(ReportSpiderItem):
    place = scrapy.Field(
        input_processor=handle_place,
    )
    holding_time = scrapy.Field(
        input_processor=handle_holding_time,
    )
    pass


class EECSSpiderItem(ReportSpiderItem):
    pass


class IIISSpiderItem(ReportSpiderItem):
    pass


class SKLOISSpiderItem(ReportSpiderItem):
    pass
