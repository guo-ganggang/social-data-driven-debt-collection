#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 24/2/2017 下午 10:00
# @Author  : GUO Ganggang
# @email   : ganggangguo@csu.edu.cn
# @Site    : 
# @File    : wordcloud_generation.py
# @Software: PyCharm

from os import path
from scipy.misc import imread
import codecs
from os import listdir
import jieba.analyse
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import os
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# 获取当前文件路径
# __file__ 为当前文件, 在ide中运行此行会报错,可改为
# d = path.dirname('.')
d = path.dirname(__file__)

# 读取文本 alice.txt 在包文件的example目录下
#内容为
"""
Project Gutenberg's Alice's Adventures in Wonderland, by Lewis Carroll

This eBook is for the use of anyone anywhere at no cost and with
almost no restrictions whatsoever.  You may copy it, give it away or
re-use it under the terms of the Project Gutenberg License included
with this eBook or online at www.gutenberg.org
"""

def tf_idf(textFile):
    content = open(path.join(d, textFile)).read()
    # tags extraction based on TF-IDF algorithm
    jieba.analyse.set_stop_words("../wordcloud_generation/stop_words.txt")
    # 返回几个TF / IDF权重最大的关键词，默认值为 20
    tags = jieba.analyse.extract_tags(content, topK=100, withWeight=False)
    text =" ".join(tags)
    text = unicode(text)
    return text

def words_freq(textFile):
    text = open(path.join(d, textFile)).read()
    d2 = {}
    lines = text.strip().split('\n')
    for line in lines:
        line_words = line.strip().split(' ')
        for word in line_words:
            if word != '':
                d2[word] = d2.get(word, 0) + 1
    d2_sorted = sorted(d2.iteritems(), key=lambda d: d[1], reverse=True)
    d3 = []
    for i in range(22):
        print d2_sorted[i][0], d2_sorted[i][1]
        tuple_word_num = (unicode(d2_sorted[i][0]), d2_sorted[i][1])
        d3.append(tuple_word_num)
    return d3

def generate_person_wordcloud(textFile,picturesFile,gen_fileName,static_funciton):

    # read the mask / color image
    # taken from http://jirkavinse.deviantart.com/art/quot-Real-Life-quot-Alice-282261010
    # 设置背景图片
    alice_coloring = imread(path.join(d, "../wordcloud_generation/images/" + picturesFile))
    FONT_PATH = os.environ.get("FONT_PATH", os.path.join(os.path.dirname(__file__), "MSYH.TTC"))
    image_colors = ImageColorGenerator(alice_coloring)
    wc = WordCloud(font_path=FONT_PATH,
    background_color="white", #背景颜色
    max_words=200,# 词云显示的最大词数
    mask=alice_coloring,#设置背景图片
    color_func=image_colors,
    # stopwords=STOPWORDS.add("said"),
    max_font_size=40, #字体最大值
    random_state=42)
    # 生成词云, 可以用generate输入全部文本(中文不好分词),也可以我们计算好词频后使用generate_from_frequencies函数

    if static_funciton == 'freq':
        # 统计词频
        # txt_freq例子为[('词a', 100),('词b', 90),('词c', 80)]
        txt_freq = words_freq(textFile)
        wc.generate_from_frequencies(txt_freq)
    elif static_funciton == 'tf-idf':
        # 统计tf-idf
        text = tf_idf(textFile)
        wc.generate(text)
    else:
        text = open(path.join(d, textFile)).read()
        wc.generate(text)


    # 从背景图片生成颜色值
    # image_colors = ImageColorGenerator(alice_coloring)

    # 以下代码显示图片
    # plt.imshow(wc)
    # plt.axis("off")
    # 绘制词云
    # plt.figure()
    # recolor wordcloud and show
    # we could also give color_func=image_colors directly in the constructor
    # plt.imshow(wc.recolor(color_func=image_colors))
    # plt.axis("off")
    # 绘制背景图片为颜色的图片
    # plt.figure()
    # plt.imshow(alice_coloring, cmap=plt.cm.gray)
    # plt.axis("off")
    # plt.show()
    # 保存图片
    gen_fileName = re.sub('.csv', '',gen_fileName)
    wc.to_file(path.join(d, "../wordcloud_generation/user_profiles/stock_del_post_wordcloud/" +gen_fileName +".png"))

# 合并合并一定时间区间内的文本
def merge_data(ipath):

    infilePath = ipath + 'event_row_news_data_seg.csv'

    time_period = set()
    with codecs.open(infilePath, "rb", "utf-8") as inputfile:
        for line in inputfile:
            temp = line.strip().split('\t')
            if -10.0 < float(temp[1]) < 12.0:
                continue
            time_period.add(temp[0])
    print len(time_period)

    time_period_text = {}
    for date in time_period:
        text = set()
        score = ''
        with codecs.open(infilePath, "rb", "utf-8") as inputfile:
            for line in inputfile:
                temp = line.strip().split('\t')
                if temp[0] != date:
                    continue
                contect = ' '.join(temp[3:])
                text.add(contect)
                score = temp[1]
                # print score

        dates = date.strip().split(',')
        new_date = dates[0].strip().split(' ')[0] + '_' + dates[1].strip().split(' ')[0]
        id = new_date + '_' + score
        # print id
        time_period_text[id] = text

    for key in time_period_text.keys():
        texts = time_period_text[key]
        outFilePath = ipath + key.strip() +'.csv'
        with open(outFilePath, 'w') as output_file:
            for text in texts:
                output_file.write(text + '\n')


if __name__ == '__main__':

    # filepath = 'D:\\SMU_PROJECTS\\summary_reporting\\'
    # merge_data(filepath)

    filepath_f = '../wordcloud_generation/stock_del_post/'
    fileNameFeature_f = '.csv'
    fileNames = [f for f in listdir(filepath_f) if f.endswith(fileNameFeature_f)]

    filepath_p = '../wordcloud_generation/images/'
    # fileNameFeature_p = 'h'
    # imageNames = [f for f in listdir(filepath_p) if f.startswith(fileNameFeature_p)]
    imageName = 'person_4.jpg'

    # flag_i = 0
    #static_funciton 三个参数的意义 'freq' 分词后中文, 'english' 英文原文, 'tf-idf' 中文原文
    static_funciton ='tf-idf'

    for fileName in fileNames:
        print fileName
        generate_person_wordcloud(filepath_f + fileName, imageName,fileName,static_funciton) #imageNames[flag_i]
        # flag_i += 1

