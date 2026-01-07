import os
import time
import json
import hashlib
import urllib.parse
import requests


# 接口地址
DynamicURL = 'https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space'
COMMENT_URL = "https://api.bilibili.com/x/v2/reply/wbi/main"


# 逆向
def get_wbi_keys(headers):
    nav_url = "https://api.bilibili.com/x/web-interface/nav"
    resp = requests.get(nav_url, headers=headers)
    json_data = resp.json()
    img_url = json_data['data']['wbi_img']['img_url']
    sub_url = json_data['data']['wbi_img']['sub_url']
    img_key = img_url.split('/')[-1].split('.')[0]
    sub_key = sub_url.split('/')[-1].split('.')[0]
    return img_key, sub_key

def getMixinKey(orig: str):
    mixin_key_enc_tab = [
        46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
        33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
        61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11,
        36, 20, 34, 44, 52
    ]
    return ''.join([orig[i] for i in mixin_key_enc_tab[:32]])

def enc_wbi(params: dict, img_key: str, sub_key: str):
    mixin_key = getMixinKey(img_key + sub_key)
    curr_time = int(time.time())
    params['wts'] = curr_time
    params = {k: v for k, v in params.items() if v != ""}
    params = dict(sorted(params.items()))
    query = urllib.parse.urlencode(params)
    w_rid = hashlib.md5((query + mixin_key).encode()).hexdigest()
    params['w_rid'] = w_rid
    return params


# 动态列表==========================================
def get_dynamic_list(host_mid, offset, headers):
    """
    获取用户空间动态
    :param host_mid: 用户 mid
    :param offset: 翻页游标，第一页传空字符串
    :param headers: 请求头（必须包含完整 Cookie）
    :return: 接口返回的 json 数据
    """
    # 完整还原 curl 中的所有 params（注意 dm_img_list 是长列表！）
    params = {
        "offset": offset,
        "host_mid": host_mid,
        "timezone_offset": "-480",
        "platform": "web",
        # "features": (
        "web_location": "333.1387",
        # "dm_img_list": (
        "x-bili-device-req-json": '{"platform":"web","device":"pc","spmid":"333.1387"}',
        # "w_rid": "cabbfbb2c9c6ecba82961d025527ed4e",
        # "wts": "1767622255"
    }

    response = requests.get(
        url=DynamicURL,
        params=params,
        headers=headers
    )
    print("接口响应状态码：", response.status_code)
    try:
        json_data = response.json()
    except Exception as e:
        print("响应非 JSON 格式，可能是被风控或 Cookie 失效")
        print("原始响应内容：", response.text[:500])
        return None

    return json_data


def get_dynamic_all(host_mid,cookies):
    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9",
        "origin": "https://space.bilibili.com",
        "referer": f"https://space.bilibili.com/{host_mid}/dynamic",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "priority": "u=1, i",
        "cookie": cookies
    }

    # ====== 新增：分页遍历逻辑 ======
    all_items = []
    offset = ""  # 初始 offset 为空

    while True:
        print(f"\n【请求】offset = {repr(offset)}")
        data = get_dynamic_list(host_mid, offset, headers)

        if not data or data.get("code") != 0:
            print("❌ 请求失败或返回错误，停止抓取")
            break

        response_data = data.get("data", {})
        items = response_data.get("items", [])
        has_more = response_data.get("has_more", False)
        next_offset = response_data.get("offset", "")

        # 合并 items（注意：有些页 items 可能是 null 或非 list）
        if isinstance(items, list):
            all_items.extend(items)
            print(f"✅ 本页获取 {len(items)} 条动态，累计 {len(all_items)} 条")
        else:
            print("⚠️ 本页 items 非列表格式，跳过")
        # 判断是否继续
        if not has_more:
            print("🔚 已无更多数据，结束遍历")
            break
        offset = next_offset
        time.sleep(0.5)  # 礼貌性延迟，避免触发风控
    return all_items


#------------------------------------------------------------------
# 评论
#------------------------------------------------------------------
def fetch_all_comments(oid,cookie,dynamic_id=None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": f"https://t.bilibili.com/{oid}",
        "Cookie": cookie
    }
    print("正在获取 WBI 密钥...\n")
    img_key, sub_key = get_wbi_keys(headers=headers)
    offset = ""  # 字符串
    all_comments = []
    page = 0

    while True:
        page += 1
        # 安全处理 offset 类型
        current_offset = str(offset) if offset is not None else ""
        print(f"第 {page} 页 | offset 长度: {len(current_offset)} ---")
        print(f"https://api.bilibili.com/x/v2/reply/wbi/main?oid={oid}")

        pagination_str = json.dumps({"offset": current_offset}, separators=(',', ':'))

        base_params = {
            'oid': oid,
            'type': '11',
            'mode': '2',
            'pagination_str': pagination_str,
            "plat": '1',
            'seek_rpid': '',
            'web_location': '1315875'
        }

        signed_params = enc_wbi(base_params, img_key, sub_key)
        resp = requests.get(COMMENT_URL, params=signed_params, headers=headers)

        if resp.status_code != 200:
            print("❌ 请求失败")
            break

        try:
            json_data = resp.json()
        except:
            break

        if json_data.get('code') != 0:
            print(f"API 错误: {json_data.get('message')}")
            break

        data = json_data.get('data', {})
        replies = data.get('replies') or []
        cursor = data.get('cursor', {})

        # print(f"Cursor: is_end={cursor.get('is_end')}, next={repr(cursor.get('next'))}")

        for reply in replies or []:
            member = reply.get('member', {})
            content = reply.get('content', {})
            control = reply.get('reply_control', {})
            time_desc = control.get("time_desc", "")

            # 提取 IP 属地：从 time_desc 中解析
            location_desc = control.get('location', '')
            location_province = ""
            if "IP属地：" in location_desc:
                try:
                    location_province = location_desc.split("IP属地：", 1)[1].strip()
                except:
                    location_province = ""

            comment = {
                "comment_id": reply.get("rpid_str"),
                "content": content.get("message"),
                "user_uid": member.get("mid"),
                "user_uname": member.get("uname"),
                "user_level": member.get("level_info", {}).get("current_level"),
                "user_avatar": member.get("avatar"),
                "like_count": reply.get("like", 0),
                "ctime": reply.get("ctime"),
                "time_desc": time_desc,
                "location": location_province
            }
            all_comments.append(comment)
        # print(all_comments)

        # ===== 核心修复：确保 offset 始终是字符串 =====
        is_end = cursor.get('is_end', True)
        next_val = cursor.get('pagination_reply', {}).get('next_offset', '')  # ← 唯一修改点
        next_offset = str(next_val) if next_val is not None else ""

        if is_end or not next_offset.strip():
            print("🔚 结束翻页")
            break

        offset = next_offset  # 字符串赋值
        time.sleep(0.5)

    return all_comments



if __name__ == "__main__":
    # 目标用户uid
    host_mid = ""
    # 你的cookie
    cookies = ""

    dynamic_all = get_dynamic_all(host_mid, cookies=cookies)

    results = []
    for item in dynamic_all:
        id_str = item.get("id_str", "")
        comment_id_str = item.get("basic", {}).get("comment_id_str", "")
        results.append({
            "id_str": id_str,
            "comment_id_str": comment_id_str
        })

    # 打印结果
    for r in results:
        # https://www.bilibili.com/opus/{id_str}
        # 动态url
        dynamic_id = r['id_str']
        dynamic_url = f"https://www.bilibili.com/opus/{dynamic_id}"
        print("===================分割线===================")
        print(f"动态链接：{dynamic_url}")
        print("===================分割线===================\n")
        # 动态评论区 id
        comment_id_str = r.get("comment_id_str")

        comments = fetch_all_comments(oid=comment_id_str, cookie=cookies,dynamic_id=dynamic_id)
        # print(comments)
        # 统计一下这个动态的评论数 （comments元素个数）
        comments_count = len(comments)
        print(comments_count)




