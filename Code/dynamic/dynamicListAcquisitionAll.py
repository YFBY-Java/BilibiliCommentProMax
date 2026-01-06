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

    cookies_str = ""


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
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    print(f"\n🎉 共抓取 {len(all_items)} 条动态，已保存至: {output_path}")


if __name__ == '__main__':
    main()