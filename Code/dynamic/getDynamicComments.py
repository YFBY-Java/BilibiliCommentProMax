import json

import requests
import csv
# 导入MD5
import hashlib
import time
from urllib.parse import quote

"""
爬取具体视频的评论
"""

Base_Url = 'https://www.bilibili.com/video/'
CommentURL = 'https://api.bilibili.com/x/v2/reply/wbi/main'
# CommentURL = 'https://api.bilibili.com/x/v2/reply/main'
BV_Name = None


def get_md5(pagination_str, oid, date):
    Zt = [
        "mode=3",  # "mode=3" 表示用"最热评论"排序
        f"oid={oid}",
        f"pagination_str={quote(pagination_str)}",
        "plat=1",
        "type=1",
        "web_location=1315875",
        f"wts={date}"  # 时间戳
    ]
    ct = "ea1db124af3c7062474693fa704f4ff8"  # B站的一个通用常量
    Ut = '&'.join(Zt)
    string = Ut + ct
    MD5 = hashlib.md5()
    MD5.update(string.encode('utf-8'))
    w_rid = MD5.hexdigest()
    # print(w_rid)
    return w_rid


# 原方法，会触发风控
def get_comments(pn, oid, headers):
    # 时间戳
    date = int(time.time())
    pagination_str = '{"offset":"{\\"type\\":1,\\"direction\\":1,\\"data\\":{\\"pn\\":%s}}"}' % pn

    w_rid = get_md5(pagination_str, oid, date)
    data = {
        'oid': oid,
        'type': '1',
        'mode': '3',   # 3表示按热度排序，2表示按时间排序
        'pagination_str': pagination_str,
        "plat": '1',
        'seek_rpid':'',
        'web_location': '1315875',
        'w_rid': w_rid,
        'wts': date
    }
    # 发送请求
    response = requests.get(url=CommentURL, params=data, headers=headers)
    # 打印出完整请求
    print(response.request.url)
    # 接口 https://api.bilibili.com/x/v2/reply/wbi/main 响应状态码
    print('接口https://api.bilibili.com/x/v2/reply/wbi/main  响应：', response.status_code)
    # 获取数据
    json_data = response.json()
    print(json_data)
    next_page = json_data['data']['cursor']['next']
    is_end = json_data['data']['cursor']['is_end']
    # session_id = json_data['data']['cursor']['session_id']
    data = {
        'is_end': is_end,
        'next_page': next_page
    }

    return data





def get_comments_TurnPage(Cookie=None, type_code=None, oid=None, sort=0, nohot=0, ps=20, pn=1):
    """
    获取评论区明细_翻页加载
    Args:
        access_key (str, optional): APP 登录 Token。如果使用 APP 方式认证则必要。
        type_code (int): 评论区类型代码。必要。
        oid (int): 目标评论区 id。必要。
        sort (int, optional): 排序方式，默认为0。
            0：按时间
            1：按点赞数
            2：按回复数
        nohot (int, optional): 是否不显示热评，默认为0。
            1：不显示
            0：显示
        ps (int, optional): 每页项数，默认为20。定义域：1-20
        pn (int, optional): 页码，默认为1。

    Returns:
        dict: API响应的 JSON 数据。
    """
    url = "https://api.bilibili.com/x/v2/reply"

    params = {
        "type": type_code,
        "oid": oid,
        "sort": sort,
        "nohot": nohot,
        "ps": ps,
        "pn": pn
    }

    # 注意：如果使用 Cookie (SESSDATA) 认证，需要在 headers 中添加 Cookie
    headers = {
        "Cookie": Cookie,
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "origin": "https://www.bilibili.com",
        "priority": "u=1, i",
        "referer": "https://www.bilibili.com/opus/1152497782492233729?spm_id_from=333.1387.0.0",
        "sec-ch-ua": '"Microsoft Edge";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0"
    }

    response = requests.get(url, params=params, headers=headers)
    response.encoding = 'utf-8'  # 请求后，设置编码
    json_data = response.json()['data']
    # json_string = json.dumps(json_data, ensure_ascii=False, indent=2)
    # print(json_string)
    return json_data



