#!/usr/bin/python
# -*- coding=utf-8 -*-
import gensim
from sklearn.cluster import spectral_clustering
#import pandas as pd
import numpy as np
import codecs
import sys
from gensim import utils
reload(sys)
sys.setdefaultencoding('utf-8')

def accumulation_w2v(model_ipath,inFilePath,outFilePath):
    model = gensim.models.Word2Vec.load_word2vec_format(model_ipath, binary=False)

    contracts = set()
    with codecs.open(inFilePath, "rb", "utf-8") as inputfile:
        for line in inputfile.readlines():
            temp = line.strip().split('\t')
            contracts.add(temp[0])
    print "The Number of the contracts: " + str(len(contracts))

    with open(outFilePath, 'w') as output_file:
        for contract in contracts:
            inint_list = []
            for j in range(400):
                inint_list.append(0.0)
            with codecs.open(inFilePath, "rb", "utf-8") as inputfile:
                for line in inputfile.readlines():
                    temp = line.strip().split('\t')
                    if temp[0] == contract:
                        temp_words = temp[1].strip().split(' ')
                        for k in range(len(temp_words)):
                            char = utils.to_unicode(temp_words[k])
                            # if u'\u4e00' <= char <= u'\u9fff':
                            # print temp_3[j]
                            try:
                                temp_list = model[char]
                            except KeyError:
                                continue
                            else:
                                print "Unexpected error:", sys.exc_info()[0]
                            inint_list = list(map(lambda x: x[0] + x[1], zip(inint_list, temp_list)))
                    else:
                        continue

            final_list = ','.join(str(v) for v in inint_list)
            output_file.write(contract + ',' + final_list + '\n')


if __name__ == "__main__":
    fpath = "D:\\incomeLevelPrediction\\db_file\\w2v_model_clean_Kwords\\3words_w2v_sg0_size400_minCount2_sample1e-4\\"
    #ipath = fpath + "3words_w2v_sg0_size800_minCount5_sample1e-4\all_uid_text_3words.vector"
    ipath = fpath + "all_uid_text_3words.vector"
    # opath = "similarity_vector_v2.csv"
    # model = gensim.models.Word2Vec.load_word2vec_format(ipath, binary=False)
    # results = model.most_similar(u"开心",topn=100)
    # for e in results:
    #     print e[0], e[1]
    # print model[u"开心"]
    # similarityResults = model.similarity(u'锻炼',u'健康')
    # print similarityResults
    #spectral = spectral_clustering(model, n_cluster
    inFilePath = "D:\\yongxiong\\zhongxing_data\\zhongxing_weibo_train_seg_clean_1words.csv"
    outFilePath = "D:\\yongxiong\\zhongxing_data\\zhongxing_weibo_train_w2v_features.csv"
    accumulation_w2v(ipath, inFilePath, outFilePath)