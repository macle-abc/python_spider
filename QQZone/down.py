from PyQt5.QtCore import QRunnable, QThreadPool
import requests
import os
import json


class Download(QRunnable):
    def __init__(self, l: list, qq:str, item:str):
        self.l = l
        self.qq = qq
        self.item = item
        super().__init__()

    def run(self):
        index = 0
        if not os.path.exists(f"download/{self.qq}/{self.item[:self.item.find('.json')]}"):
            os.makedirs(f"download/{self.qq}/{self.item[:self.item.find('.json')]}")
        for item in self.l:
            print("正在处理", index, self.qq)
            url = item.get("photo") or item.get('video')
            html = requests.get(url)
            if html.status_code != 200:
                print("下载失败!")
                return None
            filename = f"download/{self.qq}/{self.item[:self.item.find('.json')]}/{index}.{'mp4' if item.get('video') else 'jpeg'}"
            with open(filename, 'wb') as f:
                f.write(html.content)
                index += 1

threadpool = QThreadPool()
threadpool.setMaxThreadCount(8)
qqs = [""]
for qq in qqs:
    for item in os.listdir(f"data/{qq}"):
        with open(f"data/{qq}/{item}", encoding='utf-8') as f:
            urls = json.load(f)
        threadpool.start(Download(urls, qq, item))
threadpool.waitForDone()
