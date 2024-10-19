import requests
import time



def get_UserName(mid):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    }
    nameURL = f"https://api.bilibili.com/x/space/acc/info?mid={mid}"

    while True:
        response = requests.get(url=nameURL, headers=headers)
        json_data = response.json()
        print(json_data)
        if json_data['code'] == -799:
            print("请求过于频繁，程序将沉睡1秒")
            time.sleep(1)
            continue
        if json_data['code'] == 0:
            json_data = json_data['data']
            mid = json_data['mid']
            name = json_data['name']
            print(f"UID:{mid}\tName:[{name}]")
            return name
        if json_data['code'] == -412:
            print("请求被拦截，当前使用的IP已经被拉黑，请更换IP")
            return None


