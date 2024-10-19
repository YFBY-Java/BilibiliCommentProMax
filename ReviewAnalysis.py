import time
from collections import Counter

import jieba

from Code.User import getUserName
from Code.Util.readVideoList import readVideoList
from Code.Util.wordCloudDiagrams import create_wordcloud

if __name__ == '__main__':
    print("正在进行评论分析，请先确认目标在分析列表中")
    mid = input("请输入要分析用户UID：")
    start_time = time.time()
    filename = getUserName.get_UserName(mid)
    # 加载用户定义的词典文件
    jieba.load_userdict(f"资源列表/词典/{filename}.txt")

    with open(f"资源列表/词典/{filename}.txt", 'r', encoding='utf-8') as ignore_file:
        # 读取要忽略的词汇，并按行拆分成列表
        dictionary = ignore_file.read().splitlines()
        print(dictionary)

    videoList = readVideoList(filename, mid)
    # 初始化词频统计器
    word_counter = Counter()
    num = 1
    # 遍历视频列表
    for e in videoList:
        print(f"正在分析第{num}个视频")
        # 打开分析列表中的文件
        with open(f"资源列表/分析列表/{filename}/{e}.txt", mode='r', encoding='utf-8', errors='ignore') as f:
            # 使用 jieba 分词
            words = [word for word in jieba.cut(f.read()) if word in dictionary]
            # 更新词频统计
            word_counter.update(words)
        num = num+1


    # 获取出现次数最多的20个词及其出现次数
    top_words = word_counter.most_common(20)

    # 打印结果
    for word, count in top_words:
        print(f"{word}: {count} 次")

    background_image_path = "资源列表/词云图背景图/爱莉希雅.jpg"

    create_wordcloud(word_counter, background_image_path).to_file(f"资源列表/词云图生成结果/{filename}.png")

    end_time = time.time()
    # 计算时长（秒）
    elapsed_time = end_time - start_time
    # 将时长转换为时分秒格式
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    # 输出结果
    formatted_time = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))
    print(f"程序执行时长：{formatted_time}")
