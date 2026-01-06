import time
import json
import hashlib
import urllib.parse
import requests

# ====== 配置区 ======
YOUR_COOKIE = "enable_web_push=DISABLE; buvid_fp_plain=undefined; enable_feed_channel=ENABLE; buvid3=55B47D9F-0FE7-EB4E-D7DF-ECCBD88F224C45015infoc; b_nut=1742286045; _uuid=7106268EE-E23D-3B610-87FC-EC344F6585C442602infoc; hit-dyn-v2=1; fingerprint=ad2c19aeebce81ba025910181eca5a37; buvid_fp=ad2c19aeebce81ba025910181eca5a37; _qimei_uuid42=19705002739100cd7f73bc24bee6750d7906cdd898; _qimei_i_3=43c26581c60b03dbc593fc30538476b5f6bff1f3470805d0e5897c5e73c1763f373035943c89e29ab7a8; header_theme_version=OPEN; theme-tip-show=SHOWED; theme-avatar-tip-show=SHOWED; CURRENT_QUALITY=80; rpdid=|(J~kJu)|mu~0J'u~lJ~ukYuR; dy_spec_agreed=1; LIVE_BUVID=AUTO5717540510998206; _qimei_h38=5325990e7f73bc24bee6750d0200000571980d; buvid4=17413F75-C142-3F4B-BDA7-AD0FE38A447617347-024031215-zc+oy34FAZz4XtTqc3fRtA%3D%3D; theme-switch-show=SHOWED; DedeUserID=3546662442109032; DedeUserID__ckMd5=84a1ca737a6520b1; PVID=5; home_feed_column=5; browser_resolution=1545-819; _qimei_fingerprint=634953f821cbb95915b88ac3a1e27b85; bp_t_offset_3546662442109032=1151349258813702144; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc4ODEwMzcsImlhdCI6MTc2NzYyMTc3NywicGx0IjotMX0.Sm090gWO_s2Q5cHC8bTNqJQyzDcAbYaY3v76rh-gDP8; bili_ticket_expires=1767880977; SESSDATA=95782f9b%2C1783173837%2C9e0c8%2A11CjDOoV8VcJAN1ClPTb4f1YpT6P4IjwBRv5IJsYnGPPZKk8ZJzZUs_hSqnCeRrnF_v4oSVkE5SGFPZkVBNFVTQXlCSWVlWi1zRlZaOHlJdlBaUWZBbzRQeGEtREZEWDBNRDVOTlVlaGdTa0ozOEdrWmE4SlR6RDZxMXFSLWxDbEVXZUJvRzhkS3ZnIIEC; bili_jct=6d6689573bb069f44de9f2148d5fa33c; sid=802orv83; CURRENT_FNVAL=4048; b_lsid=D9978D83_19B93B7EFA8; _qimei_i_1=7bc14687965855d2c897ab370d8370b2a4eca0a3470e0585b18f7c582493206c616332923980eadc82b7fcf0"

DYNAMIC_OID = "379047058"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": f"https://t.bilibili.com/{DYNAMIC_OID}",
    "Cookie": YOUR_COOKIE
}

COMMENT_URL = "https://api.bilibili.com/x/v2/reply/wbi/main"


# ====== WBI 工具函数（保持不变）======
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


# ====== 获取全部评论（核心修改）======
def fetch_all_comments(oid):
    # 初始化 WBI 密钥
    img_key, sub_key = get_wbi_keys()
    offset = ""
    all_comments = []
    page = 0
    retry_count = 0
    max_retries = 3

    while True:
        page += 1
        print(f"\n--- 正在获取第 {page} 页评论 ---")

        base_params = {
            'oid': oid,
            'type': '11',
            'mode': '3',
            'pagination_str': json.dumps({"offset": offset}, separators=(',', ':')),
            "plat": '1',
            'seek_rpid': '',
            'web_location': '1315875'
        }

        signed_params = enc_wbi(base_params, img_key, sub_key)
        resp = requests.get(COMMENT_URL, params=signed_params, headers=HEADERS)

        print(f"状态码: {resp.status_code}")

        # 如果是 412（WBI 失效），重新获取密钥
        if resp.status_code == 412 and retry_count < max_retries:
            print("⚠️ WBI 密钥可能过期，正在刷新...")
            time.sleep(1)
            img_key, sub_key = get_wbi_keys()
            retry_count += 1
            continue  # 重试当前页
        else:
            retry_count = 0  # 重置重试计数

        if resp.status_code != 200:
            print("❌ 请求失败，停止爬取")
            break

        try:
            json_data = resp.json()
        except Exception as e:
            print(f"JSON 解析失败: {e}")
            break

        code = json_data.get('code')
        if code == -404:
            print("动态不存在或已删除")
            break
        elif code != 0:
            msg = json_data.get('message', '未知错误')
            print(f"API 错误 ({code}): {msg}")
            # 如果是签名错误，尝试刷新 WBI
            if code == -403 and retry_count < max_retries:
                print("可能是 WBI 签名失效，刷新密钥...")
                img_key, sub_key = get_wbi_keys()
                retry_count += 1
                continue
            else:
                break

        data = json_data.get('data', {})
        replies = data.get('replies', []) or []
        cursor = data.get('cursor', {})

        # 提取评论
        for reply in replies:
            member = reply.get('member', {})
            content = reply.get('content', {})
            control = reply.get('reply_control', {})
            full_loc = control.get('location', '')
            location = full_loc[5:].strip() if full_loc.startswith('IP属地：') else ''

            comment = {
                'rpid': reply.get('rpid'),
                'content': content.get('message'),
                'uname': member.get('uname'),
                'like': reply.get('like', 0),
                'ctime': reply.get('ctime'),
                'location': location
            }
            all_comments.append(comment)
            print(f"[{comment['uname']}] {comment['content']}")

        # 判断是否结束
        is_end = cursor.get('is_end', True)
        offset = cursor.get('next', '')

        if is_end or not offset:
            print("✅ 已到达最后一页，评论爬取完成")
            break

        time.sleep(0.8)  # 更保守的延迟，避免被限流

    return all_comments


# ====== 执行 ======
if __name__ == '__main__':
    print(f"开始爬取动态 {DYNAMIC_OID} 的全部评论...")
    comments = fetch_all_comments(DYNAMIC_OID)
    print(f"\n🎉 共成功获取 {len(comments)} 条评论")

    # # 可选：保存到文件
    # with open(f"comments_{DYNAMIC_OID}.json", "w", encoding="utf-8") as f:
    #     json.dump(comments, f, ensure_ascii=False, indent=2)
    # print(f"评论已保存至 comments_{DYNAMIC_OID}.json")