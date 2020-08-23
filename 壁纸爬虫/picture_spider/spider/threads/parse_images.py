from spider.spider_import import *


def parse_images_url_thread(page_queue: Queue, urls_queue: Queue):
    """
    解析图片url线程，用于从page_queue中获取网页详情页html结构信息
    并从中提取出图片的url将其放入urls_queue中
    :param page_queue: 网页详情页的响应报文所组成的安全队列
    :param urls_queue: 网页中图片的data-src属性所组成的url安全队列
    :return: None
    """
    while True:
        page = page_queue.get()
        if page is None:
            break
        if page.status_code != 200:
            print(f"详情页获取失败!状态码为:{page.status_code}")
        else:
            html = BeautifulSoup(page.text, 'html5lib')
            # 使用css选择器获取div
            divs = html.select(".thumb-container-big")
            for div in divs:
                # 使用css选择器获取img
                image = div.select_one(".boxgrid img")
                if not image:
                    print("图片获取失败!")
                else:
                    # 判断image是否存在data-src属性
                    if 'data-src' in image.attrs and image.attrs['data-src']:
                        print(f"图片url获取成功:{image.attrs['data-src']}")
                        urls_queue.put(image.attrs['data-src'])
                    else:
                        print(f"图片属性可能被修改!{image.attrs}")

    urls_queue.put(None)


if __name__ == '__main__':
    page_queue = Queue()
    urls_queue = Queue()
    page_queue.put(requests.get("https://wall.alphacoders.com/highest_rated.php", headers=get_headers()))
    page_queue.put(None)
    parse_images_url_thread(page_queue, urls_queue)
    while True:
        url = urls_queue.get()
        if url is None:
            break
        else:
            print(url)
