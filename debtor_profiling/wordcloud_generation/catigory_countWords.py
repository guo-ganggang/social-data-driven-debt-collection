__author__ = 'GGG'
# -*- coding: UTF-8 -*-

import matplotlib.pyplot as pyplot
import matplotlib
import codecs
import os
import math
from itertools import islice

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def computeTF(inFilePath_1,inFilePath_2,outFilePath):
    words_static = {}
    with codecs.open(inFilePath_1, "rb", "utf-8") as input_file:
        for line in islice(input_file, 1, None):
            temp = line.strip().split(' ')
            for i in range(len(temp)):
                words_static[temp[i]]= words_static.get(temp[i], 0) + 1
    print len(words_static)
    words_tf = {}
    max_value = 0
    for key in words_static.keys():
        if words_static[key] >= max_value:
            max_value = words_static[key]
    print max_value

    for key in words_static.keys():
        words_tf[key] = words_static[key] / float(max_value)
    coumuteTFIDF(words_tf,inFilePath_2,outFilePath)

def computeIDF(inFilePath,word):
    line_total = 0
    find_line = 0
    with codecs.open(inFilePath, "rb", "utf-8") as input_file:
        for line in islice(input_file, 1, None):
            temp = line.strip().split(' ')
            if word in temp[0:]:
                find_line += 1
            line_total += 1
    idf = math.log(float(line_total) / (find_line+1))
    return idf


def coumuteTFIDF(words_tf,inFilePath,outFilePath):
    word_tfidf = {}
    for word in words_tf:
        idf = computeIDF(inFilePath,word)
        word_tfidf[word] = idf * words_tf[word]

    font = matplotlib.font_manager.FontProperties(fname='c:\\windows\\Fonts\\simsun.ttc')

    word_tfidf_sorted = sorted(word_tfidf.iteritems(), key=lambda d: d[1], reverse=True)
    with codecs.open(outFilePath, "a+", "utf-8") as output_file:
        for i in range(1200):
            print word_tfidf_sorted[i][0],word_tfidf_sorted[i][1]
            output_file.write(word_tfidf_sorted[i][0] + "," + str(word_tfidf_sorted[i][1]) + "\n")
    #print '-------------','show' + Num +'barChat'
    bar_width = 0.35
    pyplot.bar(range(60), [word_tfidf_sorted[i][1] for i in range(60)],bar_width)
    pyplot.xticks(range(60), [word_tfidf_sorted[i][0] for i in range(60)], fontproperties=font,rotation=30)
    pyplot.title(u"WORDS FREQUENCY" + u"by GGG",fontproperties=font)
    pyplot.show()

if __name__ == '__main__':
    filePath = "D:\\pingan_stock\\pingan_stock_undervalueed\\stock_bbs\\"
    inPath_1 = filePath + "guangda_bbs_seg_clean_3words.csv"
    inPath_2 = filePath + "stock_bbs_post_seg_clean_3words.csv"
    outPath = filePath + "guangda_bbs_catigory_keywords_1200.csv"
    computeTF(inPath_1, inPath_2, outPath)



