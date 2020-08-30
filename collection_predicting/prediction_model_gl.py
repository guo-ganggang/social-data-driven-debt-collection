#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19/02/2017 下午 10:25
# @Author  : GUO Ganggang
# @email   : ganggangguo@csu.edu.cn
# @Site    : 
# @File    : prediction_model_gl.py
# @Software: PyCharm

###########
## 采用随机深林和boosting tree 算法构建预测模型
## 采用graphlab机器学习库
###########


from __future__ import division
import graphlab as gl
import codecs
import sys
import os


class LeadsGenerationModel_Validation:
    def __init__(self,train_file,feature_portfolio,model,target,key,kfolds): #validation_outfile,
        self.train_file = train_file
        # self.validation_outfile =  validation_outfile
        self.feature_portfolio = feature_portfolio
        self.model = model
        self.target = target
        self.key = key
        self.kfolds = kfolds

    def validate(self):
        accu_list = []
        pre_list = []
        rec_list = []
        f1_list = []

        # with codecs.open(self.validation_outfile,"a+","utf-8") as output_handler:
        # output_handler.write("Features: " + " ".join(self.features) + "\n")
        # iteration = 0
        # for i in range(1,30):
        #     fraction_list = [0.7,0.8,0.9]
        #     for fraction in fraction_list:
        #         iteration += 1

        data_zero  = self.train_file[self.train_file[self.target] == 0]
        data_one   = self.train_file[self.train_file[self.target] == 1]
        data_two   = self.train_file[self.train_file[self.target] == 2]
        data_three = self.train_file[self.train_file[self.target] == 3]

        folds_zero = gl.cross_validation.KFold(data_zero, self.kfolds)
        folds_one = gl.cross_validation.KFold(data_one, self.kfolds)
        folds_two = gl.cross_validation.KFold(data_two, self.kfolds)
        folds_three = gl.cross_validation.KFold(data_three, self.kfolds)

        for i in range(self.kfolds):
            (train_data_0, test_data_0) = folds_zero[i]
            (train_data_1, test_data_1) = folds_one[i]
            (train_data_2, test_data_2) = folds_two[i]
            (train_data_3, test_data_3) = folds_three[i]

            test_data = test_data_0.append(test_data_1).append(test_data_2).append(test_data_3)
            train_data = train_data_0.append(train_data_1).append(train_data_2).append(train_data_3)

            test_data = test_data.dropna()
            train_data = train_data.dropna()
            print "length of train_data:    %s and length of test_data: %s" % (len(train_data),len(test_data))

            # net = gl.deeplearning.create(train_data, target=self.target)
            # model_dl = gl.neuralnet_classifier.create(train_data,
            #                                          target=self.target,
            #                                          network=net, max_iterations=700)
            # train_data['deep_features'] = model_dl.extract_features(train_data)
            # test_data['deep_features'] = model_dl.extract_features(test_data)
            #
            if self.model == 'BT_':
                BT_model = gl.boosted_trees_classifier.create(train_data, target=self.target, \
                                                              features=self.feature_portfolio, \
                                                   class_weights='auto', max_iterations=200)
                results = BT_model.evaluate(test_data)
            else:
                RF_model = gl.random_forest_classifier.create(train_data, target = self.target,features = self.feature_portfolio, \
                                                              class_weights='auto', max_iterations=200)
                results = RF_model.evaluate(test_data)

            accu_list.append(results['accuracy'])
            pre_list.append(results['precision'])
            rec_list.append(results['recall'])
            f1_list.append(results['f1_score'])

            # output_handler.write("Accuracy         :%s" % results['accuracy'] + "\n")
            # output_handler.write("precision         :%s" % results['precision'] + "\n")
            # output_handler.write("recall         :%s" % results['recall'] + "\n")
            # output_handler.write("f1_score         :%s" % results['f1_score'] + "\n")
            # output_handler.write("Confusion Matrix :%s" % results['confusion_matrix'] + "\n")

        total_accu = reduce(lambda x, y: x + y, accu_list)
        total_pre = reduce(lambda x, y: x + y, pre_list)
        total_rec = reduce(lambda x, y: x + y, rec_list)
        total_f1 = reduce(lambda x, y: x + y, f1_list)


        oFile = "D:\\yongxiong\\zhongxing_data\\train_data\\result_set\\" + str(self.model) + "result_zhongxing.csv"
        with codecs.open(oFile, "a+", "utf-8") as oFile_handler:
            # oFile_handler.write('feature_portfolio' + ',' + 'kfolds' + ',' + 'accuracy' +
            #                     ',' + 'precision' +
            #                     ',' + 'recall' \
            #                     + ',' + 'f1_score' \
            #                     + '\n')
            oFile_handler.write(str(self.key) + ',' + str(self.kfolds) + ',' + str(float(total_accu) / self.kfolds) \
                                + ',' + str(float(total_pre) / self.kfolds) + ',' + str(float(total_rec) / self.kfolds) \
                                + ',' + str(float(total_f1) / self.kfolds) \
                                + '\n')

if __name__ == "__main__":

    filePath = 'D:\\yongxiong\\zhongxing_data\\train_data\\'
    inFilePath = filePath + 'zhongxing_train_all_features_target_std.csv'
    train_data = gl.SFrame.read_csv(inFilePath, delimiter=",", header=True)
    columes_name = train_data.column_names()
    columes_name.remove('target')
    kfolds = 4
    models = ['BT_','RF_']
    feature_portfolios = {}
    # 460 - 400 个特征
    feature_portfolios[0] = columes_name[0:]
    # 460 - 400 个特征
    feature_portfolios[1] = columes_name[0:59]
    for key, feature_portfolio in feature_portfolios.iteritems():
        print feature_portfolio
        # output
        # output_file =  filePath + "result_set\\BT_validatation_zhongxing_%s.txt" % key
        model = LeadsGenerationModel_Validation(train_data, feature_portfolio, models[0],'target', key,kfolds)  #, output_file
        model.validate()
