import os

import requests
import time
import json

"""
爬取 B 站用户空间动态列表（完整复现 curl 请求）
"""

# 接口地址
DynamicURL = 'https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space'

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


def main():
    # host_mid = "436175352"
    host_mid = "3546622923377024"

    cookies_str = "enable_web_push=DISABLE; buvid_fp_plain=undefined; enable_feed_channel=ENABLE; buvid3=55B47D9F-0FE7-EB4E-D7DF-ECCBD88F224C45015infoc; b_nut=1742286045; _uuid=7106268EE-E23D-3B610-87FC-EC344F6585C442602infoc; hit-dyn-v2=1; fingerprint=ad2c19aeebce81ba025910181eca5a37; buvid_fp=ad2c19aeebce81ba025910181eca5a37; _qimei_uuid42=19705002739100cd7f73bc24bee6750d7906cdd898; _qimei_i_3=43c26581c60b03dbc593fc30538476b5f6bff1f3470805d0e5897c5e73c1763f373035943c89e29ab7a8; header_theme_version=OPEN; theme-tip-show=SHOWED; theme-avatar-tip-show=SHOWED; CURRENT_QUALITY=80; rpdid=|(J~kJu)|mu~0J'u~lJ~ukYuR; dy_spec_agreed=1; LIVE_BUVID=AUTO5717540510998206; _qimei_h38=5325990e7f73bc24bee6750d0200000571980d; buvid4=17413F75-C142-3F4B-BDA7-AD0FE38A447617347-024031215-zc+oy34FAZz4XtTqc3fRtA%3D%3D; theme-switch-show=SHOWED; DedeUserID=3546662442109032; DedeUserID__ckMd5=84a1ca737a6520b1; PVID=5; home_feed_column=5; browser_resolution=1545-819; _qimei_fingerprint=634953f821cbb95915b88ac3a1e27b85; bp_t_offset_3546662442109032=1151349258813702144; CURRENT_FNVAL=4048; b_lsid=43510AB82_19B8E78B6E1; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njc4ODEwMzcsImlhdCI6MTc2NzYyMTc3NywicGx0IjotMX0.Sm090gWO_s2Q5cHC8bTNqJQyzDcAbYaY3v76rh-gDP8; bili_ticket_expires=1767880977; SESSDATA=95782f9b%2C1783173837%2C9e0c8%2A11CjDOoV8VcJAN1ClPTb4f1YpT6P4IjwBRv5IJsYnGPPZKk8ZJzZUs_hSqnCeRrnF_v4oSVkE5SGFPZkVBNFVTQXlCSWVlWi1zRlZaOHlJdlBaUWZBbzRQeGEtREZEWDBNRDVOTlVlaGdTa0ozOEdrWmE4SlR6RDZxMXFSLWxDbEVXZUJvRzhkS3ZnIIEC; bili_jct=6d6689573bb069f44de9f2148d5fa33c; sid=802orv83; _qimei_i_1=79e96a87965855d2c897ab370d8370b2a4eca0a3470e0585b18f7c582493206c616332923980eadc828bf7c2"

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
        "cookie": cookies_str
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

    # ====== 保存全部结果 ======
    output_path = r"E:\PythonXiangmu\jsonPy\all_dynamics.json"
    # os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # with open(output_path, "w", encoding="utf-8") as f:
    #     json.dump(all_items, f, ensure_ascii=False, indent=2)
    print(f"\n🎉 共抓取 {len(all_items)} 条动态，已保存至: {output_path}")


if __name__ == '__main__':
    main()