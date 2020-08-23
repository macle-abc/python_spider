from spider.threads import *

from threading import Thread, Event
from queue import Queue
from multiprocessing import cpu_count


def main():
    """
    程序入口
    :return: None
    """
    while True:
        result = input("请输入需要爬取的起始页数目以及共需爬取的数目以空格间隔(eg:1 10):").split()
        if len(result) != 2:
            print("格式错误!请重新输入!(eg:1 10)")
        else:
            try:
                start_number, count = int(result[0]), int(result[1])
            except ValueError as e:
                print("格式错误!请重新输入!(eg:1 10)")
            else:
                break
    page_queue = Queue()
    urls_queue = Queue()
    images_queue = Queue()
    event = Event()
    threads = [
        Thread(target=parse.parse_thread, args=(page_queue, start_number, count)),
        Thread(target=parse_images.parse_images_url_thread, args=(page_queue, urls_queue)),
        Thread(target=request_api.request_api_thread, args=(urls_queue, images_queue, event)),
    ]
    download_threads = []
    for item in range(cpu_count() * 2):
        download_threads.append(
            Thread(target=download_images.download_images_thread, args=(images_queue,)),
        )
    for thread in threads:
        thread.start()
    event.wait()
    for thread in download_threads:
        thread.start()
    for thread in threads:
        thread.join()
    for thread in download_threads:
        thread.join()
    print("爬取完成!")


if __name__ == '__main__':
    main()
