import requests
from bs4 import BeautifulSoup
from requests.sessions import session
import time
s = session()

headers = {
   "Accept": "*/*",
   "Accept-Language": "zh-CN,zh;q=0.9",
   "Content-Type": "application/x-www-form-urlencoded",
    "Host": "passport.weibo.cn",
    "Origin": "https://passport.weibo.cn",
    "Referer": "https://passport.weibo.cn/signin/login?entry=mweibo&res=wel&wm=3349&r=https%3A%2F%2Fm.weibo.cn%2F",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Mobile Safari/537.3"
    }

loginUrl = "https://passport.weibo.cn/sso/login" #post
temp = "https://m.weibo.cn/u/5644764907?uid=5644764907&t=0&luicode=10000011&lfid=100103type%3D1%26q%3D%E6%9D%A8%E8%B6%85%E8%B6%8A" #get
firstUrl = "https://m.weibo.cn/api/container/getIndex?" #get  响应包含count 在scheme里面
secondUrl = "https://m.weibo.cn/api/container/getSecond?" #get  然后不断secondUrl直到ok为0

loginInfo = {
    "username": "",
    "password": "",
    "savestate": "1",
    "r": "https://m.weibo.cn/?jumpfrom=weibocom",
    "ec": "1",
    "pagerefer": "https://m.weibo.cn/login?backURL=https%253A%252F%252Fm.weibo.cn%252F%253Fjumpfrom%253Dweibocom",
    "entry": "mweibo",
    "wentry":"", 
    "loginfrom":"", 
    "client_id": "",
    "code": "",
    "qq": "",
    "mainpageflag": "1",
    "hff": ""
   }

login = s.post(loginUrl, data=loginInfo, headers=headers)
print("------------------------登录消息-----------------------------")
print(login.status_code, login.text)
time.sleep(0.5)

tempPage = s.get(temp)
print("-----------------------temp消息-------------------------------")
print(tempPage.status_code, tempPage.text)
time.sleep(0.5)

firstInfo = {
"uid": "5644764907",
"t": "0",
"luicode": "10000011",
"lfid": "100103type=1&q=杨超越",
"containerid": "1078035644764907"
}

firstPage = s.get(firstUrl, params=firstInfo)
print("----------------------first消息-----------------------------")
if firstPage.status_code == 200:
    print("firstok")
time.sleep(0.5)

secondeInfo = {
    "containerid": "1078035644764907_-_photoall",
    "count": "24",
    "title": "图片墙",
    "luicode": "10000011",
    "lfid": "1078035644764907"
    }

#开始循环second消息
secondPage = s.get(secondUrl, params=secondeInfo)
print("-----------------------seconde消息----------------------------")
if secondPage.status_code == 200:
    results = secondPage.json()
    if results['ok'] == 1:
        try:
            for item in results['data']['cards']:
                for imgs in item['pics']:
                    print(imgs['pic_mw2000'])
        except Exception as e:
            print(e)
    elif results['ok'] == 0:
        import sys
        print("直接结束")
        sys.exit(0)

else:
    print("请重试")
time.sleep(0.5)

##开始循环
#page = 2 
#while True:
#    secondeInfo['page'] = page
#    secondPage = s.get(secondUrl, params=secondeInfo)
#    print("第" + str(page - 1) + "次循环")
#    if secondPage.status_code == 200:
#        results = secondPage.json()
#        if results['ok'] == 1:
#            try:
#                for item in results['data']['cards']:
#                    for imgs in item['pics']:
#                        print(imgs['pic_mw2000'])
#            except Exception as e:
#                print(e)
#                break
#        elif results['ok'] == 0:
#            print("结束了")
#            break
#    else:
#        print("请重试" + str(page - 1))
#    time.sleep(0.5)
#    page = page + 1

#s.close()
