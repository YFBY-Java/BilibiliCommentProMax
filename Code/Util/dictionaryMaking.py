import csv
import os
from io import StringIO

def dictionaryMaking(Name):
    # 获取当前文件的绝对路径
    current_file_path = os.path.abspath(__file__)
    # 向上回退三级
    parent_directory = os.path.abspath(os.path.join(current_file_path, os.pardir, os.pardir, os.pardir))

    folder_path = f"{parent_directory}\\资源列表\\原始词库\\{Name}"
    # 使用 with 语句打开文件夹
    with os.scandir(folder_path) as entries:
        file_list = [entry.name for entry in entries if entry.is_file()]
    print("文件列表:")
    print(file_list)
    commentsList = []
    for i in file_list:
        with open(f"{folder_path}/{i}", mode='r', encoding='utf-8', errors='ignore') as f:
            # 读取文件内容
            content = f.read()
            # 替换或删除 NUL 字符
            content = content.replace('\0', '')  # 将 NUL 字符替换为空字符串
            # 使用 StringIO 将处理后的内容传递给 csv.reader
            reader = csv.reader(StringIO(content))
            next(reader)  # 跳过表头
            for row in reader:
                # if row:
                first_column = row[0]  # 获取第一列
                if first_column not in commentsList:
                    commentsList.append(first_column)
        with open(f"{parent_directory}\\资源列表\\词典\\{Name}.txt", mode='w', encoding='utf-8',
                  errors='ignore') as f:
            f.write("\n".join(commentsList))


if __name__ == '__main__':
    # 参数换为你要转换的字典名  去原始词库目录找
    dictionaryMaking("崩坏星穹铁道")
