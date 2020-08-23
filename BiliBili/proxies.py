import random
from selenium import webdriver
import requests
import re
from bs4 import BeautifulSoup


def get_proxies():
    """从proxies.txt中返回一个可用的https代理, 如果失败将返回None"""
    with open("proxies.txt", 'r') as f:
        proxies_list = f.read()
    proxies_list = proxies_list.split('\n')
    proxies = random.choice(proxies_list)
    result = re.search(r'(.*?):[0-9]+', proxies)
    ip = result.group(1)
    proxies = {
        "http": f"http://{proxies}",
    }
    try:
        html = requests.get(f"http://ip.tool.chinaz.com/{ip}", proxies=proxies, timeout=5)
    except Exception as e:
        print("失败", ip)
        return None
    bs = BeautifulSoup(html.text, "html5lib")
    result = bs.select_one("#leftinfo > div.IcpMain02.bor-t1s02 > div.WhoIpWrap.jspu > p.WhwtdWrap.bor-b1s.col-gray03")
    if result:
        try:
            html = requests.get("https://www.baidu.com", proxies=proxies, timeout=5)
        except Exception as e:
            print("失败", ip)
            return None
        else:
            if html.status_code == 200:
                return proxies
            else:
                print("失败", ip)
                return None
    else:
        return None


def save_proxies():
    driver = webdriver.Chrome()
    driver.get("https://ip.ihuan.me/ti.html")
    import time
    print("请保存结果到proxies.txt中")
    time.sleep(60)
    driver.quit()


def get_success_proxies():
    proxies = get_proxies()
    while not proxies:
        proxies = get_proxies()
    return proxies


if __name__ == "__main__":
    save_proxies()
    # get_proxies()