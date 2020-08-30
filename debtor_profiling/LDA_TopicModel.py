#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 30/9/2016 8:41 PM
# @Author  : GUO Ganggang
# @email   : ganggangguo@csu.edu.cn
# @Site    :
# @File    : obtain_train_data.py
# @Software: PyCharm

import graphlab as gl
import codecs
import numpy as np
from itertools import islice


class TopicModel:
    def trainModel(self, trained_file, train_field, model_saved_name, num_topics, num_iterations, method='auto',
                   beta=0.01, delimiter="\t"):
        train_data = gl.SFrame.read_csv(trained_file, delimiter, header=True)
        print train_data
        train_bag = gl.text_analytics.count_words(train_data[train_field])
        train_model = gl.topic_model.create(train_bag, num_topics=num_topics, num_iterations=num_iterations, beta=beta,
                                            method=method, verbose=True)
        train_model.save(model_saved_name)
        return train_model
    # def predict(self,train_model,test_file,test_field,test_result_field,test_output_file,delimiter = " "):
    #     test_data = gl.SFrame.read_csv(test_file,delimiter = delimiter,header = True)
    #     test_bag = gl.text_analytics.count_words(test_data[test_field])
    #     test_data[test_result_field] = train_model.predict(test_bag)
    #     test_data.save(test_output_file)


def dealwithData(inFilePath,outFilePath):
    with codecs.open(outFilePath, "w", "utf-8") as output_file:
        output_file.write('uid' + '\t' + 'text' + '\n')
        with codecs.open(inFilePath, "rb", "utf-8") as inHandle:
            for line in inHandle:
                temp = line.strip().split(' ')
                uid = temp[0]
                text = " ".join(temp[1:])
                output_file.write(uid + '\t' + text + '\n')

def showLDAtopicSep(input_file,output_file):
    weibo_model = gl.load_model(input_file)
    topics_words = weibo_model.get_topics(num_words=200, output_type='topic_words')
    topics_words.save(output_file)


def prediction_weibo_LDA(prediction_model_filePath,data_filepath,output_filepath):

    weibo_LDA_model = gl.load_model(prediction_model_filePath)

    weibo_train_data = gl.SFrame.read_csv(data_filepath, delimiter="\t", header=True)
    weibo_model_bag = gl.text_analytics.count_words(weibo_train_data['text'])

    weibo_train_data ['weibo_topic'] = weibo_LDA_model.predict(weibo_model_bag)
    weibo_train_data['weibo_topic_probability'] = weibo_LDA_model.predict(weibo_model_bag, output_type='probability')

    weibo_train_data.remove_column('text')
    weibo_train_data.save(output_filepath)



# 按uid 对每位用户的每条微博的主题进行统计,并根据各个主题出现次数多少，输出前5个
def static_LDATopic(input_path,output_path):

    with codecs.open(input_path, "rb", "utf-8") as input_file:
        phones = set()
        for line in islice(input_file.readlines(), 1, None):
            temp = line.strip().split(',')
            phones.add(temp[0])

    phone_topics = {}
    for phone in phones:
        topics = []
        with codecs.open(input_path, "rb", "utf-8") as input_file:
            for line in islice(input_file.readlines(), 1, None):
                temp = line.strip().split(',')
                if temp[0] == phone:
                    topics.append(temp[1])
        print topics
        phone_topics[phone] = topics

    print len(phone_topics)

    phone_sorted_3topics = {}
    phone_sorted_3topics_num = {}
    for key in phone_topics.keys():
        static_num = {}
        sorted_topics = []
        sorted_topics_num = []
        for i in range(len(phone_topics[key])):
            if phone_topics[key][i] not in static_num.keys():
                static_num[phone_topics[key][i]] = 1
            else:
                static_num[phone_topics[key][i]] += 1
        # for key_sta in static_num.keys():
        #     print key_sta,static_num[key_sta]

        lda_sort = sorted(static_num.iteritems(), key=lambda d: d[1], reverse=True)
        for j in range(10):
            # print lda_sort[j][0],lda_sort[j][1]
            sorted_topics.append(lda_sort[j][0])
            sorted_topics_num.append(lda_sort[j][1])
        phone_sorted_3topics[key] = sorted_topics
        phone_sorted_3topics_num[key] = sorted_topics_num


    with codecs.open(output_path, "w", "utf-8") as output_handler:
        for key_pho in phone_sorted_3topics:
            print key_pho, phone_sorted_3topics[key_pho]
            topics_3sort_str = ','.join(phone_sorted_3topics[key_pho])
            topics_3sort_num_str = ','.join([str(value) for value in phone_sorted_3topics_num[key_pho]])
            output_handler.write(str(key_pho) + ','+ topics_3sort_str + '\n')
            output_handler.write('times'+ ','+ topics_3sort_num_str + '\n')


if __name__ == "__main__":

    # dealwithData(inFilePath, outFilePath)
    # filePath = 'D:\\incomeLevelPrediction\\db_file\\'
    # #filePath = 'D:\yongxiong\zhongxing_data'
    # train_file = filePath + 'all_seg_data_clean_Kwords\\merge_headerTrue_all_uid_text_clean_than20_v2.csv'
    # train_field = 'text'
    # model_saved_name = filePath + 'LDA_model_clean_Kwords\\all_uid_text_clean_than20_merge'
    # topic_model = TopicModel()
    # train_model = topic_model.trainModel(train_file,train_field,model_saved_name,num_topics = 250,num_iterations = 1500)
    # print train_model.get_topics()


    # filePath = 'D:\\incomeLevelPrediction\\db_file\\'
    # input_file = filePath + 'LDA_model_clean_Kwords\\all_weibo_7_LDA_model'
    # output_file = filePath + 'qualitative_analysis\\show_all_weibo_7_LDA_model_topics.csv'
    #
    # showLDAtopicSep(input_file,output_file)

    # prediction_model_filePath = 'D:\\incomeLevelPrediction\\db_file\\LDA_model_clean_Kwords\\all_weibo_3_LDA_model\\'
    # data_filepath = 'D:\\yongxiong\\zhongxing_data\\zhongxing_weibo_uid_weibo_LDA_train_seg_clean_3words.csv'
    # output_filepath = 'D:\\yongxiong\\zhongxing_data\\zhongxing_weibo_3words_LDA_result.csv'
    # data_filepath = 'D:\\yongxiong\\test_data\\weibo_uid_ugc_seg_clean_3words.csv'
    # output_filepath = 'D:\\yongxiong\\test_data\\weibo_uid_ugc_seg_clean_3words_LDA.csv'
    # prediction_weibo_LDA(prediction_model_filePath, data_filepath, output_filepath)

    # filePath = 'D:\\yongxiong\\zhongxing_data\\'
    # input_path = filePath + 'zhongxing_weibo_3words_LDA_result.csv'
    # output_path = filePath + 'zhongxing_weibo_3words_LDA_result_static.csv'

    filePath = 'D:\\yongxiong\\test_data\\'
    input_path = filePath + 'weibo_uid_ugc_seg_clean_1words_LDA.csv'
    output_path = filePath + 'weibo_uid_ugc_seg_clean_1words_LDA_static.csv'
    static_LDATopic(input_path, output_path)


