import time

from Code.Video import BaseVideoList


def get_VideoList(mid, counter, csv_writer):  # 获取当前页视频列表(BV号)
    while True:
        json_data = BaseVideoList.requests_video(mid,counter)
        print(json_data)
        code = json_data['code']
        if code == -799:
            print("请求过于频繁，程序将沉睡1秒，当前执行方法为——获取视频列表——get_VideoList")
            time.sleep(1)
            continue
        if code == 0:
            data = []
            vlist = json_data['data']['list']['vlist']
            if vlist:  # vlist不为空
                vlist_len = len(vlist)
                for i in range(0, vlist_len):
                    bvid = vlist[i]['bvid']
                    title = vlist[i]['title']

                    one_data = {
                        "视频BV号": bvid,
                        "视频标题": title
                    }
                    data.append(one_data)
                    csv_writer.writerow(one_data)
            return data
        if code == -412:
            print("请求被拦截，当前使用的IP已经被拉黑，请更换IP")
            return None

