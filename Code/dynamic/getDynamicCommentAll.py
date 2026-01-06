import time
import json
import hashlib
import urllib.parse
import requests

# ====== 配置区 ======
# cookie
YOUR_COOKIE = ""
# 目标动态oid
DYNAMIC_OID = "379047058"
CURRENT_OFFSET = ""  # 初始为空字符串（第一页）

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": f"https://t.bilibili.com/{DYNAMIC_OID}",
    "Cookie": YOUR_COOKIE
}

COMMENT_URL = "https://api.bilibili.com/x/v2/reply/wbi/main"


def get_wbi_keys():
    nav_url = "https://api.bilibili.com/x/web-interface/nav"
    resp = requests.get(nav_url, headers=HEADERS)
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


#------------------------------------------------------
def fetch_all_comments(oid):
    print("正在获取 WBI 密钥...")
    img_key, sub_key = get_wbi_keys()
    offset = ""  # 字符串
    all_comments = []
    page = 0

    while True:
        page += 1
        # 安全处理 offset 类型
        current_offset = str(offset) if offset is not None else ""
        print(f"\n--- 第 {page} 页 | offset 长度: {len(current_offset)} ---")

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
        resp = requests.get(COMMENT_URL, params=signed_params, headers=HEADERS)

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

        print(f"Cursor: is_end={cursor.get('is_end')}, next={repr(cursor.get('next'))}")

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
        print(all_comments)

        # ===== 核心修复：确保 offset 始终是字符串 =====
        is_end = cursor.get('is_end', True)
        next_val = cursor.get('pagination_reply', {}).get('next_offset', '')  # ← 唯一修改点
        next_offset = str(next_val) if next_val is not None else ""

        if is_end or not next_offset.strip():
            print("🔚 结束翻页")
            break

        offset = next_offset  # 字符串赋值
        time.sleep(0.8)

    return all_comments

if __name__ == '__main__':
    comments = fetch_all_comments(DYNAMIC_OID)
    print(f"\n 总共爬取 {len(comments)} 条评论")