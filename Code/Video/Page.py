import time

from Code.Video import BaseVideoList


def get_VideoPage(mid):  # 获取到视频一共有多少页
    while True:
        json_data = BaseVideoList.requests_video(mid,1)
        print(json_data)
        if json_data['code'] == -799:
            print("请求过于频繁，程序将沉睡1秒,当前执行方法为——获取视频页数——get_VideoPage")
            time.sleep(1)
            continue
        if json_data['code'] == 0:
            count = int(json_data['data']['page']['count'])
            page = (count + 30 - 1) // 30
            return page
        if json_data['code'] == -412:
            print("请求被拦截，当前使用的IP已经被拉黑，请更换IP")
            return None
