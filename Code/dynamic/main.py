import requests
import time
import re

from Code.dynamic.getDynamicComments import get_comments



def extract_valuable_comment_data_flat(response_json):
    """
    从 Bilibili 评论 API 响应中提取有价值的字段，返回扁平化的一层结构。
    """
    comments_list = []

    replies = response_json.get("replies")
    if replies is None:
        return replies

    for reply in replies:
        # 提取用户信息
        member_info = reply.get("member", {})
        # 提取评论内容
        content_info = reply.get("content", {})
        # 提取回复控制信息 (如 IP 属地)
        control_info = reply.get("reply_control", {})
        # 处理 location 字段，只保留地名部分
        full_location = control_info.get("location", "") # 例如 "IP属地：江苏"
        location_province = ""
        if full_location.startswith("IP属地："):
            location_province = full_location[len("IP属地："):].strip() # 提取 "江苏" 并去除可能的空格

        comment = {
            # 评论唯一标识
            "comment_id": reply.get("rpid_str"),
            # 评论内容
            "content": content_info.get("message"),
            # 用户信息 (扁平化)
            "user_uid": member_info.get("mid"),
            "user_uname": member_info.get("uname"),
            "user_level": member_info.get("level_info", {}).get("current_level"),
            "user_avatar": member_info.get("avatar"),
            # 点赞数
            "like_count": reply.get("like"),
            # 发布时间戳和格式化时间
            "ctime": reply.get("ctime"),
            "time_desc": control_info.get("time_desc"), # 如 "3小时前发布"
            # IP 属地
            "location": location_province
        }
        comments_list.append(comment)

    return comments_list


def getDynamicComments(rid_str, headers):
    Cookie = headers['Cookie']
    pn = 1
    while True:
        comments_turn_page = get_comments(rid_str, headers)
        comment_data_flat = extract_valuable_comment_data_flat(comments_turn_page)
        if comment_data_flat is not []:
            print(comment_data_flat)
        page_info = comments_turn_page.get('page', {})
        count = page_info.get('count', 0)
        if pn * 20 >= count:
            break
        pn += 1


if __name__ == '__main__':
    Cookie = "DedeUserID=166415666; DedeUserID__ckMd5=875108bbcf993082; hit-dyn-v2=1; dy_spec_agreed=1; enable_feed_channel=ENABLE; buvid_fp=c950ee71e17a2867ac097343e73041bb; header_theme_version=OPEN; theme-avatar-tip-show=SHOWED; enable_web_push=DISABLE; rpdid=|(J~kJu)|mu~0J'u~lJ))l|~Y; home_feed_column=5; browser_resolution=1707-898; theme-tip-show=SHOWED; buvid4=5B298FAE-D1CF-5E35-F2A3-2E5F082A5BD353012-025081323-U9tH98fPvljN5q4eFwc3lg%3D%3D; theme-switch-show=SHOWED; buvid3=60F81FFE-4EC0-4613-A033-53510C98BB9859942infoc; b_nut=1763880759; _uuid=105CC279D-10184-C5B1-5A8F-99AD17127F4163116infoc; CURRENT_QUALITY=0; PVID=2; LIVE_BUVID=AUTO6817662421804219; bp_t_offset_166415666=1150371702782296064; b_lsid=73D2A4A5_19B93D2A7B1; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc5NzA4MTIsImlhdCI6MTc2NzcxMTU1MiwicGx0IjotMX0._EUc9DA73c5mPgPcHNzpiVlFHmLx_rJrAXp1mbWDbk8; bili_ticket_expires=1767970752; SESSDATA=0edb8488%2C1783263613%2C878bc%2A12CjBiYIXuD9hi6l2rtl_TUDcTF7jiz9o7flrMTtXYItEM0mJGsx0gQdVsLCMNJ8_Me3MSVmlWWkM4a280cC1ndHJEZ3QtSkRFWGhDV0JkU21URWVJS0tHZm0xdDBEem53VjQ3VVFGMi1XLWZyU1FtTlNCb0NXX3pkVFdFMjVlZlhTYWxZRTNocmRBIIEC; bili_jct=3cb4e66b3e97a0141603862879a46668; sid=7vupz9px; CURRENT_FNVAL=4048"




    # rid_str 动态id
    rid_str = "379047058"

    headers = {
        "Cookie": Cookie,
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "origin": "https://www.bilibili.com",
        "priority": "u=1, i",
        # "referer": "https://www.bilibili.com/opus/1152497782492233729?spm_id_from=333.1387.0.0",
        "sec-ch-ua": '"Microsoft Edge";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0"
    }

    getDynamicComments(rid_str, headers)

    # https://api.bilibili.com/x/v2/reply/wbi/main?oid=379047058&type=11&mode=3&pagination_str=%7B%22offset%22:%22%22%7D&plat=1&seek_rpid=&web_location=1315875&w_rid=eb51b4397ef0438d5dbb6254d38237d8&wts=1767704941
