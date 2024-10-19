import csv
import os
from io import StringIO
from Code.Util.readVideoList import readVideoList


def analyzeTheFile(mid, UserName):
    # mid = input("请输入目标的UID:")

    if not os.path.exists(f"资源列表/分析结果/{UserName}"):
        os.makedirs(f"资源列表/分析结果/{UserName}")
    videoList = readVideoList(UserName, mid)
    for video in videoList:
        commentsList = []
        read_fileName = video + ".csv"
        write_fileName = video + ".txt"
        # print(read_fileName)
        try:
            with open(f"资源列表/评论列表/{UserName}/{read_fileName}", mode='r', encoding='gbk', errors='ignore') as f:
                # 读取文件内容
                content = f.read()
                # 替换或删除 NUL 字符
                content = content.replace('\0', '')  # 将 NUL 字符替换为空字符串
                # 使用 StringIO 将处理后的内容传递给 csv.reader
                reader = csv.reader(StringIO(content))
                next(reader)  # 跳过表头
                for row in reader:
                    # if row:
                    first_column = row[9]  # 获取第一列
                    commentsList.append(first_column)
            if not os.path.exists(f"资源列表/分析列表/{UserName}"):
                os.makedirs(f"资源列表/分析列表/{UserName}")
            with open(f"资源列表/分析列表/{UserName}/{write_fileName}", mode='w', encoding='utf-8',
                      errors='ignore') as f:
                f.write("\n".join(commentsList))
        except:
            print("读取文件失败")
    print("文件写入完成")
