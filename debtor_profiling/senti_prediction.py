#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 18/10/2016 8:21 PM
# @Author  : GUO Ganggang
# @email   : ganggangguo@csu.edu.cn
# @Site    : 
# @File    : senti_prediction.py
# @Software: PyCharm

from __future__ import division
import graphlab as gl
import codecs
from itertools import islice
from gensim import utils
from os import listdir
import gensim


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

gl.set_runtime_config('GRAPHLAB_DEFAULT_NUM_PYLAMBDA_WORKERS', 32)

def clean_segData(inFilePath,outFilePath,k,clean_list):
    values = set()
    with codecs.open(outFilePath, "w", "utf-8") as output_file:
        with codecs.open(inFilePath, "rb", "utf-8") as inputStockCode:
            for line in inputStockCode:
                temp = line.strip().split(' ')
                # uid  = temp[0]
                # text = temp[1]
                #temp2 = text.strip().split(' ')
                clean_temp = []
                for i in range(len(temp)):
                    if temp[i] in clean_list:
                        #print temp[i]
                        continue
                    else:
                        clean_temp.append(temp[i])
                lenth = len(clean_temp)
                vec = " ".join(clean_temp[0:])
                #print lenth
                if lenth >= k:
                    if vec in values:
                        continue
                    else:
                        output_file.write(vec + '\n')
                        values.add(vec)
                    #output_file.write(vec + '\n')
                # elif lenth < k:
                #     print lenth,k
                #     print vec


def build_w2v_Vector(w2v_model_path,inputFile,opath,outFile_head):
    model = gensim.models.Word2Vec.load_word2vec_format(w2v_model_path, binary=False)
    with open(opath, 'a+') as output_file:
        output_file.write(outFile_head)
        with codecs.open(inputFile, "rb", "utf-8") as infile:
            for line in islice(infile.readlines(), 1, None):
                temp = line.strip().split("\t")
                phone = temp[0]
                text_seg = temp[1].strip().split(" ")
                words_vec_initi = []
                for i in range(400):
                    words_vec_initi.append(0.0)
                for j in range(len(text_seg)):
                    try:
                        words_vec_new = model[utils.to_unicode(text_seg[j])]
                    except:
                        print text_seg[j]
                        continue
                    words_vec = list(map(lambda x: x[0] + x[1], zip(words_vec_initi, words_vec_new)))
                    words_vec_initi = words_vec

                text_vec = " ".join(str(v) for v in words_vec_initi)
                text_seg = ' '.join(text_seg[0:])
                output_file.write(phone + ',' + text_seg + ',' + text_vec + '\n')


def build_LDA_vec(lda_model_path,inFilePath,predict_data_field,lda_result_output_path):
    weibo_LDA_model = gl.load_model(lda_model_path)
    predict_data = gl.SFrame.read_csv(inFilePath,delimiter = ",",header = True)
    predict_bag = gl.text_analytics.count_words(predict_data[predict_data_field])
    predict_data["LDA_topic"] = weibo_LDA_model.predict(predict_bag)
    predict_data['LDA_topic_probability'] = weibo_LDA_model.predict(predict_bag, output_type='probability')
    predict_data.save(lda_result_output_path,format='csv')


def weibo_senti_prediction(filePath,features,target):
    inpath = filePath + "senti_6class\\word2vec_ldaFeature\\senti_train_data_word2vec-2-400_lda_feature_4class_v3.csv"
    train_file = gl.SFrame.read_csv(inpath, delimiter=",", header=True)
    accu_list = []
    pre_list = []
    rec_list = []
    f1_list = []
    validation_outfile = filePath + "senti_6class\\prediction_results\\validation_outfile_lda_w2v-2-400_4class.csv"
    with codecs.open(validation_outfile, "a+", "utf-8") as output_handler:
        #output_handler.write("Features: " + " ".join(features) + "\n")
        iteration = 0
        for i in range(1, 20):
            fraction_list = [0.7, 0.8]
            for fraction in fraction_list:
                iteration += 1
                # data_zero = train_file[train_file[target] == 0]
                data_one = train_file[train_file[target] == 1]
                data_two = train_file[train_file[target] == 2]
                data_three = train_file[train_file[target] == 3]
                data_four = train_file[train_file[target] == 4]
                # data_five = train_file[train_file[target] == 5]
                # data_six = train_file[train_file[target] == 6]

                # train_data_0, test_data_0 = data_one.random_split(fraction)
                train_data_1, test_data_1 = data_one.random_split(fraction)
                train_data_2, test_data_2 = data_two.random_split(fraction)
                train_data_3, test_data_3 = data_three.random_split(fraction)
                train_data_4, test_data_4 = data_four.random_split(fraction)
                # train_data_5, test_data_5 = data_five.random_split(fraction)
                # train_data_6, test_data_6 = data_six.random_split(fraction)

                test_data = test_data_1.append(test_data_2).append(test_data_3) \
                    .append(test_data_4) #.append(test_data_5).append(test_data_6)

                train_data = train_data_1.append(train_data_2).append(train_data_3) \
                    .append(train_data_4) # .append(train_data_5).append(train_data_6)

                test_data = test_data.dropna()
                train_data = train_data.dropna()
                print "length of train_data:    %s and length of test_data: %s" % (len(train_data), len(test_data))

                # lg_model = gl.logistic_classifier.create(train_data, target=target, features=features,l2_penalty=0.001, \
                #                                           class_weights='auto', max_iterations=200)

                # lg_model = gl.random_forest_classifier.create(train_data, target=target, features=features, \
                #                                               class_weights='auto', max_iterations=200)

                lg_model = gl.boosted_trees_classifier.create(train_data, target=target, features=features, \
                                                              class_weights='auto', max_iterations=200)

                classifier = lg_model.classify(test_data)

                test_data["classify_probability"] = classifier["probability"]
                test_data["classify_class"] = classifier["class"]

                results = lg_model.evaluate(test_data)
                accu_list.append(results['accuracy'])
                pre_list.append(results['precision'])
                rec_list.append(results['recall'])
                f1_list.append(results['f1_score'])

                output_handler.write("Accuracy         :%s" % results['accuracy'] + "\n")
                output_handler.write("precision         :%s" % results['precision'] + "\n")
                output_handler.write("recall         :%s" % results['recall'] + "\n")
                output_handler.write("f1_score         :%s" % results['f1_score'] + "\n")
                output_handler.write("Confusion Matrix :%s" % results['confusion_matrix'] + "\n")

        total_accu = reduce(lambda x, y: x + y, accu_list)
        total_pre = reduce(lambda x, y: x + y, pre_list)
        total_rec = reduce(lambda x, y: x + y, rec_list)
        total_f1 = reduce(lambda x, y: x + y, f1_list)

        oFile = filePath + "senti_6class\\prediction_results\\EvaluateResult_lda_w2v-2-400_4class.txt"
        with codecs.open(oFile, "a+", "utf-8") as oFile_handler:
            oFile_handler.write(str(float(total_accu) / iteration) \
                                + '\t' + str(float(total_pre) / iteration) + '\t' + str(float(total_rec) / iteration) \
                                + '\t' + str(float(total_f1) / iteration) \
                                + '\n')


def weibo_senti_label(model_train_data_path,predict_data_path, features,target,result_output_path):
    # 训练模型
    train_data = gl.SFrame.read_csv(model_train_data_path, delimiter=",", header=True)
    train_data = train_data.dropna()
    # lg_model = gl.logistic_classifier.create(train_data, target=target, features=features, l2_penalty=0.001,\
    #                                          class_weights='auto', max_iterations=200)

    # lg_model = gl.random_forest_classifier.create(train_data, target=target, features=features,class_weights='auto', \
    #                                               max_iterations=200)

    bt_model = gl.boosted_trees_classifier.create(train_data, target=target, features=features, \
                                                  class_weights='auto', max_iterations=200)

    # 预测并保存情感标签
    predict_data = gl.SFrame.read_csv(predict_data_path, delimiter=",", header=True)
    predict_data = predict_data.dropna()
    classifier = bt_model.classify(predict_data)
    predict_data["senti_classify_probability"] = classifier["probability"]
    predict_data["senti_classify_class"] = classifier["class"]
    predict_data.save(result_output_path,format='csv')


def staticSentiByUser(inputPath,outputPath):
    # 获取字典类型uid 与情感分类列表
    phones = set()
    with codecs.open(inputPath, "rb", "utf-8") as inputfile:
        for line in islice(inputfile.readlines(), 1, None):
            temp = line.strip().split(',')
            phones.add(temp[0])
    print len(phones)

    # 统计后写入文件
    with codecs.open(outputPath, "w", "utf-8") as output_handler:
        output_handler.write('phone' + ',' + 'angry' + ',' + 'joyful' + ',' + 'sad' + ',' + 'scared' + '\n')
        for phone in phones:
            senti_class_static = {}
            for i in range(4):
                senti_class_static[str(i)] = 1
            sum = 4
            with codecs.open(inputPath, "rb", "utf-8") as inputfile:
                for line in islice(inputfile.readlines(), 1, None):
                    temp = line.strip().split(',')
                    if temp[0] == phone:
                        sum += 1
                        senti_class_static[temp[6]] = senti_class_static.get(temp[6], 0) + 1
            print senti_class_static['1'],senti_class_static['2'],senti_class_static['3'],senti_class_static['4']
            angry_ratio = round((senti_class_static['1'] / float(sum)), 2)
            joyful_ratio = round((senti_class_static['2'] / float(sum)), 2)
            sad_ratio = round((senti_class_static['3'] / float(sum)), 2)
            scared_ratio = round((senti_class_static['4'] / float(sum)), 2)

            output_handler.write(  \
                str(phone) + ',' + str(angry_ratio) + ',' + str(joyful_ratio) + \
                ',' + str(sad_ratio) + ',' + str(scared_ratio) + '\n')


if __name__ == "__main__":
    # 清理分词后的文本数据
    # filePath = 'D:\\incomeLevelPrediction\\db_file\\senti_6class\\senti_train_data_7class\\'
    # k = 1
    # clean_list = ['.1', '.2', '.3', '.4', '.5', '.6', '.7', '.8', '.9', '.10', "'''", "''", \
    #               '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.', '．', '……', \
    #               '＂', '／', '〜', '•', '➊', '➋', '➌', '➍', '➎', '➏', '﹑', '´', '＼', \
    #               '1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月', \
    #               # '一件', '一只', '一辆', '[转载]', '一句', '一下','一位', \
    #               # '链接', '网页', '中国','ヽ','｀', '一个', '一起', '一定','一次','一种','一直','一部', '－', \
    #               '....', '.....', '......', '……', '➠', '........................', '➕', '••••••', '•••']
    # # for i in range(6):
    # inFilePath = filePath + 'surprized_seg.csv'
    # outFilePath = filePath + 'surprized_seg_clean_3words.csv'
    # clean_segData(inFilePath, outFilePath, k, clean_list)

    # 构建word2vec特征
    # fpath = "D:\\incomeLevelPrediction\\db_file\\"
    fpath = "D:\\incomeLevelPrediction\\db_file\\"
    filePath = "D:\\yongxiong\\test_data\\"
    modelpath = fpath + "w2v_model_clean_Kwords\\3words_w2v_sg0_size400_minCount2_sample1e-4\\all_uid_text_3words.vector"
    ipath = filePath + "weibo_uid_ugc_seg_clean_3words.csv"
    opath = filePath + "weibo_uid_ugc_seg_clean_3words_w2v.csv"
    outFile_head = 'phone' + ',' + 'text_seg' + ',' + 'w2v_vec'  + '\n'
    #
    build_w2v_Vector(modelpath,ipath, opath,outFile_head)

    # 构建LDA特征
    # filePath = "D:\\incomeLevelPrediction\\db_file\\"
    # modelFilePath = filePath + "LDA_model_clean_Kwords\\all_weibo_3_LDA_model"
    # infilePath = filePath + "zhongxing_weibo_uid_seg_clean_3words_w2v.csv"
    # predict_data_field = "text_seg"
    # predict_field_output_file = filePath + "zhongxing_weibo_uid_seg_clean_3words_w2v_lda.csv"
    # build_LDA_vec(modelFilePath, infilePath, predict_data_field, predict_field_output_file)

    modelFilePath = fpath + "LDA_model_clean_Kwords\\all_weibo_3_LDA_model"
    infilePath = filePath + "weibo_uid_ugc_seg_clean_3words_w2v.csv"
    predict_data_field = "text_seg"
    predict_field_output_file = filePath + "weibo_uid_ugc_seg_clean_3words_w2v_lda.csv"
    build_LDA_vec(modelFilePath, infilePath, predict_data_field, predict_field_output_file)


    # 情感倾向预测
    # 'angry': 1, 'dislike': 2, 'joyful': 3, 'sad': 4, 'scared': 5, 'surprized': 6
    # model_train_data_path = file_path + "senti_6class\\word2vec_ldaFeature\\senti_train_data_word2vec-2-400_lda_feature_4class_v4.csv"
    # predict_data_path = file_path + "zhongxing_weibo_uid_seg_clean_3words_w2v_lda.csv"
    # result_output_path = file_path + "zhongxing_weibo_uid_seg_clean_3words_w2v_lda_sentiValue.csv"
    # features = ['w2v_vec','LDA_topic_probability','LDA_topic'] #,'LDA_topic_probability'
    # target = 'income_level_flag'
    # weibo_senti_label(model_train_data_path, predict_data_path, features, target, result_output_path)

    model_train_data_path = fpath + "senti_6class\\word2vec_ldaFeature\\senti_train_data_word2vec-2-400_lda_feature_4class_v4.csv"
    predict_data_path = filePath + "weibo_uid_ugc_seg_clean_3words_w2v_lda.csv"
    result_output_path = filePath + "weibo_uid_ugc_seg_clean_3words_w2v_lda_sentiValue.csv"
    features = ['w2v_vec','LDA_topic_probability','LDA_topic'] #,'LDA_topic_probability'
    target = 'income_level_flag'
    weibo_senti_label(model_train_data_path, predict_data_path, features, target, result_output_path)


    # 模型评价
    # 'angry': 1, 'dislike': 2, 'joyful': 3, 'sad': 4, 'scared': 5, 'surprized': 6
    # file_path = "D:\\incomeLevelPrediction\\db_file\\"
    # features = ['w2v_vec','LDA_topic_probability'] #,'LDA_topic_probability'
    # target = 'income_level_flag'
    # weibo_senti_prediction(file_path, features, target)

    # 统计
    # filePath = "D:\\yongxiong\\zhongxing_data\\3_train_data_features_target\\sentiment_classifier_feature\\"

    infilePath = filePath + 'weibo_uid_ugc_seg_clean_3words_w2v_lda_sentiValue.csv'
    outputPath = filePath + 'weibo_uid_ugc_seg_clean_3words_w2v_lda_sentiValue_static.csv'
    staticSentiByUser(infilePath, outputPath)
