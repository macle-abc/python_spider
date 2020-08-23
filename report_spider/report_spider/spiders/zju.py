import scrapy
from cssselect.parser import SelectorSyntaxError
from scrapy.selector.unified import Selector

from report_spider.items import ReportSpiderLoader, ReportSpiderItem
from report_spider import search

from urllib import parse
import re


class ZjuSpider(scrapy.Spider):
    name = "zju"
    allowed_domains = ['www.cs.zju.edu.cn/csen/xsjz/list.htm']
    start_urls = ['http://www.cs.zju.edu.cn/csen/xsjz/list.htm']

    def parse(self, response):
        detail_info = self.__try_find_element(response,
                                              '//li[@class="list_guild"]',
                                              '',
                                              r'')
        for detail in detail_info:
            detail_title = self.__try_find_element(detail,
                                                   'a/@title',
                                                   '',
                                                   r'')
            if not detail_title:
                print("Warring!详情页标题获取失败!")
            else:
                if len(detail_title) != 1:
                    raise ValueError("请修改规则以满足详情页标题精确匹配出一个结果!")
                if not self.__check_detail_title_valid(detail_title[0]):
                    continue
                else:
                    detail_link = self.__try_find_element(detail,
                                                          'a/@href',
                                                          '',
                                                          r'')
                    if not detail_link:
                        print("Warring!详情页链接获取失败!")
                        continue
                    else:
                        if len(detail_link) != 1:
                            raise ValueError("请修改规则以满足详情页链接精确匹配出一个结果!")
                        detail_link = parse.urljoin(response.url, detail_link.extract_first())
                        yield scrapy.Request(detail_link, self.parse_detail, dont_filter=True)
        next_url = self.__try_find_element(response,
                                           '//a[@class="next"]/@href',
                                           '',
                                           r'')
        if next_url:
            if len(next_url) != 1:
                raise ValueError("请修改规则以满足获取下一页链接精确匹配出一个结果!")
            next_url = parse.urljoin(response.url, next_url.extract_first())
            if next_url != 'javascript:void(0);':
                yield scrapy.Request(next_url, self.parse, dont_filter=True)

    def parse_detail(self, response):
        article = self.__try_find_element(response,
                                          '//div[@class="wp_articlecontent"]//text()',
                                          '',
                                          r'')
        article = article.extract()
        article = "".join([item.strip() for item in article if item.strip()])
        # if not search.main(article):
        #     return None
        item = ReportSpiderLoader(ReportSpiderItem(), response=response)
        self.__set_item_value(item, "title",
                              "Warring!标题获取失败!",
                              "请修改规则以满足标题精确匹配出一个结果!",
                              response,
                              '//div[@class="content_title"]/h2/text()',
                              '',
                              r'')
        self.__set_item_value(item, "speaker",
                              "Warring!报告人获取失败!",
                              "请修改规则以满足报告人精确匹配出一个结果!",
                              response,
                              '//div[@class="content_title"]/h2/text()',
                              '',
                              r'')
        self.__set_item_value(item, "holding_time",
                              "Warring!举行时间获取失败!",
                              "请修改规则以满足举行时间精确匹配出一个结果!",
                              response,
                              '//div[@class="content_title"]/h2/text()',
                              '',
                              r'')
        self.__set_item_value(item, "place",
                              "Warring!报告地点获取失败!",
                              "请修改规则以满足举办地点精确匹配出一个结果!",
                              response,
                              '//div[@class="content_title"]/h2/text()',
                              '',
                              r'')
        self.__set_item_value(item, "release_time",
                              "Warring!发布时间获取失败!",
                              "请修改规则以满足发布时间精确匹配出一个结果!",
                              response,
                              '//div[@class="content_title"]/h2/text()',
                              '',
                              r'')
        item.add_value("university", '浙江大学')
        item.add_value("detail_link", response.url)
        yield item.load_item()

    @staticmethod
    def __try_find_element(response, element_xpath, element_css, element_re_pattern, element_find_func=None) -> list:
        try:
            element = response.xpath(element_xpath)
        except ValueError as e:
            raise ValueError("非法的xpath表达式!")
        if not element:
            try:
                element = response.css(element_css)
            except SelectorSyntaxError as e:
                raise SelectorSyntaxError("非法的css选择器!")
            if not element:
                re_pattern = re.compile(element_re_pattern)
                element = re.search(re_pattern, response.text)
                if not element:
                    if element_find_func is None:
                        raise ValueError(f"xpath,css,正则表达式匹配失败!请修改配置文件中的匹配规则或实现自定义函数!")
                    elif not callable(element_find_func):
                        raise ValueError(f"element_find_func必须是一个可调用对象!")
                    element = element_find_func(response)
                    if not isinstance(element, list):
                        raise ValueError(f"{element_find_func.__name__}必须返回list类型!")
                    else:
                        return element
                else:
                    return [element.groupdict()]
            else:
                return element
        else:
            return element

    @staticmethod
    def __check_detail_title_valid(detail_title: Selector) -> bool:
        if not isinstance(detail_title, Selector):
            raise TypeError(f"detail_title必须是Selector类型")
        else:
            loc_title = detail_title.extract()
        # 自定义检验规格
        return True

    def __set_item_value(self, item, element_name, warring_message, exception_message, *args):
        element = self.__try_find_element(*args)
        if element:
            if len(element) != 1:
                raise ValueError(exception_message)
            else:
                item.add_value(element_name, element.extract_first())
        else:
            print(warring_message)
