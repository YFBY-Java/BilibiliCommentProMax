import requests
import time





def get_UserName(mid,Cookie):
    headers = {
        'authority': 'api.bilibili.com',
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'no-cache',
        'origin': 'https://space.bilibili.com',
        'pragma': 'no-cache',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        'cookie': Cookie
    }
    nameURL = f"https://api.bilibili.com/x/space/acc/info?mid={mid}"
    # nameURL = f"https://api.bilibili.com/x/space/wbi/acc/info?mid={mid}"

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


if __name__ == '__main__':
    print(get_UserName(mid=1340190821))