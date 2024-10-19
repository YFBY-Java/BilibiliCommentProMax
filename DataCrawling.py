import concurrent.futures
import csv
import os
import time
from Code.Comment.getComment import download_comment
from Code.User import getUserName
from Code.Video import Page
from Code.Video.getVideoList import get_VideoList


if __name__ == '__main__':
    start_time = time.time()
    Cookie = "i-wanna-go-back=-1; nostalgia_conf=-1; hit-new-style-dyn=1; CURRENT_PID=4cd3f370-cfc1-11ed-a1ba-1bd0ab9c9f37; LIVE_BUVID=AUTO4216806977265660; rpdid=|(umYR)Jukm)0J'uY)JYJ|)|l; b_ut=5; buvid3=48D1EA68-20C7-F241-B6A8-0B1F39D8B56B13158infoc; b_nut=1696428813; _uuid=28DF73B1-AD1E-610106-310FD-1063103105B8FFB14254infoc; header_theme_version=CLOSE; is-2022-channel=1; CURRENT_QUALITY=80; DedeUserID=3493298050173740; DedeUserID__ckMd5=2400b6c0cbc038ab; enable_web_push=DISABLE; buvid4=BC583ED0-3589-BDBB-0B49-54DA9CBC48F314270-023100422-JSpXaFEgPSzR5HIIuGldng%3D%3D; buvid_fp_plain=undefined; hit-dyn-v2=1; CURRENT_FNVAL=4048; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDQzODE1MTIsImlhdCI6MTcwNDEyMjI1MiwicGx0IjotMX0.i8DMmNLtVY5k6xPjZWk4eHcwCPoOkevfTgBDGTgyJOA; bili_ticket_expires=1704381452; home_feed_column=5; browser_resolution=1545-828; SESSDATA=f7598175%2C1719825637%2C0146b%2A11CjDSU0v_vZ0OzWu3WxrdmC-1VsZeEE8S4vdusPcNeI4UOC1Yo1nSs4N-QbNp4BTuaDkSVmtTcG1UTVI1ZHl3S0gyVnZ3UHFENXUtSmdkUTlOcFhGX1hvbDdOM0I3S2VzSDlvMkRjR3I2Z0l5ZlBIX1JFcDlfd093T3RUQ3phV2pBTnBEYlJrMkdnIIEC; bili_jct=df4f804330ccc179090212d12eaef65e; sid=73tlvib6; b_lsid=44CCFC810_18CCEB54A2D; bp_video_offset_3493298050173740=882340360270905362; fingerprint=1aab5d25187ce9285680bb7c18e645c7; buvid_fp=48D1EA68-20C7-F241-B6A8-0B1F39D8B56B13158infoc; PVID=2"
    # Cookie = input("请输入从浏览器获取的Cookie:")
    mid = input("请输入要爬取用户的UID:")
    UserName = getUserName.get_UserName(mid)
    if UserName is None:
        # 结束程序
        exit()
    else:
        if not os.path.exists(f"资源列表/视频列表/{UserName}"):
            os.makedirs(f"资源列表/视频列表/{UserName}")
    file_name = mid + ".csv"
    with open(f"资源列表/视频列表/{UserName}/{file_name}", mode='w', encoding='gbk', newline='', errors='ignore') as f:
        # 在这里操作文件
        csv_writer = csv.DictWriter(f, fieldnames=[
            '视频BV号',
            '视频标题'
        ], quoting=csv.QUOTE_ALL)  # fieldnames 指定csv文件中的字段名 即表头
        csv_writer.writeheader()  # writeheader() 写入表头
        page = Page.get_VideoPage(mid)  #
        counter = 1
        while True:
            if counter > page:
                print("视频列表获取完毕")
                break
            get_VideoList(mid, counter, csv_writer)
            counter = counter + 1
            # time.sleep(1)
    if not os.path.exists(f"资源列表/评论列表/{UserName}"):
        os.makedirs(f"资源列表/评论列表/{UserName}")
    videoList = []
    with open(f"资源列表/视频列表/{UserName}/{file_name}", 'r') as file:
        reader = csv.reader(file)
        next(reader)   # 跳过表头
        for row in reader:
            first_column = row[0]  # row[0] 获取第一列
            videoList.append(first_column)
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        # 使用线程池并行下载评论
        futures = [executor.submit(download_comment, Cookie, bv, UserName) for bv in videoList]
        # 等待所有任务完成
        concurrent.futures.wait(futures)
    print("该用户所有视频爬取完毕！")

    end_time = time.time()
    # 计算时长（秒）
    elapsed_time = end_time - start_time
    # 将时长转换为时分秒格式
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    # 输出结果
    formatted_time = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))
    print(f"程序执行时长：{formatted_time}")

