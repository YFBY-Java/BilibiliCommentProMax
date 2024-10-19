import csv


def readVideoList(UserName,mid):
    videoList = []
    with open(f"资源列表/视频列表/{UserName}/{mid}.csv", 'r') as file:
        reader = csv.reader(file)
        next(reader)  # 跳过表头
        for row in reader:
            first_column = row[0]
            videoList.append(first_column)
    return videoList