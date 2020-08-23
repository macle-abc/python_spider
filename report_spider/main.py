from scrapy.cmdline import execute

import sys
from os import path

sys.path.append(path.abspath(path.dirname(__file__)))

from ui.UserInterface import UserInterface

if __name__ == '__main__':
    # 用于用户交互操作
    user_interface = UserInterface()
    user_interface.show_ui()
    # 用于测试单个爬虫文件list中最后的一个参数是爬虫名
    # eg: sklois是测试report_spider/spiders/sklois.py中的爬虫代码
    # execute(["scrapy", "crawl", "sklois"])
