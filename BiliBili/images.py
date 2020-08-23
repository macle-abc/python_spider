# 传入一个mid开始爬取
# 需要记录最新爬取时间
from headers import get_headers
from proxies import get_success_proxies
import os
import json
import re
import requests
import multiprocessing

"""相册页api"""
# 成功:
# data:items有数据
# 失败:
# data:items没有数据

def download_multiply(urls:set, uid:int, process_num:int):
    pool = multiprocessing.Pool(processes=process_num)
    if not urls:
        return None
    urls = list(urls)
    for i in range(0, len(urls), process_num):
        temp = urls[i:i + process_num]
        pool.apply_async(download_list, (temp, uid))
    pool.close()
    pool.join()
    print(uid, "下载完成!")


def download_list(urls:list, uid:int):
    for url in urls:
        download_one(url, uid)


def download_one(url:str, uid:int):
    headers = get_headers()
    result = re.search(r"([\w]+).(bmp|jpg|png|tif|gif|pcx|tga|exif|fpx|svg|psd|cdr|pcd|dxf|ufo|eps|ai|raw|WMF|webp|image)", url)
    if not result:
        print("图片格式匹配失败!", url)
        return None
    file_name = result.group(1)
    format = result.group(2)
    file_name = f"{file_name}.{format}"
    html = requests.get(url, headers=headers)
    if html.status_code != 200:
        print("图片下载失败!", html.status_code)
        return None
    if not os.path.exists(f"images/{uid}/"):
        os.makedirs(f"images/{uid}/")
    with open(f"images/{uid}/{file_name}", 'wb') as f:
        f.write(html.content)
    print("图片下载完成", url)


def get_images_set_and_save_ctime(uid:int)->set:
    images_set = set()
    images_doc_list_api = "https://api.vc.bilibili.com/link_draw/v1/doc/doc_list"
    headers = get_headers()
    # proxies = get_success_proxies()

    if os.path.exists(f"{uid}.ctime"):
        with open(f"{uid}.ctime", 'r') as f:
            ctime = f.read()
    else:
        ctime = 0
    ctime = int(ctime) if ctime else 0

    # 第一次单独处理

    current_page_num = 0
    while True:
        params = {
            "uid": uid,
            "page_num": current_page_num,
            "page_size": 30,
            "biz": "all",
        }
        html = requests.get(images_doc_list_api, headers=headers, params=params)
        html.encoding = 'utf-8'
        if html.status_code != 200:
            print("获取图片列表状态码异常!", html.status_code)
            return None
        result = json.loads(html.text)
        items = result['data']['items']
        # 如果为空表示无需继续
        if not items:
            return images_set
        if current_page_num == 0:
            new_ctime = items[0]['ctime']
            new_ctime = int(new_ctime)
            if new_ctime > ctime:
                with open(f"{uid}.ctime", 'w') as f:
                    f.write(str(new_ctime))
            else:
                print("已经存在过去的图片,无需获取图片集!")
                return None
        current_page_num = current_page_num + 1


        for item in items:
            # 先判断是否需要保存
            current_ctime = int(item['ctime'])
            if current_ctime < ctime:
                # 无需保存
                continue
            pictures = item['pictures']
            for picture in pictures:
                images_set.add(picture['img_src'])
    return images_set


if __name__ == "__main__":
    uids = []
    for uid in uids:
        s = get_images_set_and_save_ctime(uid)
        download_multiply(s, uid, 4)
