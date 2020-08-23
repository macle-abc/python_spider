# -*- coding: utf-8 -*-
import scrapy

from urllib import parse
import re
import datetime

from report_spider.items import IIISSpiderItem
from report_spider import search


class IiisSpider(scrapy.Spider):
    name = 'iiis'
    allowed_domains = ['iiis.tsinghua.edu.cn/seminars']
    start_urls = ['https://iiis.tsinghua.edu.cn/seminars/']

    def parse(self, response):
        detail_infos = response.xpath('//div[@class="table-responsive"]/table/tbody//tr')
        for detail_info in detail_infos:
            detail_link = detail_info.xpath('td[1]/a/@href').extract_first().strip()
            item_dict = dict(
                detail_link=parse.urljoin(response.url, detail_link),
                title=detail_info.xpath('td[1]/a/text()').extract(),
                holding_time=detail_info.xpath('td[3]/text()').extract_first(),
                place=detail_info.xpath('td[4]/text()').extract_first(),
                university="清华大学",
            )
            temp = {}
            for key, value in item_dict.items():
                if value and key != 'title':
                    temp[key] = value.strip()
                elif value and key == "title":
                    temp[key] = value
            speaker = detail_info.xpath('td[2]/text()[1]').extract_first()
            if speaker and speaker.strip():
                temp['speaker'] = speaker.strip()
            else:
                speaker = detail_info.xpath("td[2]/a/text()").extract_first()
                if speaker and speaker.strip():
                    temp['speaker'] = speaker.strip()
            yield scrapy.Request(item_dict['detail_link'], callback=self.parse_detail, meta={
                "item_dict": temp,
            }, dont_filter=True)
        next_url = response.css("#page-next::attr(value)").extract_first()
        next_url = parse.urljoin(response.url, next_url)
        if next_url != response.url:
            yield scrapy.Request(next_url, callback=self.parse, dont_filter=True)

    def parse_detail(self, response):
        article = response.css('.contentss ::text').extract()
        article = "".join([item.strip() for item in article if item.strip()])
        if not search.main(article):
            return None
        item_dict = response.meta['item_dict']
        item_dict['title'] = "".join(item_dict['title'])
        item = IIISSpiderItem()
        for key, value in item_dict.items():
            if key == "holding_time":
                time = re.search(r"(\d+-){2}\d+ \d+:\d+", value)
                if time:
                    time = time.group(0)
                    holding_time = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M")
                    item['holding_time'] = holding_time
            else:
                item[key] = value
        yield item
