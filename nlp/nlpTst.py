# -*- coding: utf-8 -*-
import jieba
import jieba.analyse
from os import path
from scipy.misc import imread
import matplotlib.pyplot as plt
from collections import Counter
from PIL import Image
import numpy as np
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

with open(path.join(path.dirname(__file__), 'dict//stopwords.txt'), 'r', encoding='utf-8') as f:
    STOPWORD = [word.strip() for word in f.readlines()]
d=path.dirname(__file__)

def generate_wordcloud(text):
    '''
    输入文本生成词云,如果是中文文本需要先进行分词处理
    '''
    # 设置显示方式
    alice_mask = np.array(Image.open(path.join(d, "image//money_pig_orange.jpg")))
    font_path=path.join(d,"font//ylq.ttf")
    stopwords = set(STOPWORDS)
    wc = WordCloud(background_color="white",# 设置背景颜色
           max_words=2000, # 词云显示的最大词数
           mask=alice_mask,# 设置背景图片
           stopwords=stopwords, # 设置停用词
           font_path=font_path, # 兼容中文字体，不然中文会显示乱码
                  )

    # 生成词云
    wc.generate(text)

    # 生成的词云图像保存到本地
    wc.to_file(path.join(d, "test.png"))

    # 显示图像
    #plt.imshow(wc, interpolation='bilinear')
    # interpolation='bilinear' 表示插值方法为双线性插值
    #plt.axis("off")# 关掉图像的坐标
    #plt.show()

def word_segment(text):
    '''
    通过jieba进行分词并通过空格分隔,返回分词后的结果
    '''
    # 计算每个词出现的频率，并存入txt文件
    jieba_word=jieba.cut(text,cut_all=False) # cut_all是分词模式，True是全模式，False是精准模式，默认False
    data=[]
    for word in jieba_word:
        if word not in STOPWORD:
            data.append(word)
    dataDict=Counter(data)
    with open('doc//词频统计.txt','w') as fw:
        for k,v in dataDict.items():
            fw.write("%s,%d\n" % (k,v))
        #  fw.write("%s"%dataDict)

    # 返回分词后的结果
    jieba_word = jieba.cut(text, cut_all=False)  # cut_all是分词模式，True是全模式，False是精准模式，默认False
    seg_list = ' '.join(jieba_word)
    print(seg_list.__len__())
    return seg_list

def main():

    with open(path.join(path.dirname(__file__), 'txt//2440868373_content.txt'), 'r', encoding='gbk', errors='ignore') as article:

        jieba.load_userdict(path.join(path.dirname(__file__), 'dict//userdict.txt'))  # 导入用户自定义词典
        jieba.add_word('宜信财富')
        #jieba.analyse.set_stop_words(path.join(path.dirname(__file__), 'dict//stopwords.txt'))#TF_IDF方式时使用
        #stopwords = [line.strip() for line in article.open('stoped.txt', 'r', 'utf-8').readlines()]
        #words = jieba.cut(article.read(),cut_all=False)
        ############################
        # 读取文件
        # text = open(path.join(path.dirname(__file__), 'txt//1774800467_content.txt'), 'r', encoding='gbk', errors='ignore').read()

        # 若是中文文本，则先进行分词操作
        text = word_segment(article.read())
        # 生成词云
        generate_wordcloud(text)

if __name__ == '__main__':
    main()