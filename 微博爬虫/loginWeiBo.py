from requests.sessions import session
class Login:
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

    def __init__(self, userName:str, password:str):
        """设置用户名和密码"""
        self.loginInfo['username'] = userName 
        self.loginInfo['password'] = password

    def login(self)->session:
        """如果登录成功那么返回session否则返回None并且打印失败信息"""
        self.s = session()
        loginStatus = self.s.post(self.loginUrl, data=self.loginInfo, headers=self.headers)
        if loginStatus.status_code == 200:
           if 'errline' in loginStatus.json()['data']:
               print(loginStatus.json()['msg'])
               return None
           elif loginStatus.json()['msg'] == "":
               print("登录成功")
               return self.s
           else:
               print("未知情况")
               print(loginStatus.json())
               return None
        else:
            return None

    def printCookies(self):
        for item in self.s.cookies:
            print(item)