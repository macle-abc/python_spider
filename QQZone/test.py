import requests
from requests.sessions import session
import os
import sys
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


def get_list(next_api: str, qqnumber: str, qzonetoken: str, g_tk: str, my_cookie: dict) -> requests.Response:
    api = "https://mobile.qzone.qq.com/list"
    headers = {
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Mobile Safari/537.36",
    }
    params = {}
    if next_api:
        params['res_attach'] = next_api
    params["qzonetoken"] = qzonetoken
    params["g_tk"] = g_tk
    params["format"] = "json"
    params["list_type"] = "shuoshuo"
    params["action"] = "0"
    params["res_uin"] = qqnumber
    params["count"] = "10"
    # print(f"api={api}, headers={headers}, params={params}, cookies={my_cookie}", "!!!!!")
    try:
        html = requests.get(api, headers=headers, params=params, cookies=my_cookie, timeout=20)
    except TimeoutError as e:
        print(e, "超时", "可能被禁止!", "error")
        return None
    if html.status_code != 200:
        print(html, "动态爬取失败!", html.text, "error")
        return None
    return html


def handle_list(results: dict) -> (str, list):
    try:
        next_param = results['data']['attach_info']
    except KeyError as e:
        print(e, "缺少下次请求参数!", "error")
        return None
    try:
        vFeeds = results['data']['vFeeds']
    except KeyError as e:
        print(e, "缺少媒体信息!", "error", results)
        return None, None
    l = []
    for item in vFeeds:
        video = item.get("video")
        if video:
            video_urls = video.get('videourls')
            # print(isinstance(video_urls, list), type(video_urls))
            for each_video_url in video_urls.values():
                l.append({
                    "video": each_video_url.get('url'),
                })
        pic = item.get("pic")
        if pic:
            try:
                pic = pic['picdata']['pic']
            except KeyError as e:
                print(e, "缺少图片信息", "error")
            for each_pic in pic:
                photos = each_pic.get('photourl')
                # data.vFeeds[0].pic.picdata.pic[0].photourl[0].url
                # print(isinstance(photos, list))
                for each_photo in photos.values():
                    l.append({
                        "photo": each_photo.get('url'),
                    })
    return next_param, l


def transform_cookie(cookie: list) -> dict:
    result = {}
    for item in cookie:
        result[item['name']] = item['value']
    return result


def gettoken(cookie: list) -> str:
    tmpSkey, tmpToken = None, None
    tempskek = ""
    temppskey = ""
    for item in cookie:
        if item['name'] == "skey":
            tempskek = item['value']
        elif item['name'] == "p_skey":
            temppskey = item['value']
    # print(cookie, type(cookie))
    # return ""
    skey = temppskey or tempskek or ""
    hash = 5381
    token = tmpToken
    if skey:
        if skey != tmpSkey:
            tmpSkey = skey
            i, l = 0, len(skey)
            while i < l:
                hash += (hash << 5) + ord(skey[i])
                i += 1
            token = hash & 0x7fffffff
            return token
    else:
        return None


def login() -> (str, dict):
    options = webdriver.ChromeOptions()
    options.add_argument(
        'user-agent=Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Mobile Safari/537.36',
    )
    browser = webdriver.Chrome(chrome_options=options)
    browser.get("https://h5.qzone.qq.com/")
    try:
        WebDriverWait(browser, 1000).until(
            EC.presence_of_element_located(
                (
                    By.ID,
                    "g_list"
                )
            )
        )
    finally:
        user = browser.find_element_by_id('u')
        password = browser.find_element_by_id('p')
        user.send_keys("")
        password.send_keys("")
        password.send_keys(Keys.ENTER)
    try:
        WebDriverWait(browser, 1000).until(EC.presence_of_element_located((By.CLASS_NAME, "_not_inQQ")))
    finally:
        results = (browser.page_source, browser.get_cookies())
        # return browser.page_source, browser.get_cookies()
        browser.quit()
        return results


if __name__ == '__main__':
    html, cookie = login()
    regexp = r'shine0callback = \(function\(\){ try{return "(.*)";}'
    result = re.search(regexp, html)
    try:
        qzonetoken = result.group(1)
    except Exception as e:
        print(type(e), e, "qzonetoken获取失败!")
        sys.exit(-1)
    g_tk = gettoken(cookie)
    my_cookie = transform_cookie(cookie)
    if not g_tk:
        print("g_tk获取失败")
        sys.exit(-1)
    qqlists = [
 	"",
    ]
    for qqnumber in qqlists:
        next_api = None
        index = 0
        while True:
            print(index)
            html = get_list(next_api, qqnumber, qzonetoken, g_tk, my_cookie)
            if not html:
                print("爬取完成!", qqnumber)
                break
            try:
                my_cookie['x-stgw-ssl-info'] = html.cookies['x-stgw-ssl-info']
                js = json.loads(html.text)
            except json.JSONDecodeError as e:
                print(e, "html反序列化失败!", "error", html.text)
                sys.exit(-1)
            else:
                next_api, json_list = handle_list(js)
                if not next_api:
                    print("爬取完成!", qqnumber)
                    break
                if os.path.exists(f"data/{qqnumber}"):
                    pass
                else:
                    os.makedirs(f"data/{qqnumber}")
                if json_list:
                    with open(f"data/{qqnumber}/{index}.json", 'w', encoding='utf-8') as f:
                        json.dump(json_list, f, indent=4)
                        index += 1
                    print("处理完", index, f"qq={qqnumber}")
                else:
                    print("处理完", index, f"qq={qqnumber}", "但是没有媒体信息!")
