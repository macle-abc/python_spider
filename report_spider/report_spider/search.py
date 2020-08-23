import concurrent.futures
from multiprocessing import cpu_count
from os import path

file_name = path.abspath(path.dirname(__file__)) + "\\常见术语.txt"
with open(file_name, 'r', encoding='utf-8') as f:
    all_terms = f.readlines()
all_terms = list({item.strip() for item in all_terms if item.strip()})


def is_contain(terms: list, info: str) -> bool:
    """
    检查info中是否包含常见术语以判断是否需要爬取
    :param terms: 常见术语
    :param info:文章内容
    :return:是否含有常见术语
    """
    for term in terms:
        if info.find(term) != -1:
            return True
    else:
        return False


def get_terms() -> list:
    """
    将所有的常见术语根据cpu数目尽可能均等划分
    :return: 划分后的常见术语,用于并发判断是否包含该常见术语
    """
    result = []
    cpu_number = cpu_count()
    terms_count = len(all_terms)
    each = terms_count // cpu_number
    for i in range(cpu_number):
        result.append(all_terms[i * each: (i + 1) * each])
    return result


def main(info):
    terms = get_terms()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        if True in executor.map(is_contain, terms, [info for item in range(len(terms))]):
            return True
        else:
            return False


if __name__ == '__main__':
    print(main("公钥"))
