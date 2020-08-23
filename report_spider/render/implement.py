from render.settings import get_settings

import json
import re
from os import path


class RenderSpider:
    """
    根据confs下面的配置文件生成爬虫代码
    """

    def __init__(self, name: str):
        """
        :param name: 爬虫名
        """
        if not isinstance(name, str):
            raise TypeError("name应为str类型!")
        self.__name = name
        self.__file_name = get_settings("CONF_JSON_PATH") + name + ".json"
        try:
            with open(self.__file_name, 'r', encoding='utf-8') as f:
                self.__json = json.load(f)
        except FileNotFoundError as e:
            raise ValueError(f"{self.__file_name}不存在!请检查name是否合法!")
        except UnicodeDecodeError as e:
            raise ValueError(f"{self.__file_name}应为utf-8编码!请检查编码格式!")

    @staticmethod
    def __replace(context: dict, content: str) -> str:
        for key, value in context.items():
            pattern = "\{% " + f"{key}" + " %\}"
            content = re.sub(pattern, value, content)
        return content

    def render_spider(self):
        """
        生成爬虫代码
        :return: None
        """

        def render_json(json_result: dict, output: dict, prefix: str = ""):
            """
            将json_result中的每一个key添加前缀
            '''
            eg:  "detail_meta_rule": {
                 "xpath": "//li[@class=\"list_guild\"]",
                 }
                 将保存在output中为"detail_meta_rule.xpath": "//li[@class=\"list_guild\"]"
            '''
            :param json_result: 需要增加前缀的json结果
            :param output: 保存增加完前缀的json结果
            :param prefix: 每一个key需要添加的前缀
            :return: None
            """
            for key, value in json_result.items():
                if isinstance(value, dict):
                    render_json(value, output, f"{prefix}{key}.")
                elif isinstance(value, str):
                    output[f"{prefix}{key}"] = value

        def save_spider_file():
            """
            保存生成后的爬虫文件于settings.py中的SPIDERS_PATH目录下
            :return: None
            """
            spiders_path = get_settings("SPIDERS_PATH")
            file_path = spiders_path + f"{self.__name}.py"
            if not path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"请在{get_settings('USERINTERFACE_PATH')}文件中导入新的爬虫代码!")
            else:
                message = f"{file_path}文件已存在!是否覆盖?(Y or N)"
                choice = input(message)
                if choice in 'yY':
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"保存成功!请在{get_settings('USERINTERFACE_PATH')}文件中导入新的爬虫代码!")
                else:
                    print("放弃操作!")

        with open(get_settings("GENERICS_SPIDER_PATH"), 'r', encoding='utf-8') as f:
            generics_content = f.read()
        context = {
            "class_name": self.__name.title() + "Spider",
        }
        render_json(self.__json, context)
        content = self.__replace(context, generics_content)
        save_spider_file()


class ImplementSpider:
    """
    根据用户输出生成爬虫的配置文件，RenderSpider将根据该配置文件生成爬虫代码
    """
    def __init__(self):
        while True:
            self.__name = self.__get_info("爬虫名:")
            temp_file_name = get_settings("SPIDERS_PATH") + self.__name + ".json"
            if path.exists(temp_file_name):
                print("该名称已存在!请重新输入!")
            else:
                break
        self.__start_url = self.__get_info("起始页的url:")
        self.__university = self.__get_info("该爬虫爬取的单位名称:")

    @staticmethod
    def __get_info(tips: str = "输入提示") -> str:
        while True:
            value = input(tips)
            if value:
                return value
            else:
                print("请重新输入有效的内容!")

    def render_json(self):
        with open(get_settings("GENERICS_JSON_PATH"), "r", encoding='utf-8') as f:
            result = json.load(f)
        result['start_url'] = self.__start_url
        result['name'] = self.__name
        result['detail']['university'] = self.__university
        file_name = get_settings("CONF_JSON_PATH") + self.__name + ".json"
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"请填写:{file_name}中的爬取规格:")


def main():
    # 第一步:生成爬虫配置文件
    # implement_spider = ImplementSpider()
    # implement_spider.render_json()
    # 第二步:第一步中输入的爬虫名
    # render = RenderSpider('zju')
    # render.render_spider()
    pass


if __name__ == '__main__':
    main()
