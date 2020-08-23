rowList = []
import re
with open(r"", 'r', encoding='utf-8') as f:
    for row in f:
        rowList.append(row)

tempList = []
uidSet = set()
uidList = []
for each in rowList:
    if each.find("错误类型:<class 'KeyError'>") != -1:
        result = re.search(r'uid:5071967746\|ouid:([0-9]{10})', each)
        if result != None:
            print(result.group(1))
            uidList.append(result.group(1))
        else:
            tempList.append(each)
    else:
        tempList.append(each)
        print("=" * 80) 


uidSet = set(uidList)
print("temp" + "=" * 80)
print(tempList)
print("len(set)" + str(len(uidSet)))
print("len(list)" + str(len(uidList)))
with open("firstUid.txt", 'w', encoding='utf-8') as f:
    for each in uidSet:
        f.write(str(each) + '\n')
