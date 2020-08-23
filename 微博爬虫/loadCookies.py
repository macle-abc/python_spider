def GetCookies(filePath:str)->dict:
    cookies = {}
    import json
    with open(filePath, 'r') as f:
        result = json.load(f)
        for item in result:
            cookies[item['name']] = item['value']
    return cookies

if __name__ == "__main__":
    print(GetCookies(r""))
