from Code.AnalyzeTheFile.analyzeTheFile import analyzeTheFile
from Code.User.getUserName import get_UserName


if __name__ == '__main__':
    # 转换评论，把评论写入到txt文件
    mid = input("请输入目标的UID:")
    UserName = get_UserName(mid)
    analyzeTheFile(mid, UserName)  # 提取评论写入txt文件
