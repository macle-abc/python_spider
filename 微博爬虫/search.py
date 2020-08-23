from loginWeiBo import Login
from requests.sessions import session
import time
import re 
import random

class Search:
    searchUrl = "https://m.weibo.cn/api/container/getIndex?" #get  """ok为0"""
    keywordList = []
    searchInfoList = []
    containerUrl = "https://m.weibo.cn/api/container/getIndex"
    def __init__(self, s:session):
        if s == None:
            print("请使用Login.login获取登录成功后的session")
        else:
            self.s = s
    
    def setKeywords(self, many:bool=False, *keywordList):
        itemInfo = {
            "containerid": "",
            "page_type":"searchall",
        }
        if many:
            self.keywordList = list(keywordList)
            print(self.keywordList)
        else:
            keyword = input("请输入需要搜索的相似用户名:")
            self.keywordList.append(keyword)
        for keyword in self.keywordList:
            import copy
            itemInfo['containerid'] = "100103type=3&q={}&t=0".format(keyword)
            self.searchInfoList.append(copy.deepcopy(itemInfo))

    def printSearchInfoList(self):
        for item in self.searchInfoList:
            print(item)

    def getUserList(self)->list:
        #多个cookie，每次getindex都让不同的cookie获取uid，
        uidList = []
        resultsList = []
        for searchInfo in self.searchInfoList:
            currentKeyword = re.search(r"type=3&q=(.*?)&t=0", searchInfo['containerid'])
            currentKeyword = currentKeyword.group(1)
     #       print(currentKeyword)
            #首次调用getindex接口
            random.seed(time.time())
            time.sleep(0.5 + random.randint(1, 5))
            try:
                userList = self.s.get(self.containerUrl, params = searchInfo)
            except Exception as e:
                print(e)
                print(f"可能需要重试!当前关键字:{currentKeyword}")
                continue
            else:
                if userList.status_code == 200:
                    try:
                        if userList.json()['ok'] == 0:
                            print(currentKeyword, "没有数据了")
                            print(userList.url)
                            continue
                        elif userList.json()['ok'] == 1:
                            for user in userList.json()['data']['cards'][1]['card_group']:
                                uidList.append(user['user']['id'])
                                print(f"当前关键词为:{currentKeyword}", end='\t')
                                print("获取到:" + user['user']['screen_name'] + "用户id:" + str(user['user']['id']))
                            print("第1次完成")
                        else:
                            print(userList.json(), "未知状态!")
                            continue
                    except Exception as e:
                        print(e)
                        print(f"{useList}中可能缺少某些字段")
                        continue
                else:
                    print(userList.url, userList.status_code, "接口调用失败")
                    continue
                page = 2
                while True:
                    params = searchInfo
                    params['page'] = f"{page}"
                    random.seed(time.time())
                    time.sleep(0.5 + random.randint(1, 5))
                    try:
                        userList = self.s.get(self.containerUrl, params = params)
                    except Exception as e:
                        print(e)
                        print(f"可能需要重试!当前关键字:{currentKeyword}")
                        break
                    if userList.status_code == 200:
                        try:
                            if userList.json()['ok'] == 0:
                                    print(searchInfo, "没有数据了")
                                    break
                            elif userList.json()['ok'] == 1:
                                for user in userList.json()['data']['cards'][0]['card_group']:
                                    uidList.append(user['user']['id'])
                                    print(f"当前关键词为:{currentKeyword}", end='\t')
                                    print("获取到:" + user['user']['screen_name'] + "用户id:" + str(user['user']['id']))
                            else:
                                    print(userList.json(), "未知状态!")
                                    break
                        except Exception as e:
                            print(e)
                            print(f"{userList}中可能缺少某些字段")
                            break
                    else:
                         print(userList.url, userList.status_code, "接口调用失败")
                         break
                    print(f"第{page}次完成")
                    page = page + 1
                print(f'{currentKeyword}已完成，获取到{len(uidList)}个uid')
                resultsList.append([currentKeyword, uidList])
        print("搜索完成")
        return resultsList


        #首先从搜索列表获取用户id            如果失败ok==0
        """
        https://m.weibo.cn/api/container/getIndex?
       containerid: 100103type=3&q=发&t=0
       page_type: searchall   分页后会多一个page字段 page:2                  ->>>>>>>>>>>uid



        根据230283+uid构建用户基本信息   !!!注意点需要用户登录才能获取更详细的信息
        containerid: 2302832528302757_-_INFO
        title: 基本资料
        luicode: 10000011
        lfid: 2302832528302757
        """
    

if __name__ == "__main__":
    login = Login("", "")
    s = login.login()
    if s != None:
        searchInstance = Search(s)
        searchInstance.setKeywords()
        searchInstance.printSearchInfoList()
        searchInstance.getUserList()
    else:
        import sys 
        sys.exit(1)

"""
               uid=253996115
containerid: 2302832539961154_-_INFO
title: 基本资料
luicode: 10000011
lfid: 2302832539961154
"""

"""
               uid= 2528302757
containerid: 230283 2528302757_-_INFO
               uid= 1649173367
containerid: 230283 1649173367_-_INFO
               uid= 1881159861
containerid: 230283 1881159861_-_INFO
title: 基本资料
luicode: 10000011
lfid: 2302831881159861
"""
