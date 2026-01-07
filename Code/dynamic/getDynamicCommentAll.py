import time
import json
import hashlib
import urllib.parse
import requests

# ====== 配置区 ======
# cookie
COOKIE = ""
# 目标动态oid
DYNAMIC_OID = "379047058"
CURRENT_OFFSET = ""  # 初始为空字符串（第一页）

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": f"https://t.bilibili.com/{DYNAMIC_OID}",
    "Cookie": COOKIE
}

COMMENT_URL = "https://api.bilibili.com/x/v2/reply/wbi/main"


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


#------------------------------------------------------
def fetch_all_comments(oid,cookie):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": f"https://t.bilibili.com/{oid}",
        "Cookie": cookie
    }
    print("正在获取 WBI 密钥...")
    img_key, sub_key = get_wbi_keys(headers)
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
    # 键盘输入cookie
    # cookie = input("请输入cookie：")

    cookie = "enable_web_push=DISABLE; buvid_fp_plain=undefined; enable_feed_channel=ENABLE; buvid3=55B47D9F-0FE7-EB4E-D7DF-ECCBD88F224C45015infoc; b_nut=1742286045; _uuid=7106268EE-E23D-3B610-87FC-EC344F6585C442602infoc; hit-dyn-v2=1; fingerprint=ad2c19aeebce81ba025910181eca5a37; buvid_fp=ad2c19aeebce81ba025910181eca5a37; _qimei_uuid42=19705002739100cd7f73bc24bee6750d7906cdd898; _qimei_i_3=43c26581c60b03dbc593fc30538476b5f6bff1f3470805d0e5897c5e73c1763f373035943c89e29ab7a8; header_theme_version=OPEN; theme-tip-show=SHOWED; theme-avatar-tip-show=SHOWED; CURRENT_QUALITY=80; rpdid=|(J~kJu)|mu~0J'u~lJ~ukYuR; dy_spec_agreed=1; LIVE_BUVID=AUTO5717540510998206; _qimei_h38=5325990e7f73bc24bee6750d0200000571980d; buvid4=17413F75-C142-3F4B-BDA7-AD0FE38A447617347-024031215-zc+oy34FAZz4XtTqc3fRtA%3D%3D; theme-switch-show=SHOWED; DedeUserID=3546662442109032; DedeUserID__ckMd5=84a1ca737a6520b1; PVID=5; home_feed_column=5; browser_resolution=1545-819; _qimei_fingerprint=634953f821cbb95915b88ac3a1e27b85; bp_t_offset_3546662442109032=1151349258813702144; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc4ODEwMzcsImlhdCI6MTc2NzYyMTc3NywicGx0IjotMX0.Sm090gWO_s2Q5cHC8bTNqJQyzDcAbYaY3v76rh-gDP8; bili_ticket_expires=1767880977; SESSDATA=95782f9b%2C1783173837%2C9e0c8%2A11CjDOoV8VcJAN1ClPTb4f1YpT6P4IjwBRv5IJsYnGPPZKk8ZJzZUs_hSqnCeRrnF_v4oSVkE5SGFPZkVBNFVTQXlCSWVlWi1zRlZaOHlJdlBaUWZBbzRQeGEtREZEWDBNRDVOTlVlaGdTa0ozOEdrWmE4SlR6RDZxMXFSLWxDbEVXZUJvRzhkS3ZnIIEC; bili_jct=6d6689573bb069f44de9f2148d5fa33c; sid=802orv83; CURRENT_FNVAL=4048; b_lsid=67418D7B_19B98E542D7; _qimei_i_1=5bf34d87965855d2c897ab370d8370b2a4eca0a3470e0585b18f7c582493206c616332923980eadc829cff8e"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": f"https://t.bilibili.com/{DYNAMIC_OID}",
        "Cookie": cookie
    }

    oid = DYNAMIC_OID

    comments = fetch_all_comments(oid=oid,cookie=cookie)
    print(f"\n 总共爬取 {len(comments)} 条评论")