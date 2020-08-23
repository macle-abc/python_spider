import requests
from bs4 import BeautifulSoup

from .item import NanChangTemperature

from queue import Queue
import queue
import re

base_url = "http://lishi.tianqi.com/nanchang/"
headers = {
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36"
}


def put_url(q: Queue):
    for year in range(2011, 2021):
        for month in range(1, 13):
            if year == 2020 and month > 5:
                continue
            else:
                q.put(f"{base_url}{year}{month:02}.html")
    q.put(None)


def download(q: Queue, parse_queue: Queue):
    while True:
        try:
            item = q.get(timeout=2)
        except queue.Empty as e:
            break
        if item is None:
            break
        else:
            print(f"正在下载{item}")
            parse_queue.put(requests.get(item, headers=headers))
    parse_queue.put(None)


def parse(parse_queue: Queue, handle_funcs: tuple):
    while True:
        try:
            item = parse_queue.get(timeout=2)
        except queue.Empty as e:
            break
        if item is None:
            break
        else:
            for func in handle_funcs:
                item = func(item)


def save(item):
    for each_data in item:
        NanChangTemperature(date=each_data['date'], max_temperature=each_data['max_temperature']).save()


def find_element(item):
    if item.status_code != 200:
        return None
    else:
        bs = BeautifulSoup(item.text, 'html5lib')
        ul = bs.select(".thrui li")
        for each in ul:
            date = each.select_one(".th200")
            max_temperature = each.select_one("div:nth-child(2)")
            if date and max_temperature:
                date = date.string
                date = re.search(r"(?P<date>(\d+-){2}\d+).*", date)
                max_temperature = max_temperature.string
                max_temperature = re.search(r"(?P<temperature>-?\d+).*", max_temperature)
                if date and max_temperature:
                    date = date.group('date')
                    max_temperature = int(max_temperature.group('temperature'))
                    yield {"date": date, "max_temperature": max_temperature}
                else:
                    print("可能遗漏数据!", item.url)
            else:
                print("可能遗漏数据!", item.url)
