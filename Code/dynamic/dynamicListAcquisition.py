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
        #     "itemOpusStyle,listOnlyfans,opusBigCover,onlyfansVote,"
        #     "forwardListHidden,decorationCard,commentsNewVersion,"
        #     "onlyfansAssetsV2,ugcDelete,onlyfansQaCard,avatarAutoTheme,"
        #     "sunflowerStyle,cardsEnhance,eva3CardOpus,eva3CardVideo,"
        #     "eva3CardComment"
        # ),
        "web_location": "333.1387",
        # "dm_img_list": (
        #     '[{"x":2776,"y":1731,"z":0,"timestamp":1926,"k":74,"type":0},'
        #     '{"x":2785,"y":1741,"z":6,"timestamp":2134,"k":95,"type":0},'
        #     '{"x":2949,"y":2089,"z":101,"timestamp":2235,"k":104,"type":0},'
        #     '{"x":3120,"y":2379,"z":168,"timestamp":2335,"k":79,"type":0},'
        #     '{"x":4168,"y":4095,"z":454,"timestamp":2435,"k":101,"type":0},'
        #     '{"x":3796,"y":4071,"z":188,"timestamp":2535,"k":78,"type":0},'
        #     '{"x":4149,"y":4162,"z":499,"timestamp":2635,"k":70,"type":0},'
        #     '{"x":3696,"y":3668,"z":31,"timestamp":2735,"k":60,"type":0},'
        #     '{"x":4004,"y":3567,"z":232,"timestamp":2835,"k":113,"type":0},'
        #     '{"x":4435,"y":3937,"z":616,"timestamp":2936,"k":81,"type":0},'
        #     '{"x":4394,"y":4015,"z":540,"timestamp":3037,"k":80,"type":0},'
        #     '{"x":4557,"y":4187,"z":699,"timestamp":3141,"k":93,"type":0},'
        #     '{"x":4490,"y":4122,"z":626,"timestamp":3280,"k":108,"type":0},'
        #     '{"x":4336,"y":3977,"z":468,"timestamp":3380,"k":113,"type":0},'
        #     '{"x":5327,"y":4992,"z":1456,"timestamp":3483,"k":72,"type":0},'
        #     '{"x":4072,"y":3738,"z":198,"timestamp":3584,"k":122,"type":0},'
        #     '{"x":5087,"y":4746,"z":1211,"timestamp":4016,"k":95,"type":0},'
        #     '{"x":4672,"y":4288,"z":787,"timestamp":4117,"k":108,"type":0},'
        #     '{"x":5139,"y":4727,"z":1246,"timestamp":4217,"k":88,"type":0},'
        #     '{"x":4044,"y":3620,"z":141,"timestamp":4319,"k":69,"type":0},'
        #     '{"x":5650,"y":5041,"z":1704,"timestamp":4420,"k":93,"type":0},'
        #     '{"x":6236,"y":5603,"z":2293,"timestamp":4522,"k":67,"type":0},'
        #     '{"x":4678,"y":4055,"z":728,"timestamp":4623,"k":125,"type":0},'
        #     '{"x":6124,"y":5524,"z":2174,"timestamp":4727,"k":101,"type":0},'
        #     '{"x":6221,"y":5257,"z":2719,"timestamp":5210,"k":125,"type":0},'
        #     '{"x":4586,"y":3622,"z":1084,"timestamp":5320,"k":117,"type":0},'
        #     '{"x":5294,"y":3945,"z":1682,"timestamp":10072,"k":102,"type":0},'
        #     '{"x":5163,"y":3840,"z":1565,"timestamp":10186,"k":81,"type":0},'
        #     '{"x":4709,"y":3248,"z":1571,"timestamp":10287,"k":123,"type":0},'
        #     '{"x":2593,"y":1099,"z":635,"timestamp":10387,"k":89,"type":0},'
        #     '{"x":4222,"y":2759,"z":2332,"timestamp":10487,"k":74,"type":0},'
        #     '{"x":1313,"y":-174,"z":70,"timestamp":10587,"k":64,"type":0},'
        #     '{"x":4585,"y":3162,"z":3587,"timestamp":10688,"k":80,"type":0},'
        #     '{"x":3527,"y":2126,"z":2555,"timestamp":10789,"k":61,"type":0},'
        #     '{"x":4165,"y":2734,"z":3237,"timestamp":10891,"k":64,"type":0},'
        #     '{"x":1293,"y":-149,"z":375,"timestamp":10992,"k":121,"type":0},'
        #     '{"x":2645,"y":1204,"z":1724,"timestamp":11280,"k":120,"type":0},'
        #     '{"x":4772,"y":3948,"z":3311,"timestamp":11382,"k":125,"type":0},'
        #     '{"x":6049,"y":6044,"z":3695,"timestamp":11482,"k":118,"type":0},'
        #     '{"x":2948,"y":3053,"z":471,"timestamp":11584,"k":82,"type":0},'
        #     '{"x":5033,"y":5155,"z":2298,"timestamp":11686,"k":79,"type":0},'
        #     '{"x":5504,"y":3967,"z":3882,"timestamp":11786,"k":97,"type":0},'
        #     '{"x":2741,"y":1325,"z":1653,"timestamp":11887,"k":122,"type":0},'
        #     '{"x":1513,"y":139,"z":437,"timestamp":11988,"k":102,"type":0},'
        #     '{"x":3273,"y":1776,"z":2267,"timestamp":12088,"k":71,"type":0},'
        #     '{"x":3771,"y":2263,"z":2775,"timestamp":12191,"k":107,"type":0},'
        #     '{"x":5543,"y":4044,"z":4589,"timestamp":12292,"k":124,"type":0},'
        #     '{"x":2928,"y":1428,"z":1977,"timestamp":12393,"k":123,"type":0},'
        #     '{"x":3175,"y":1675,"z":2224,"timestamp":12494,"k":74,"type":1},'
        #     '{"x":2683,"y":1190,"z":1734,"timestamp":12640,"k":64,"type":0}]'
        # ),
        # "dm_img_str": "V2ViR0wgMS4wIChPcGVuR0wgRVMgMi4wIENocm9taXVtKQ",
        # "dm_cover_img_str": (
        #     "QU5HTEUgKE5WSURJQSwgTlZJRElBIEdlRm9yY2UgUlRYIDMwNjAg"
        #     "TGFwdG9wIEdQVSAoMHgwMDAwMjU2MCkgRGlyZWN0M0QxMSB2c181XzAg"
        #     "cHNfNV8wLCBEM0QxMSlHb29nbGUgSW5jLiAoTlZJRElBKQ"
        # ),
        # "dm_img_inter": (
        #     '{"ds":[{"t":1,"c":"bmF2LXRhYl9faXRlbS10ZX","p":[887,43,789],"s":[72,184,200]}],'
        #     '"wh":[4040,3070,70],"of":[25,50,25]}'
        # ),
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
    host_mid = "436175352"

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

    # 第一页 offset 为空
    offset = ""

    data = get_dynamic_list(host_mid, offset, headers)

    if data:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        output_path = r"E:\PythonXiangmu\jsonPy\test.json"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)  # 确保目录存在
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 响应已成功保存至: {output_path}")


if __name__ == '__main__':
    main()