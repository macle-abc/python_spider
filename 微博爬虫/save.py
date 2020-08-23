import json
import pymysql
import datetime

conn = pymysql.connect(host="192.168.1.107", user="abc", passwd="testabc", db="weibo")
cur = conn.cursor()

def SaveItem(cur, uid:int, name:str=None, introduction:str=None, regtime:datetime.date=None, sex:bytes=None, birthday:datetime.date=None, constellation:str=None, location:str=None, school:str=None, company:str=None):
    sql = "insert into UserInfo values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    try:
        cur.execute(sql, (name, introduction, regtime, sex, birthday, constellation, location, school, company, uid))
        conn.commit()
    except Exception as e:
        with open('error.txt', 'a') as f:
            f.write("="*40 + "记录失败" + str(e) + "uid:" + str(uid) + str(datetime.datetime.now()))
            f.write("\n")


with open(r"", 'r') as f:
    index = 1
    for row in f:
        print(index)
        dic = json.loads(row)
        record = {}
        for key in ['name', 'introduction', 'regtime', 'sex', 'birthday', 'constellation', 'location', 'school', 'company', 'uid']:
            record[key] = dic[key] if key in dic else None 
        if record['sex'] != None:
            if record['sex'] == '男':
                record['sex'] = b'\x01'
            elif record['sex'] == '女':
                record['sex'] = b'\x00'
        print(record)
        SaveItem(cur, **record)
        index = index + 1



cur.close()
conn.close()

