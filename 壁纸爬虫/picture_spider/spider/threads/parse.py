from spider.spider_import import *


def parse_thread(page_queue: Queue, page_start_number: int = 1, page_count: int = 10):
    """
    解析每一个响应报文中下一页的url，并将当前响应报文传递给page_queue中
    供解析线程解析
    :param page_start_number: 网页详情页起始数
    :param page_count: 网页详情页总数
    :param page_queue: 网页详情页的响应报文所组成的安全队列
    :return: None
    """
    base_url = get_setting("BASE_URL")
    '''
    请求参数格式为
    PARAMS = {
    "lang": "Chinese",
    "pagex": 1,
    }
    '''
    pagex = page_start_number
    while pagex <= page_count + page_start_number - 1:
        print(f"正在获取第{pagex}页响应")
        # 构造请求参数
        response = requests.get(base_url, params={
            "lang": "Chinese",
            "pagex": pagex
        }, headers=get_headers())
        if response.status_code != 200:
            print(f"网页详情页请求失败!状态码为:{response.status_code}")
        else:
            page_queue.put(response)
        pagex += 1
    page_queue.put(None)


if __name__ == '__main__':
    page_queue = Queue()
    parse_thread(page_queue)
    while True:
        page = page_queue.get()
        if page is None:
            break
        else:
            print(page)
