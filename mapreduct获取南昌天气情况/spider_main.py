from spider.handle import put_url, download, parse, find_element, save

from threading import Thread
from queue import Queue


def main():
    parse_queue = Queue()
    url_queue = Queue()
    url_thread = Thread(target=put_url, args=(url_queue,))
    url_thread.start()
    download_threads = []
    parse_threads = []
    for item in range(4):
        download_threads.append(Thread(target=download, args=(url_queue, parse_queue)))
        parse_threads.append(Thread(target=parse, args=(parse_queue, (find_element, save))))
    for item in download_threads:
        item.start()
    for item in parse_threads:
        item.start()
    url_thread.join()
    for item in download_threads:
        item.join()
    for item in parse_threads:
        item.join()
    print("爬取结束!")


if __name__ == '__main__':
    main()
