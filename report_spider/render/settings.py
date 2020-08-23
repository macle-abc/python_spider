from os import path

# render目录
RENDER_PATH = path.abspath(path.dirname(__file__))
# 项目目录
PROJECT_PATH = path.dirname(RENDER_PATH)
# 爬虫目录
SPIDERS_PATH = PROJECT_PATH + r"/report_spider/spiders/"
# ui目录
UI_PATH = PROJECT_PATH + r"/ui/"
# userinterface.py路径
USERINTERFACE_PATH = UI_PATH + r"UserInterface.py"
# 配置文件路径
CONF_JSON_PATH = RENDER_PATH + r"/confs/"
# 模板文件路径
TEMPLATE_PATH = RENDER_PATH + r"/template/"
# json模板文件
GENERICS_JSON_PATH = TEMPLATE_PATH + "generics.json"
# 爬虫模板文件
GENERICS_SPIDER_PATH = TEMPLATE_PATH + "generics.txt"


def get_settings(key: str) -> str:
    """
    从settings.py中获取key的值
    :param key: setting.py中全局变量名
    :return: 对应的value值
    """
    if isinstance(key, str):
        try:
            return globals()[key]
        except KeyError as e:
            print("请检查key!")
            return None
    else:
        return None
