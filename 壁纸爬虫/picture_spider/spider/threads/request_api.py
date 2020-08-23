from spider.spider_import import *


def request_api_thread(urls_queue: Queue, images_queue: Queue, event: Event):
    """
    api请求线程，用于向api发送请求，获取图片详情url链接添加到images_queue中
    :param event: 允许主线程开启下载线程
    :param urls_queue: 网页中图片的data-src属性所组成的url安全队列
    :param images_queue: 图片url安全队列
    :return: None
    """
    api = get_setting("API_URL")
    while True:
        url = urls_queue.get()
        if url is None:
            break
        # url like "https://images7.alphacoders.com/422/thumb-350-422813.png"
        # url 正则表达式解析
        url_pattern = re.compile(
            r"http(s|S)://(?P<image_server>.*)\..*\.com/\d+/thumb-\d+-(?P<content_id>\d+)\.(?P<file_type>.*)")
        result = re.match(url_pattern, url)
        if not result:
            print(f"存在丢失数据{url}")
        else:
            # 拟造api接口的data数据
            '''
            例如
            content_id: 171916
            content_type: wallpaper
            file_type: jpg
            image_server: images4
            '''
            data = result.groupdict()
            data['content_type'] = 'wallpaper'
            image = requests.post(api, data=data, headers=get_headers())
            if image.status_code != 200:
                print(f"图片解析失败!{data}")
            else:
                # json反序列化
                image_result = json.loads(image.text)
                # 有效性判断
                if 'status' in image_result and image_result['status'] == "success":
                    if 'link' in image_result and image_result['link']:
                        # 合法的图片url放入队列中
                        images_queue.put(image_result['link'])
                        event.set()
                    else:
                        print(f"可能api接口已经被修改!")
                        print(image_result)
                else:
                    print(f"可能api接口已经被修改!")
                    print(image_result)
    images_queue.put(None)


if __name__ == '__main__':
    url_queue = Queue()
    image_queue = Queue()
    url_queue.put("https://images7.alphacoders.com/422/thumb-350-422813.png")
    url_queue.put(None)
    request_api_thread(url_queue, image_queue)
    while True:
        image = image_queue.get()
        if image is None:
            break
        else:
            print(image)
