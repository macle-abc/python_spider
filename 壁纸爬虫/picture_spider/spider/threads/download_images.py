from spider.spider_import import *


def download_images_thread(images_queue: Queue):
    """
    下载图片线程
    :param images_queue: 图片url安全队列
    :return: None
    """
    images_dir = get_setting("IMAGES_DIR")
    while True:
        try:
            image_url = images_queue.get(timeout=2)
        except queue.Empty as e:
            break
        # 图片url全部获取完成退出下载
        if image_url is None:
            break
        print(f"正在处理图片{image_url}")
        # 下载图片
        image = requests.get(image_url, headers=get_headers())
        if image.status_code != 200:
            print(f"图片下载失败!状态码为:{image.status_code}!")
        else:
            # 获取文件名
            file_name = re.compile(r"https:.*/(?P<id>\d+)")
            # 获取当前时间戳
            file_time = str(time()).replace('.', '')
            file_name = re.match(file_name, image_url)
            if not file_name:
                print(f"图片文件名匹配失败!当前url为{image_url}")
            else:
                file_name = "".join([file_name.group('id'), file_time])
                if 'Content-Type' not in image.headers:
                    print(f"图片类型获取失败!当前url为{image_url}")
                else:
                    # 从响应头中获取图片类型
                    file_type = image.headers['Content-Type'].replace('image/', '')
                    file_type = file_type.replace('"', '')
                    # 文件名为图片路径+文件名+文件类型
                    # 保存文件
                    file_name = images_dir + file_name + f".{file_type}"
                    f = open(file_name, 'wb')
                    f.write(image.content)
                    f.close()
                    print(f"{image_url}图片下载完成!保存为{file_name}")


if __name__ == '__main__':
    image_queue = Queue()
    image_queue.put("https://initiate.alphacoders.com/download/wallpaper/171916/images4/jpg/54552224378540")
    image_queue.put(None)
    download_images_thread(image_queue)
