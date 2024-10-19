"""
看情况选择是否配置IP代理池，不配置也能正常运行代码
如需要使用代理池，将proxies传入请求函数的proxies属性即可
我使用的是 巨量ip 的代理池服务，每天可以免费领取1000个IP
使用其他服务请参照服务商提供的Dome进行代理池配置
例:
    response = requests.get(url=URL, params=data, headers=headers, proxies=proxies)
"""

import requests


def getProxy():
    # 提取代理API接口，获取1个代理IP
    api_url = "在此处填写生成的代理链接"

    # 获取API接口返回的代理IP
    proxy_ip = requests.get(api_url)

    proxy_ip = proxy_ip.json()
    ip_list = proxy_ip['data']['proxy_list']
    ip = ip_list[0]

    # 用户名密码认证(动态代理/独享代理)
    username = "用户名"
    password = "用户密码"
    proxies = {
        "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": ip},
    }
    return proxies
