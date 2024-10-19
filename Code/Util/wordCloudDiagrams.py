from wordcloud import WordCloud
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

# 定义创建词云的函数
def create_wordcloud(data, background_image_path):
    font_path = "C:\Windows\WinSxS\\amd64_microsoft-windows-font-truetype-simhei_31bf3856ad364e35_10.0.22621.1_none_55bd821267d31393\simhei.ttf"
    # 打开背景图片
    background_image = Image.open(background_image_path).convert("RGBA")

    # 将背景图片转换为 numpy 数组
    background_array = np.array(background_image)

    # 创建 WordCloud 对象，设置词云图的宽、高、背景颜色、停用词、最小字体大小，并从词频数据生成词云
    wordcloud = WordCloud(width=1000, height=1000, background_color=None, mode="RGBA",
                           min_font_size=10, mask=background_array,font_path=font_path).generate_from_frequencies(data)

    # 创建图像窗口，设置图像大小
    plt.figure(figsize=(8, 8), facecolor=None)
    # 在图像窗口中显示词云图
    plt.imshow(wordcloud, interpolation='bilinear')
    # 不显示坐标轴
    plt.axis("off")
    # 调整布局
    plt.tight_layout(pad=0)
    return wordcloud



