# -*- coding: utf-8 -*-
import scrapy

from urllib import parse
import datetime
import re

from report_spider.items import SCUTSpiderItem, ReportSpiderLoader
from report_spider import search


class ScutSseSpider(scrapy.Spider):
    name = 'scut_sse'
    allowed_domains = ['www2.scut.edu.cn/sse/xshd/list.htm']
    start_urls = ['http://www2.scut.edu.cn/sse/xshd/list.htm']

    def parse(self, response):
        detail_info_css = response.css('#wp_news_w67 > ul > li')
        for detail_info in detail_info_css:
            release_time = detail_info.css(".news_meta::text").extract_first()
            if release_time:
                try:
                    release_time = datetime.datetime.strptime(release_time, '%Y-%m-%d').date()
                except ValueError as e:
                    print(type(e), e, "Error!")
                else:
                    apart_days = datetime.datetime.now().date() - release_time
                    # if apart_days.days > (365 + 180):
                    #     continue
            detail_title = detail_info.css(".news_title a::attr(title)").extract_first()
            if detail_title and not detail_title.endswith("报告会的通知"):
                continue
            detail_link = detail_info.css(".news_title a::attr(href)").extract_first()
            detail_link = parse.urljoin(ScutSseSpider.start_urls[0], detail_link)
            yield scrapy.Request(detail_link, callback=self.parse_detail,
                                 dont_filter=True,
                                 meta={
                                     "release_time": release_time,
                                     "detail_link": detail_link,
                                 },
                                 )
        next_url = response.css(".next::attr(href)").extract_first()
        if next_url and next_url != "javascript:void(0);" and next_url != "null":
            next_url = parse.urljoin(ScutSseSpider.start_urls[0], next_url)
            if next_url.startswith("http://www2.scut.edu.cn/sse/xshd/list"):
                yield scrapy.Request(next_url, callback=self.parse, dont_filter=True)

    def parse_detail(self, response):
        article = response.css(".arti_cont ::text").extract()
        article = "".join([item.strip() for item in article if item.strip()])
        if not search.main(article):
            return None
        detail_link = response.meta['detail_link']
        release_time = response.meta['release_time']
        meta = response.xpath('//head//meta[@name="description"]/@content').extract_first()
        if meta:
            meta_re = dict(
                title_re=r"报告题目(：|:)(?P<title>\w+)",
                speaker_re=r"(报 告 人|报告人)(：|:)*?(?P<speaker>\w+)(主持人)?",
                holding_time_re=r"报告时间(：|:)(?P<year>\d+)年(?P<month>\d+)月(?P<day>\d+)日.*?(?P<time>\d+(:|：)\d+)",
                place_re=r"报告地点(：|:)(?P<place>\w+)(欢迎广大师生踊跃参加)?",
            )
            loader = ReportSpiderLoader(item=SCUTSpiderItem(), response=response)
            loader.add_value("university", "华南理工大学")
            loader.add_value("detail_link", detail_link)
            loader.add_value("release_time", release_time)
            for key, value in meta_re.items():
                re_result = re.search(value, meta)
                if re_result:
                    if key == "holding_time_re":
                        loader.add_value(key[:len(key) - 3], "".join(re_result.groupdict().values()).replace('：', ':'))
                    elif key == "speaker_re":
                        loader.add_value(key[:len(key) - 3], "".join(re_result.groupdict().values()).replace('报告时间', ""))
                    else:
                        loader.add_value(key[:len(key) - 3], "".join(re_result.groupdict().values()))
            item = loader.load_item()
            yield item

