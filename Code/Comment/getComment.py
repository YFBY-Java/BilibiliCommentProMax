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


def getVideoInformation(BV, headers):
    """
    获取视频的基本信息
    :param BV:
    :return:
    """
    name_url = 'https://api.bilibili.com/x/web-interface/view'
    data = {
        'bvid': BV
    }
    response = requests.get(url=name_url, params=data, headers=headers)
    json_data = response.json()
    BV_Name = json_data['data']['title']
    data = {
        'BV_aid': json_data['data']['aid'],
        'BV_Name': BV_Name
    }
    print(f"正在爬取视频《{BV_Name}》的评论--->>>")
    return data


def get_md5(data, oid, date):
    Zt = [
        "mode=3",  # "mode=3" 表示用"最热评论"排序
        f"oid={oid}",
        f"pagination_str={quote(data)}",
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
def get_comments(pn, oid, headers, csv_writer):
    # 时间戳
    date = (time.time() * 1000)
    pagination_str = '{"offset":"{\\"type\\":1,\\"direction\\":1,\\"data\\":{\\"pn\\":%s}}"}' % pn

    w_rid = get_md5(pagination_str, oid, date)
    data = {
        'oid': oid,
        'type': '1',
        'mode': '3',   # 3表示按热度排序，2表示按时间排序
        'pagination_str': pagination_str,
        "plat": '1',
        # 'seek_rpid':'',
        'web_location': '1315875',
        'w_rid': w_rid,
        'wts': date
    }
    # 发送请求
    response = requests.get(url=CommentURL, params=data, headers=headers)
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
    writeComment(json_data, csv_writer)
    return data


def writeComment(json_data, csv_writer):
    # 提取数据所在的列表
    replies_ = json_data['data']['replies']
    for index in replies_:
        # 评论
        message_ = index['content']['message'].replace("\n", ",")
        name = index['member']['uname']  # 昵称
        mid = str(index['member']['mid'])  # uid
        rank = index['member']['rank']  # 用户权重，一般均为10000 (年度大会员也为10000)
        """
            B站以前不显示ip,老评论没有ip,必须对ip进行处理，如果不处理，会出现   KeyError: 'location' 的错误 
        """
        if 'reply_control' in index and 'location' in index['reply_control']:
            location = index['reply_control']['location']
            # 进行处理
        else:
            # 进行处理，因为找不到reply_control键或者location键
            location = "无IP"

        # location = index['reply_control']['location']  # ip
        location = location.replace("IP属地：", "")
        sex = index['member']['sex']
        level_info = index['member']['level_info']['current_level']  # 等级
        decorationName = index['member']['pendant']['name']  # 装扮名
        like = index['like']
        fans_detail = index['member']['fans_detail']
        if fans_detail is not None:
            fans_detail = index['member']['fans_detail']['level']
        dit = {
            '昵称': name,
            '性别': sex,
            'IP': location,
            'UID': mid,
            '等级': level_info,
            '装扮': decorationName,
            '用户权重': rank,
            '获赞数': like,
            '粉丝团等级': fans_detail,
            '评论': message_
        }

        csv_writer.writerow(dit)


def download_comment(Cookie, BV, UserName):
    headers = {
        # "Cookie": Cookie,
        # "Referer":
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    }
    data = getVideoInformation(BV, headers)
    BV_Name = data['BV_Name']
    BV_oid = data['BV_aid']
    file_name = BV + ".csv"

    with open(f"资源列表/评论列表/{UserName}/{file_name}", mode='w', encoding='gbk', newline='', errors='ignore') as f:
        # 在这里操作文件
        csv_writer = csv.DictWriter(f, fieldnames=[
            '昵称',
            '性别',
            'IP',
            'UID',
            '等级',
            '装扮',
            '用户权重',
            '获赞数',
            '粉丝团等级',
            '评论'
        ], quoting=csv.QUOTE_ALL)  # fieldnames 指定csv文件中的字段名 即表头
        csv_writer.writeheader()  # writeheader() 写入表头

        pn = 1
        while True:
            data = get_comments(pn, BV_oid, headers, csv_writer)
            pn = pn + 1
            is_end = data['is_end']
            if is_end is True:
                break
    print(f"视频《{BV_Name}》的评论下载完毕!")
