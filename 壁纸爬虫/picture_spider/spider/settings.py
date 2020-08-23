from os import path

BASE_URL = "https://wall.alphacoders.com/highest_rated.php"
API_URL = "https://api.alphacoders.com/content/get-download-link"
IMAGES_DIR = path.abspath(path.dirname(path.dirname(__file__))) + "/images/"


def get_setting(key: str):
    """
    从当前文件中获取key所对应的value值
    :param key: settings.py中全局变量名
    :return: key变量的值
    """
    if not isinstance(key, str):
        raise TypeError("key应该为str类型")
    if key in globals():
        return globals()[key]
    else:
        raise ValueError(f"key只能从{globals().keys()}中选取")


if __name__ == '__main__':
    try:
        print(get_setting(2))
    except TypeError as e:
        print(e)
    try:
        print(get_setting('test'))
    except ValueError as e:
        print(e)
