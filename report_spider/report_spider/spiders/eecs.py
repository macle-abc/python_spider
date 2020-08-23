# -*- coding: utf-8 -*-
import scrapy

from report_spider.items import EECSSpiderItem
from report_spider import search

from urllib import parse
import datetime
import re


class EecsSpider(scrapy.Spider):
    name = 'eecs'
    allowed_domains = ['eecs.pku.edu.cn/xygk1/jzxx1.htm']
    start_urls = ['http://eecs.pku.edu.cn/xygk1/jzxx1.htm']

    def parse(self, response):
        """
        解析当前response中的报告信息，解析完成后将报告信息的详情页留给parse_detail继续解析
        :param response: 请求的响应
        :return: 下一个的url请求
        """
        detail_info_xpath = response.xpath('//ul[@class="ggtzM"]//li')
        for detail_info in detail_info_xpath:
            detail_title = detail_info.css("a::attr(title)").extract_first()
            if not detail_title or (detail_title.find("学术报告") == -1 and detail_title.find("学术讲座") == -1):
                continue
            detail_link = detail_info.css("a::attr(href)").extract_first()
            detail_link = parse.urljoin(EecsSpider.start_urls[0], detail_link)
            release_time = detail_info.css("em::text").extract_first()
            release_time = datetime.datetime.strptime(release_time, "%Y-%m-%d").date()
            yield scrapy.Request(detail_link, callback=self.parse_detail, dont_filter=True, meta={
                "release_time": release_time,
                "detail_link": detail_link,
            })
        # 获取下一页的url
        next_url = response.css(".p_next a::attr(href)").extract_first()
        if next_url:
            next_url = parse.urljoin(response.url, next_url)
            # 将详情页的url丢给parse_detail去完成解析
            yield scrapy.Request(next_url, callback=self.parse, dont_filter=True)

    def parse_detail(self, response):
        """
        解析每一个具体的报告信息
        :param response: 请求的响应
        :return: Item
        """
        meta = response.css(".v_news_content ::text").extract()
        article = "".join([item.strip() for item in meta if item.strip()])
        # 根据常见术语判断是否需要记录该报告
        if not search.main(article):
            return None
        detail_link = response.meta['detail_link']
        release_time = response.meta['release_time']

        content = ""
        for item in meta:
            content += item
        if not content:
            return None
        if re.match(r'(\r\n){2,}', content):
            return None
        content = content.split('\r\n')
        content = [item.strip() for item in content if item and item.strip()]
        holding_time_and_place_re = r"(时间：\s*(?P<month_1>\d+)月(?P<day_1>\d+)日.*(?P<time_1>\d+:\d+)—\d+:\d+ (" \
                                    r"?P<place_1>.*))|" \
                                    r"((?P<year_2>\d+)年(?P<month_2>\d+)月(?P<day_2>\d+)日.*(?P<time_2>\d+:\d+).*，(" \
                                    r"?P<place_2>.*)) "
        title_re = r"(题目|主题|报告题目|报告主题|演讲题目)：(\s*)(?P<title>.*)"
        holding_time_re = r"((时间|讲座时间)：(\s*)(?P<year_1>\d+)年(?P<month_1>\d+)月(?P<day_1>\d+)日.*(?P<time_1>\d+:\d+).*)|" \
                          r"((讲座时间|时间)：(\s*)(?P<month_2>\d+)月(?P<day_2>\d+)日.*(?P<time_2>\d+:\d+).*) "
        place_re = r"(地点|活动地点|讲座地点)：(\s*)(?P<place>.*)"
        speaker_re = r"(主讲人|报告人|演讲嘉宾)：(\s*)(?P<speaker>.*)"
        meta_result = {
            "detail_link": detail_link,
            "release_time": release_time,
        }
        for item in content:
            holding_time_and_place_result = re.search(holding_time_and_place_re, item)
            if holding_time_and_place_result:
                if holding_time_and_place_result.group('month_1'):
                    month = holding_time_and_place_result.group('month_1')
                    day = holding_time_and_place_result.group('day_1')
                    time = holding_time_and_place_result.group('time_1')
                    place = holding_time_and_place_result.group('place_1')
                    holding_time = f"{release_time.year}{month}{day}{time}"
                    holding_time = datetime.datetime.strptime(holding_time, "%Y%m%d%H:%M")
                    meta_result['holding_time'] = holding_time
                    meta_result['place'] = place
                elif holding_time_and_place_result.group('year_2'):
                    year = holding_time_and_place_result.group('year_2')
                    month = holding_time_and_place_result.group('month_2')
                    day = holding_time_and_place_result.group('day_2')
                    time = holding_time_and_place_result.group('time_2')
                    place = holding_time_and_place_result.group('place_2')
                    holding_time = f"{year}{month}{day}{time}"
                    holding_time = datetime.datetime.strptime(holding_time, "%Y%m%d%H:%M")
                    meta_result['holding_time'] = holding_time
                    meta_result['place'] = place
            else:
                holding_time_result = re.search(holding_time_re, item)
                if holding_time_result:
                    if holding_time_result.group('year_1'):
                        holding_time_re = r"((时间|讲座时间)：(\s*)(?P<year_1>\d+)年(?P<month_1>\d+)月(?P<day_1>\d+)日.*(?P<time_1>\d+:\d+).*)|" \
                                          r"((讲座时间|时间)：(\s*)(?P<month_2>\d+)月(?P<day_2>\d+)日.*(?P<time_2>\d+:\d+).*) "
                        year = holding_time_result.group('year_1')
                        month = holding_time_result.group('month_1')
                        day = holding_time_result.group('day_1')
                        time = holding_time_result.group('time_1')
                        holding_time = f"{year}{month}{day}{time}"
                        holding_time = datetime.datetime.strptime(holding_time, "%Y%m%d%H:%M")
                        meta_result['holding_time'] = holding_time
                    elif holding_time_result.group('month_2'):
                        month = holding_time_result.group('month_2')
                        day = holding_time_result.group('day_2')
                        time = holding_time_result.group('time_2')
                        holding_time = f"{release_time.year}{month}{day}{time}"
                        holding_time = datetime.datetime.strptime(holding_time, "%Y%m%d%H:%M")
                        meta_result['holding_time'] = holding_time
                place_result = re.search(place_re, item)
                if place_result:
                    meta_result['place'] = f"{place_result.group('place')}"
            title_result = re.search(title_re, item)
            if title_result:
                meta_result['title'] = f"{title_result.group('title')}"
            speaker_result = re.search(speaker_re, item)
            if speaker_result:
                meta_result['speaker'] = f"{speaker_result.group('speaker')}"
        meta_result['university'] = "北京大学"
        item = EECSSpiderItem()
        for key, value in meta_result.items():
            item[key] = value
        # 该item是items.py下的对象实例，将传输给pipelines.py中继续处理
        yield item
