from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

import sqlite3

import sys

from report_spider.settings import DBNAME
from report_spider import create_db
# 爬虫文件
from report_spider.spiders import eecs, iiis, scut_sse, sklois


def start_spider():
    create_db.main()
    configure_logging()
    runner = CrawlerRunner(settings=get_project_settings())
    # 爬虫对象
    runner.crawl(eecs.EecsSpider)
    runner.crawl(iiis.IiisSpider)
    runner.crawl(scut_sse.ScutSseSpider)
    runner.crawl(sklois.SkloisSpider)
    d = runner.join()
    d.addBoth(lambda _: reactor.stop())
    reactor.run()
    print("爬取完成!")


class Function:
    """
    ui的功能实现
    """

    def __init__(self):
        self.conn = sqlite3.connect(DBNAME)
        self.cursor = self.conn.cursor()

    def select(self, sql: str, params: list):
        if params:
            return self.cursor.execute(sql, params).fetchall()
        else:
            return self.cursor.execute(sql).fetchall()

    def get_reports_last_month(self):
        sql = '''
        SELECT
            *, 
            REPORT.*
        FROM
            REPORT
        WHERE
            REPORT.holding_time BETWEEN datetime('now', '-30 day') AND datetime('now')
        '''
        params = None
        return self.select(sql, params)

    def get_reports(self):
        sql = '''
        SELECT * FROM "REPORT"
        '''
        params = None
        return self.select(sql, params)

    def get_reports_by_release_time(self):
        sql = '''
        SELECT
            REPORT.*
        FROM
            REPORT
        ORDER BY
            REPORT.release_time DESC
        '''
        params = None
        return self.select(sql, params)

    def get_reports_by_holding_time(self):
        sql = '''
        SELECT
            REPORT.*
        FROM
            REPORT
        ORDER BY
            REPORT.holding_time DESC
        '''
        params = None
        return self.select(sql, params)

    def __del__(self):
        self.conn.close()


class UserInterface:
    def __init__(self):
        self.__function = Function()
        self.__is_spidered = False
        self.__function_dict = {
            1: self.__spider,
            2: self.__show_reports,
            3: self.__show_reports_last_month,
            4: self.__show_reports_by_holding_time,
            5: self.__show_reports_by_release_time,
            6: sys.exit,
        }

    @staticmethod
    def __show(query_set: list):
        """
        打印查询后的结果信息
        :param query_set: 根据数据库操作返回的查询集
        :return: None
        """
        def my_print(value: str, space_count: int, sep: str = '|', end: str = '|'):
            """
            用于打印中英文字符串，避免因为中文导致的对齐问题
            :param value: 需要打印的字符串
            :param space_count: 空格数目
            :param sep: 划分符号
            :param end: 完成符号
            :return: None
            """
            item_len = 0
            for item in value:
                if ord(item) in range(255):
                    item_len += 1
                else:
                    item_len += 2
            if space_count > item_len:
                print(' ' * ((space_count - item_len) // 2), end='')
                print(value, end='')
                print(' ' * ((space_count - item_len) - ((space_count - item_len) // 2)), sep=sep, end=end)
            else:
                print("ERROR!!" * 5, "请修改格式!!")

        if query_set:
            print('|', end='')
            for value, space_count in zip(["详情链接", "标题", "报告人", "举办时间", "发布时间", "地点", "学校"],
                                          [70, 200, 100, 50, 50, 120, 35]):
                my_print(value, space_count)
            print()
            for each in query_set:
                print('|', end='')
                for value, space_count in zip([item if item else "空" for item in each],
                                              [70, 200, 100, 50, 50, 120, 35]):
                    my_print(value, space_count)
                print()
                print()
        else:
            print("没有数据")

    def __spider(self):
        if self.__is_spidered:
            print("已经爬取完成!请勿重新爬取!如需重新爬取，请重启程序!")
        else:
            self.__is_spidered = True
            start_spider()

    def __show_reports(self):
        self.__show(self.__function.get_reports())

    def __show_reports_last_month(self):
        self.__show(self.__function.get_reports_last_month())

    def __show_reports_by_holding_time(self):
        self.__show(self.__function.get_reports_by_holding_time())

    def __show_reports_by_release_time(self):
        self.__show(self.__function.get_reports_by_release_time())

    @staticmethod
    def __show_function():
        functions = [
            "1.开始爬取报告信息",
            "2.显示报告信息",
            "3.显示最近一个月的报告信息",
            "4.以举行时间排序报告信息并显示",
            "5.以发布时间排序报告信息并显示",
            "6.退出",
            "请输入您的选择(1-6)",
        ]
        print(*functions, sep='\n')

    def show_ui(self):
        while True:
            self.__show_function()
            while True:
                try:
                    choose = int(input())
                except ValueError as e:
                    print("非法操作!请重新输入!")
                else:
                    if choose in range(1, 7):
                        break
                    else:
                        print("非法操作!请重新输入!")
            self.__function_dict[choose]()


if __name__ == '__main__':
    user_interface = UserInterface()
