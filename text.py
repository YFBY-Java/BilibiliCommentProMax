import requests
import time
import re
import jieba
from collections import Counter




def get_bvid_info(bvid):
    """获取B站视频的aid和cid等信息"""
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/91.0.4472.124 Safari/537.36",
        "Referer": f"https://www.bilibili.com/video/{bvid}"
    }
    try:
        response = requests.get(url, headers=headers)
        print(response.text)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        if data["code"] == 0:
            aid = data["data"]["aid"]
            cid = data["data"]["cid"]
            title = data["data"]["title"]
            # 获取总评论数
            reply_count = data["data"]["stat"]["reply"]
            return aid, cid, title, reply_count
        else:
            return None, None, None, None
    except requests.exceptions.RequestException:
        return None, None, None, None



def get_comments(aid, page=1, size=20):
    """获取B站视频评论"""
    url = f"https://api.bilibili.com/x/v2/reply/main"
    params = {
        "jsonp": "jsonp",
        "next": page,
        "type": 1,
        "oid": aid,
        "mode": 3,  # 3表示按热度排序，2表示按时间排序
        "plat": 1,
        "size": size
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/91.0.4472.124 Safari/537.36",
        "Referer": f"https://www.bilibili.com/video/BV{aid}"
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        print(response.text)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()
    except requests.exceptions.RequestException:
        return None


def parse_comments(json_data):
    """解析评论数据"""
    comments = []
    if json_data and json_data["code"] == 0:
        replies = json_data["data"]["replies"]
        if replies:
            for reply in replies:
                comment = {
                    "user_name": reply["member"]["uname"],
                    "user_id": reply["member"]["mid"],
                    "content": reply["content"]["message"],
                    "like_count": reply["like"],
                    "reply_count": reply["rcount"],
                    "comment_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(reply["ctime"]))
                }
                comments.append(comment)
    return comments


def get_data(bvid, sample_quantity=30):
    """主函数"""

    # 验证BV号格式
    bvid_pattern = r'^BV[A-Za-z0-9]{10}$'
    if not re.match(bvid_pattern, bvid):
        return 500, '参数不合法'

    # 获取视频信息，包括总评论数
    aid, cid, title, reply_count = get_bvid_info(bvid)
    if not aid or not cid:
        return 500, '数据异常'

    # 计算总页数（每页20条评论）
    if reply_count:

        all_comments = []
        page = 1

        # 循环获取所有页评论
        while True:
            json_data = get_comments(aid, page)
            print(json_data)

            if not json_data or json_data["code"] != 0 or "replies" not in json_data["data"]:
                break

            comments = parse_comments(json_data)
            if not comments:
                break

            all_comments.extend(comments)

            # 检查是否还有下一页
            if len(comments) < 20:
                break

            # if page == 30:
            #     break

            page += 1


if __name__ == '__main__':
    bvid = 'BV1X7anzVEB5'
    get_data(bvid)