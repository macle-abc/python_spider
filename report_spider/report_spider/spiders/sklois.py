# -*- coding: utf-8 -*-
import scrapy

from urllib import parse
import datetime
import re

from report_spider.items import SKLOISSpiderItem
from report_spider import search


class SkloisSpider(scrapy.Spider):
    name = 'sklois'
    allowed_domains = ['sklois.iie.cas.cn/tzgg/tzgg_16520/index.html']
    start_urls = ['http://sklois.iie.cas.cn/tzgg/tzgg_16520/index.html']

    def parse(self, response):
        trs = response.xpath('//table[@class="gailan_bg"]//table//table//tr')
        for tr in trs:
            detail_title = tr.xpath('//a[@class="hh14"]/@title').extract_first()
            release_time = tr.xpath('//td[@class="time"]/text()').extract_first()
            detail_link = tr.xpath('//a[@class="hh14"]/@href').extract_first()
            if detail_title.find("学术报告") == -1:
                continue
            release_time = datetime.datetime.strptime(release_time, "%Y-%m-%d").date()
            detail_link = parse.urljoin(response.url, detail_link)
            yield scrapy.Request(detail_link, callback=self.parse_detail, meta={
                                "release_time": release_time,
                                "detail_link": detail_link,
                            }, dont_filter=True)
        next_url = response.xpath('//a[text()="下一页"]/@href').extract_first()
        if next_url:
            next_url = parse.urljoin(response.url, next_url)
            yield scrapy.Request(next_url, callback=self.parse, dont_filter=True)

    def parse_detail(self, response):
        article = "".join([item for item in response.xpath('//table[@class="gailan_bg"]//*/text()').extract() if item.strip()])
        if not search.main(article):
            return None
        meta_infos = response.css(".MsoNormal")
        title_re = r"题目(:|：)\s*(?P<title>.*)"
        speaker_re = r"报告人(:|：)\s*(?P<speaker>.*)"
        holding_time_re = r"时间(:|：)\s*(?P<year>\d+)年(?P<month>\d+)月(?P<day>\d+)日.*(?P<time>\d+:\d+).*"
        place_re = r"地点(:|：)\s*(?P<place>.*)"
        university = "中国科学院"
        item_dict = {
            "release_time": response.meta['release_time'],
            "detail_link": response.meta['detail_link'],
        }
        for meta_info in meta_infos:
            meta_info = meta_info.css("font::text").extract_first()
            if meta_info:
                meta_info = meta_info.replace('\xa0', ' ')
                title = re.search(title_re, meta_info)
                if title:
                    item_dict['title'] = title.group('title')
                speaker = re.search(speaker_re, meta_info)
                if speaker:
                    item_dict['speaker'] = speaker.group('speaker')
                holding_time = re.search(holding_time_re, meta_info)
                if holding_time:
                    holding_time = holding_time.group('year') + holding_time.group('month') + holding_time.group('day') + holding_time.group('time')
                    holding_time = datetime.datetime.strptime(holding_time, '%Y%m%d%H:%M')
                    item_dict['holding_time'] = holding_time
                place = re.search(place_re, meta_info)
                if place:
                    item_dict['place'] = place.group('place')
        item_dict['university'] = university
        item = SKLOISSpiderItem()
        for key, value in item_dict.items():
            item[key] = value
        yield item

