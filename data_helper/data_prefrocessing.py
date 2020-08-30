#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17/1/2017 下午 12:51
# @Author  : GUO Ganggang
# @email   : ganggangguo@csu.edu.cn
# @Site    : 
# @File    : data_prefrocessing.py
# @Software: PyCharm

import pandas as pd
import datetime
from itertools import islice
import sys
import re
import codecs
import graphlab as gl
from graphlab import SArray

reload(sys)
sys.setdefaultencoding('utf-8')

##################
## 数据预处理步骤：
##  1、从业务数据本身抽取相关特征，去噪
##
##  2、与业务数据直接相关的扩展数据抽取数据，补充残缺数据
##
##  3、与业务数据间接相关的扩展数据源抽取特征，去噪清理
##
##  4、基于实现定义的问题，打标签
##
##  5、特征匹配合并
##
##  6、特征规范化
##################


# 计算年龄
def CalculateAge(Date_ymd_list):
    '''Calculates the age and days until next birthday from the given birth date'''
    age = 0.0
    try:
      # Date = Date.split('.')
      BirthDate = datetime.date(int(Date_ymd_list[0]), int(Date_ymd_list[1]), int(Date_ymd_list[2]))
      Today = datetime.date.today()
      if (Today.month > BirthDate.month):
        NextYear = datetime.date(Today.year + 1, BirthDate.month, BirthDate.day)
      elif (Today.month < BirthDate.month):
        NextYear = datetime.date(Today.year, Today.month + (BirthDate.month - Today.month), BirthDate.day)
      elif (Today.month == BirthDate.month):
        if (Today.day > BirthDate.day):
          NextYear = datetime.date(Today.year + 1, BirthDate.month, BirthDate.day)
        elif (Today.day < BirthDate.day):
          NextYear = datetime.date(Today.year, BirthDate.month, Today.day + (BirthDate.day - Today.day))
        elif (Today.day == BirthDate.day):
          NextYear = 0
      Age = Today.year - BirthDate.year
      if NextYear == 0: #if today is the birthday
        # return '%d, days until %d: %d' % (Age, Age+1, 0)
        age = Age + 1
      else:
        DaysLeft = NextYear - Today
        age = Age + round(float(360-DaysLeft.days) / 360,1)
        # return '%d, days until %d: %d' % (Age, Age+1, DaysLeft.days)
    except:
      return 'Wrong date format'
    return age

# 处理ID相关的业务数据
def read_excel_byPanda_zhongxing(infilePath,infilePath_temp,outfilePath):

    df = pd.read_excel(infilePath)
    print df.columns

    df_temp = pd.read_excel(infilePath_temp)
    print df_temp.columns

    clean_df = pd.DataFrame()
    clean_df[u'合同号'] = df[u'合同号']
    clean_df[u'逾期天数'] = df[u'逾期天数']
    # clean_df[u'剩余本金与贷款本金比率'] = df[u'剩余本金与贷款本金比率']
    # clean_df[u'转让低价与结清金额比率'] = df[u'转让低价与结清金额比率']
    clean_df[u'待还金额与罚贷总额比率'] = df[u'待还金额与罚贷总额比率']
    # clean_df[u'已还款期数与还款总期数比率'] = df[u'已还款期数与还款总期数比率']
    # clean_df[u'转让底价'] = df[u'转让底价']
    clean_df[u'贷款本金'] = df[u'贷款本金']
    clean_df[u'还款总期限'] = df[u'还款总期限']
    # clean_df[u'已还款期数'] = df[u'已还款期数']
    clean_df[u'待还金额'] = df[u'待还金额']
    clean_df[u'罚贷总额'] = df[u'罚贷总额']

    # 年龄
    k = 0
    clean_df[u'年龄'] = df[u'身份证号']
    for date in df[u'身份证号']:
        birthday = []
        birthday.append(date[6:10])
        birthday.append(date[10:12])
        birthday.append(date[12:14])
        age = CalculateAge(birthday)
        clean_df[u'年龄'][k] = age
        k += 1

    # 客户性别
    s = 0
    clean_df[u'性别'] = df[u'客户性别']
    for sex in df[u'客户性别']:
        # print sex
        if sex == u'男':
            clean_df[u'性别'][s] = '0'
        elif sex == u'女':
            clean_df[u'性别'][s] = '1'
        else:
            print 'error'
            clean_df[u'性别'][s] = '-1'
        s += 1

    # 案件类型
    # t = 0
    # clean_df[u'案件类型'] = df[u'案件类型']
    # for type in df[u'案件类型']:
    #     if type == u'债权转让':
    #         clean_df[u'案件类型'][t] = '0'
    #     elif type == u'正常委案':
    #         clean_df[u'案件类型'][t] = '1'
    #     else:
    #         print 'error'
    #         clean_df[u'案件类型'][t] = '-1'
    #     t += 1

    # 放款城市与户籍地是否相同
    clean_df[u'放款城市与户籍地是否相同'] = df[u'放款城市']
    for h in range(len(df[u'放款城市'])):
    #   print df[u'放款城市'][h], df[u'客户户籍地址'][h]
        try:
            if df[u'放款城市'][h] in df[u'客户户籍地址'][h]:
                clean_df[u'放款城市与户籍地是否相同'][h] = '0'
            elif df[u'放款城市'][h] not in df[u'客户户籍地址'][h]:
                clean_df[u'放款城市与户籍地是否相同'][h] = '1'
        except:
            clean_df[u'放款城市与户籍地是否相同'][h] = '-1'
            continue


    # 放款城市商业信用环境指数
    clean_df[u'放款城市商业信用环境指数'] = df[u'放款城市']
    for h in range(len(df[u'放款城市'])):
        # flag = 0
        sum_value = 0
        various_credit_indexs = []

        city = df[u'放款城市'][h] + u'市'
        # try:
        for i in range(len(df_temp[u'征信市场发达程度'].get_values())):
            if city == df_temp[u'征信市场发达程度'].get_values()[i]:
                sum_value += i
                # flag += 1
                various_credit_indexs.append(i)


        for j in range(len(df_temp[u'政府信用监管职能发挥'].get_values())):
            if city == df_temp[u'政府信用监管职能发挥'].get_values()[j]:
                sum_value += j
                # flag += 1
                various_credit_indexs.append(j)


        for k in range(len(df_temp[u'人均信用投放水平'].get_values())):
            if city == df_temp[u'人均信用投放水平'].get_values()[k]:
                sum_value += k
                # flag += 1
                various_credit_indexs.append(k)

        for l in range(len(df_temp[u'诚信教育活动开展情况'].get_values())):
            if city == df_temp[u'诚信教育活动开展情况'].get_values()[l]:
                sum_value += l
                # flag += 1
                various_credit_indexs.append(l)

        for m in range(len(df_temp[u'企业信用管理水平'].get_values())):
            if city == df_temp[u'企业信用管理水平'].get_values()[m]:
                sum_value += m
                # flag += 1
                various_credit_indexs.append(m)

        various_credit_indexs.append(sum_value)
        credit_index_str = ','.join(str(v) for v in various_credit_indexs)
        # clean_df[u'放款城市商业信用环境指数'][h] = str(sum_value / float(flag))
        clean_df[u'放款城市商业信用环境指数'][h] = credit_index_str
        # except:

    # 关联手机号
    clean_df[u'联系人列表'] = df[u'客户手机']
    for p in range(len(df[u'客户手机'])):
        iphone_numbers = []

        iphone_numbers.append(int(df[u'客户手机'][p]))
        if '1' in str(df[u'亲属或好友手机'][p]):
            iphone_numbers.append(int(df[u'亲属或好友手机'][p]))
        if '1' in str(df[u'同事手机'][p]):
            iphone_numbers.append(int(df[u'同事手机'][p]))
        if '1' in str(df[u'附加联系人手机'][p]):
            iphone_numbers.append(int(df[u'附加联系人手机'][p]))
        if '1' in str(df[u'附加联系人2手机'][p]):
            iphone_numbers.append(int(df[u'附加联系人2手机'][p]))

        # print iphone_numbers
        iphone_numbers_str = '/'.join(str(v) for v in iphone_numbers)
        clean_df[u'联系人列表'][p] = iphone_numbers_str

    # 是否联系上有效还款人
    # c = 0
    # clean_df[u'跟进类型'] = df[u'跟进类型']
    # for conn in df[u'跟进类型']:
    #     # print conn
    #     if u'无法' in conn:
    #         clean_df[u'跟进类型'][c] = '0'
    #     elif u'无法' not in conn:
    #         clean_df[u'跟进类型'][c] = '1'
    #     else:
    #         print 'error'
    #         clean_df[u'跟进类型'][c] = '-1'
    #     c += 1

    clean_df.to_csv(outfilePath,encoding="utf_8_sig")

# 统计并设定预测目标
def static(infilePath,outfilePath_1,outfilePath_2,outfilePath_3):

    result_times = pd.read_excel(infilePath)
    print result_times.columns
    result_times.to_csv(outfilePath_1, encoding="utf_8_sig")
    static_result = {}
    with open(outfilePath_2, "w") as output_file:
        with open(outfilePath_1, "r") as input_file:
            for line in islice(input_file, 1, None):
                temp = line.strip().split(',')
                if "L2" not in line or (len(temp)<2):
                    continue
                else:
                    if temp[1] in static_result.keys():
                        static_result[temp[1]] += 1
                    else:
                        static_result[temp[1]] = 1
        class_1 = 0
        class_2 = 0
        class_3 = 0
        class_4 = 0
        # 21 35 51
        # 812 832 810
        # 602 634 611 607
        # 21 35 51
        for key in static_result.keys():
            print key,static_result[key]
            if 1 <= static_result[key] < 11:
                class_1 += 1
                flag = 0
            elif(12 <= static_result[key] < 16):
                class_2 += 1
                flag = 1
            elif(17 <= static_result[key] < 25):
                class_3 += 1
                flag = 2
            else:
                class_4 += 1
                flag = 3

            output_file.write(str(key)+','+str(static_result[key])+','+str(flag) + '\n')
        print len(static_result)
        print class_1,class_2,class_3 ,class_4

    value_static = {}
    with open(outfilePath_3, "w") as output_file:
        for key in static_result.keys():
            if static_result[key] in value_static.keys():
                value_static[static_result[key]] += 1
            else:
                value_static[static_result[key]] = 1
        for key in value_static.keys():
            print key, value_static[key]
            output_file.write(str(key) + ',' + str(value_static[key]) + '\n')

# 中腾讯数据处理数据
def read_excel_byPanda_zhongtengxun(infilePath,infilePath_temp,outfilePath):
    df = pd.read_excel(infilePath)
    print df.columns

    df_temp = pd.read_excel(infilePath_temp)
    print df_temp.columns

    clean_df = pd.DataFrame()
    clean_df[u'合同号'] = df[u'合同号']
    clean_df[u'逾期天数'] = df[u'逾期天数']
    # clean_df[u'剩余本金与贷款本金比率'] = df[u'剩余本金与贷款本金比率']
    # clean_df[u'转让低价与结清金额比率'] = df[u'转让低价与结清金额比率']
    clean_df[u'待还金额与罚贷总额比率'] = df[u'待还金额与罚贷总额比率']
    # clean_df[u'已还款期数与还款总期数比率'] = df[u'已还款期数与还款总期数比率']
    # clean_df[u'转让底价'] = df[u'转让底价']
    clean_df[u'贷款本金'] = df[u'贷款本金']
    clean_df[u'还款总期限'] = df[u'还款总期限']
    # clean_df[u'已还款期数'] = df[u'已还款期数']
    clean_df[u'待还金额'] = df[u'待还金额']
    clean_df[u'罚贷总额'] = df[u'罚贷总额']

    # 年龄
    k = 0
    clean_df[u'年龄'] = df[u'身份证号']
    for date in df[u'身份证号']:
        birthday = []
        birthday.append(date[6:10])
        birthday.append(date[10:12])
        birthday.append(date[12:14])
        age = CalculateAge(birthday)
        clean_df[u'年龄'][k] = age
        k += 1

    # 客户性别
    s = 0
    clean_df[u'性别'] = df[u'性别']
    for sex in df[u'性别']:
        # print sex
        if sex == u'男':
            clean_df[u'性别'][s] = '0'
        elif sex == u'女':
            clean_df[u'性别'][s] = '1'
        else:
            print 'error'
            clean_df[u'性别'][s] = '-1'
        s += 1

    # 放款城市与户籍地是否相同
    clean_df[u'放款城市与户籍地是否相同'] = df[u'放款城市']
    for h in range(len(df[u'放款城市'])):
    #   print df[u'放款城市'][h], df[u'客户户籍地址'][h]
        try:
            if df[u'放款城市'][h] in df[u'客户户籍地址'][h]:
                clean_df[u'放款城市与户籍地是否相同'][h] = '0'
            elif df[u'放款城市'][h] not in df[u'客户户籍地址'][h]:
                clean_df[u'放款城市与户籍地是否相同'][h] = '1'
        except:
            clean_df[u'放款城市与户籍地是否相同'][h] = '-1'
            continue


    # 放款城市商业信用环境指数
    clean_df[u'放款城市商业信用环境指数'] = df[u'放款城市']
    for h in range(len(df[u'放款城市'])):
        # flag = 0
        sum_value = 0
        various_credit_indexs = []

        city = df[u'放款城市'][h] + u'市'
        # try:
        for i in range(len(df_temp[u'征信市场发达程度'].get_values())):
            if city == df_temp[u'征信市场发达程度'].get_values()[i]:
                sum_value += i
                # flag += 1
                various_credit_indexs.append(i)

        for j in range(len(df_temp[u'政府信用监管职能发挥'].get_values())):
            if city == df_temp[u'政府信用监管职能发挥'].get_values()[j]:
                sum_value += j
                # flag += 1
                various_credit_indexs.append(j)

        for k in range(len(df_temp[u'人均信用投放水平'].get_values())):
            if city == df_temp[u'人均信用投放水平'].get_values()[k]:
                sum_value += k
                # flag += 1
                various_credit_indexs.append(k)

        for l in range(len(df_temp[u'诚信教育活动开展情况'].get_values())):
            if city == df_temp[u'诚信教育活动开展情况'].get_values()[l]:
                sum_value += l
                # flag += 1
                various_credit_indexs.append(l)

        for m in range(len(df_temp[u'企业信用管理水平'].get_values())):
            if city == df_temp[u'企业信用管理水平'].get_values()[m]:
                sum_value += m
                # flag += 1
                various_credit_indexs.append(m)

        various_credit_indexs.append(sum_value)
        credit_index_str = ','.join(str(v) for v in various_credit_indexs)
        # clean_df[u'放款城市商业信用环境指数'][h] = str(sum_value / float(flag))
        clean_df[u'放款城市商业信用环境指数'][h] = credit_index_str


    # 关联手机号
    clean_df[u'联系人列表'] = df[u'客户手机']
    for p in range(len(df[u'客户手机'])):
        iphone_numbers = []
        # print df[u'客户手机'][p]
        return_list = re.findall("\d+",str(df[u'客户手机'][p]))
        return_str = ''.join(return_list)
        print return_str
        if int(return_str) not in iphone_numbers:
            iphone_numbers.append(int(return_str))
        if '1' in str(df[u'客户配偶联系电话'][p]):
            return_list = re.findall("\d+", df[u'客户配偶联系电话'][p])
            return_str = ''.join(return_list)
            print return_str
            if int(return_str) not in iphone_numbers:
                iphone_numbers.append(int(return_str))
        if '1' in str(df[u'其他联系人电话'][p]):
            return_list = re.findall("\d+", df[u'其他联系人电话'][p])
            return_str = ''.join(return_list)
            print return_str
            if int(return_str) not in iphone_numbers:
                iphone_numbers.append(int(return_str))

        # # print iphone_numbers
        iphone_numbers_str = '/'.join(str(v) for v in iphone_numbers)
        clean_df[u'联系人列表'][p] = iphone_numbers_str


    clean_df.to_csv(outfilePath,encoding="utf_8_sig")

# 数据去重
def dedup(infilePath,outfilePath):
    set_phone = set()
    with open(outfilePath, 'w') as output_file:
        with codecs.open(infilePath, "rb", "utf-8") as input_file:
            for line in input_file.readlines():
                line = line.strip()
                if line not in set_phone:
                    output_file.write(line + '\n')
                    set_phone.add(line)

# 数核对
def check(infilePath_1,infilePath_2):
    first_set = set()
    flag = 0
    with codecs.open(infilePath_1, "rb", "utf-8") as input_file_1:
        for line in input_file_1.readlines():
            line = line.strip().split('	')
            first_set.add(line[1])

    with codecs.open(infilePath_2, "rb", "utf-8") as input_file_2:
        for line in input_file_2.readlines():
            line = line.strip().split('	')
            if line[0] in first_set:
                print line[0]
                flag += 1
                # print line[0]
    print flag

    # print line
    # if line == '15261441978':
    #     print 'true'
    # phone_number = re.findall("\d+",line)
    # print phone_number
    # phone_number_str = ''.join(phone_number)
    # output_file.write(phone_number_str + '\n')

# 抽取微博数据相关特征
def staicPostTime(inFilePath,output_path):
    contract_num_list = {}
    with codecs.open(inFilePath, "rb", "utf-8") as input_file:
        for line in islice(input_file, 1, None):
            temp = line.strip().split('\t')
            contract_num_list[temp[0]] = contract_num_list.get(temp[0], 1) + 1
        print len(contract_num_list)


    with open(output_path, 'w') as output_file:
        hour_list = []
        for k in range(24):
            hour_list.append(str(k) + '_clock')
        hour_str = ','.join(hour_list)
        output_file.write('phone_number' + ',' + 'post_tool' + ',' + 'post_tool_ratio' + ',' + 'original_ratio' + ',' + hour_str + '\n')
        for contract in contract_num_list.keys():
            static_hour = {}
            hourVec = []
            forward_num = 0
            post_tool_static = {}
            with codecs.open(inFilePath, "rb", "utf-8") as input_file:
                for line in islice(input_file, 1, None):
                    temp = line.strip().split('\t')
                    total_num = len(temp)
                    if temp[0] == contract:
                        #print temp[0], uid
                        if 'iPhone' in temp[total_num - 4] or 'iPad' in temp[total_num - 4]:  #3
                            post_tool_static[temp[total_num - 4]] = post_tool_static.get(temp[total_num - 4], 1) + 1

                        static_hour[temp[total_num - 3]] = static_hour.get(temp[total_num - 3], 0) + 1  #2
                        if u'转发' in temp[2]:
                            forward_num += 1

                    else:
                        continue
                #print len(static_hour)
            post_tool = []
            post_tool_ratio = []
            post_tool_sorted = sorted(post_tool_static.iteritems(), key=lambda d: d[1], reverse=True)
            for i in range(len(post_tool_sorted)):
                print post_tool_sorted[i][0],post_tool_sorted[i][1]
                post_tool.append(post_tool_sorted[i][0])
                post_tool_ratio_temp = round(post_tool_sorted[i][1] / float(contract_num_list[contract]), 4)
                post_tool_ratio.append(post_tool_ratio_temp)

            for j in range(24):
                if str(j) in static_hour.keys():
                    #print static_hour[str(j)],uid_num_list[uid]
                    ratio_hour = round((static_hour[str(j)] / float(contract_num_list[contract])),2)
                    #print 'ratio_hour ' + str(ratio_hour)
                    hourVec.append(ratio_hour)
                else:
                    hourVec.append(0.0)
            original_ratio = round((float(contract_num_list[contract] - forward_num) / contract_num_list[contract]), 4)
            # vecItem = re.sub('\[', '',str(hourVec))
            # vecItem = re.sub('\]', '', str(vecItem))
            vecItem = ','.join([str(hour) for hour in hourVec])
            post_tool = '/'.join(post_tool)
            post_tool_ratio = '/'.join([str(ratio) for ratio in post_tool_ratio])
            output_file.write(str(contract) + ',' + str(post_tool) + ',' + str(post_tool_ratio) + ',' + str(original_ratio) + ',' + vecItem + '\n')

# 异构特征合并
def merge(infilePath_1,infilePath_2,infilePath_3,outfilePath_1,outfilePath_2):
    # 将业务数据与微博特征合并
    weibo_uid_info = {}
    with codecs.open(infilePath_1, "rb", "utf-8") as input_file:
        for line in islice(input_file.readlines(), 1, None):
            line = line.strip().split('	')
            if len(line) != 8:
                print line[0]
            weibo_uid_info[line[0]] = line[1:]

    print len(weibo_uid_info)
    with open(outfilePath_1, 'w') as output_file:
        with codecs.open(infilePath_2, "rb", "utf-8") as input_file:
            for line in input_file.readlines():
                line = line.strip().split(',')
                phones = line[-1].split('/')
                # print phones
                # for phone in phones:
                # phone = phones[0]
                flag = 0
                for phone in phones:
                    if phone in weibo_uid_info.keys() and flag != 1:
                        flag = 1
                        uid_infor_1 = ','.join(weibo_uid_info[phone][0:2]) # 去除微博uid的性别
                        uid_infor_2 = ','.join(weibo_uid_info[phone][3:])
                        # uid_infor = ','.join(weibo_uid_info[phone][0:])
                        id_infor_1 = ','.join(line[0:-1]) # 去除多手机号列
                        # id_infor_2 = ','.join(line[17:])
                        # id_infor = ','.join(line[0:])
                        #str(phone) +',' +
                        # print len(line[0:16]),len(line[17:]),len(weibo_uid_info[phone][0:1]),len(weibo_uid_info[phone][2:])
                        # print len(id_infor_1) ,len(id_infor_2) ,len(uid_infor_1) ,len(uid_infor_2)
                        output_file.write(str(phone) +',' + id_infor_1 +','+  uid_infor_1 + ',' +  uid_infor_2 + '\n') # + id_infor_2 +','
                        # output_file.write(id_infor_1 + ',' + str(phone) + ',' + id_infor_2 + ',' +  uid_infor + '\n')



    # 将所有特征和分类目标合并
    target = {}
    with codecs.open(infilePath_3, "rb", "utf-8") as input_file:
        for line in input_file.readlines():
            line = line.strip().split(',')
            target[line[0]] = line[2]
    print len(target)

    static_samples = {}
    with open(outfilePath_2, 'w') as output_file:
        with codecs.open(outfilePath_1, "rb", "utf-8") as input_file:
            for line in input_file.readlines():
                temp = line.strip().split(',')
                if temp[1] in target.keys():
                    if target[temp[1]] in static_samples.keys():
                        static_samples[target[temp[1]]] += 1
                    else:
                        static_samples[target[temp[1]]] = 0
                    features_1 = ','.join(temp[2:18])   # 去除合同号列
                    features_2 = ','.join(temp[19:])    # 去除uid
                    output_file.write(target[temp[1]] + ','+  features_1 + ','+  features_2 + '\n')

    for key in static_samples:
        print key,static_samples[key]

# 合并异构特征
def merge_all_features(infilePath_1,infilePath_2,infilePath_3,outfilePath):

    # ID特征与微博uid用户画像特征，获取该文件中的target特征
    id_uid_baseProfile = {}
    contract_target = {}
    with codecs.open(infilePath_1, "rb", "utf-8") as input_file:
        for line in input_file.readlines():
            temp = line.strip().split(',')
            id_uid_baseProfile[temp[1]] = temp[2:]
            contract_target[temp[1]] = temp[0]
    print len(id_uid_baseProfile),len(contract_target)

    # 微博内容发布时间特征和发布终端特征
    weibopost_time_port = {}
    with codecs.open(infilePath_2, "rb", "utf-8") as input_file:
        for line in input_file.readlines():
            temp = line.strip().split(',')
            weibopost_time_port[temp[0]] = temp[1:]
    print len(weibopost_time_port)

    # 微博内容word2vec特征，最终合并所有特征
    static_class_numbers = {}
    train_set_numbers = 0

    features_name = []
    for i in range(446):
        features_name.append('fer_'+str(i))
    features_name_str = ','.join(features_name[0:])

    with open(outfilePath, 'w') as output_file:
        output_file.write('target' + ',' + features_name_str + '\n')
        with codecs.open(infilePath_3, "rb", "utf-8") as input_file:
            for line in input_file.readlines():
                temp = line.strip().split(',')
                id_uid_baseProfile_str = ','.join(id_uid_baseProfile[temp[0]][0:])
                weibopost_time_port_str =','.join(weibopost_time_port[temp[0]][0:])
                weibo_w2v_str = ','.join(temp[1:])

                # print len(id_uid_baseProfile[temp[0]][0:]) + len(weibopost_time_port[temp[0]][0:]) + len(temp[1:])

                if contract_target[temp[0]] in static_class_numbers.keys():
                    static_class_numbers[contract_target[temp[0]]] += 1
                else:
                    static_class_numbers[contract_target[temp[0]]] = 1
                train_set_numbers += 1
                output_file.write(str(contract_target[temp[0]]) + ',' + id_uid_baseProfile_str  + ',' + \
                                  weibopost_time_port_str  + ',' + weibo_w2v_str+ '\n')
    print train_set_numbers
    for key in static_class_numbers.keys():
        print key,static_class_numbers[key]


# 特征标准化
def graphlabDealwithData(inFilePath,outFilePath):

    data_read = gl.SFrame.read_csv(inFilePath)

    colum_name = data_read.column_names()

    length = len(colum_name)

    print length

    colum_name_filt = colum_name[1:]

    data_read_filt = data_read[colum_name_filt]

    target_dir = data_read['target']

    new_dirc = {}
    for i in range(len(colum_name_filt)):
        new_list = []
        data_array = data_read_filt[colum_name_filt[i]].to_numpy()
        sa = SArray(data_array)
        mean_sa = sa.mean()
        std_sa = sa.std()
        for j in range(len(sa)):
            new_list.append(round(((sa[j] - mean_sa) / std_sa),6))
        new_dirc[colum_name_filt[i]] = new_list


    data_write = gl.SFrame(new_dirc)
    data_write = data_write.add_column(target_dir,'target')

    data_write.save(outFilePath)

def divide_csv(infilePath):
    # contract_phone = {}
    # with codecs.open(infilePath, "rb", "utf-8") as input_file:
    #     for line in islice(input_file.readlines(), 1, None):
    #         temp = line.strip().split('\t')
    #         if temp[1] not in contract_phone.keys():
    #             contract_phone[temp[1]] = temp[0]
    #         else:
    #             continue
    with codecs.open(infilePath, "rb", "utf-8") as input_file:
        phones = set()
        for line in islice(input_file.readlines(), 1, None):
            temp = line.strip().split('\t')
            phones.add(temp[0])
        print len(phones)

    for phone in phones:
        with open('wordcloud_generation\\test_weibo_3word\\' + phone, 'w') as output_file: #+'.csv'
            with codecs.open(infilePath, "rb", "utf-8") as input_file:
                for line in islice(input_file.readlines(), 1, None):
                    temp = line.strip().split('\t')
                    if phone == temp[0] :
                        output_file.write(temp[1]+'\n')
                    else:
                        continue


# 补全数据
def complementaryData(infilePath,outfilePath):
    df = pd.read_excel(infilePath)
    print df.columns

    clean_df = pd.DataFrame()

    clean_df[u'放款城市'] = df[u'客户公司地址']
    for p in range(len(df[u'客户公司地址'])):
        if str(df[u'客户公司地址'][p]) == 'NULL' or str(df[u'客户公司地址'][p]) == '' or str(df[u'客户公司地址'][p]) == 'nan':
            continue
        else:
            if u'呼和浩特' in str(df[u'客户公司地址'][p]):
                clean_df[u'放款城市'][p] = u'呼和浩特'
            elif u'石家庄' in str(df[u'客户公司地址'][p]):
                clean_df[u'放款城市'][p] = u'石家庄'
            elif u'哈尔滨' in str(df[u'客户公司地址'][p]):
                clean_df[u'放款城市'][p] = u'哈尔滨'
            elif u'南宁' in str(df[u'客户公司地址'][p]):
                clean_df[u'放款城市'][p] = u'南宁'
            elif u'绥化' in str(df[u'客户公司地址'][p]):
                clean_df[u'放款城市'][p] = u'绥化'
            else:
                print str(df[u'客户公司地址'][p]).decode('utf8')[3:5].encode('utf8')
                if str(df[u'客户公司地址'][p]).decode('utf8')[3:5].encode('utf8') != ' ':
                    clean_df[u'放款城市'][p] = str(df[u'客户公司地址'][p]).decode('utf8')[3:5].encode('utf8')
    clean_df.to_csv(outfilePath,encoding="utf_8_sig")



if __name__ == '__main__':

    # filePath = "D:\\machine_learning_credit_risk\\data\\zhongtengxun\\"
    # filePath = "D:\\yongxiong\\zhongxing_data\\"
    filePath = "D:\\yongxiong\\test_data\\"
    # inFilePath = filePath + "debit_infor_zhongxing.xlsx"
    # inFilePath_temp  = filePath + u"2013中国城市商业信用环境指数" + ".xlsx"
    # outFilePath = filePath + "debit_infor_zhongxing.csv"
    # read_excel_byPanda_zhongxing(inFilePath,inFilePath_temp,outFilePath)

    # inFilePath = filePath + "quary_infor_zhongtengxun.xlsx"
    # outFilePath_1 = filePath + "quary_infor_zhongtengxun.csv"
    # outFilePath_2 = filePath + "quary_infor_static.csv"
    # outFilePath_3 = filePath + "quary_infor_static_value.csv"
    # static(inFilePath,outFilePath_1,outFilePath_2,outFilePath_3)


    # inFilePath = filePath + u"中腾讯_phoneNumbers.xlsx"
    # outFilePath = filePath + u"phone_中腾讯.csv"
    # read_excel_byPanda_temp(inFilePath,outFilePath)
    # infilePath = filePath + "iphone_number.txt"
    # outfilePath = filePath + "zhongxing_phones.csv"
    # dedup(infilePath, outfilePath)

    # infilePath = filePath + "zhognxing_sweibo_uid.txt"
    # outfilePath = filePath + "zhongtengxun_weibo_uid.txt"
    # check(infilePath, outfilePath)

    # list_test = ['3','5','7','9','41']
    # print list_test[1:]
    # inFilePath_1 = filePath + "zhongtengxun_weibo_uid_profile.csv"
    # inFilePath_2 = filePath + "debit_infor_zhongtengxun.csv"
    # inFilePath_3 = filePath + "quary_infor_static_zhongtengxun.csv"
    # outfilePath_1 = filePath + "zhongtengxun_all_features.csv"
    # outfilePath_2 = filePath + "zhongtengxun_id_uid_features_target.csv" #w2v_time_post_
    # merge(inFilePath_1,inFilePath_2,inFilePath_3,outfilePath_1,outfilePath_2)

    inFilePath = filePath + "weibo_uid_ugc.csv"    #"zhongxing_weibo_uid_weibo_LDA_train.csv"
    outfilePath = filePath + "ugc_posttool_posttime_originalWeiboRatio_static.csv"   #"zhongxing_weibo_postTime_postTool.csv"
    staicPostTime(inFilePath, outfilePath)

    # inFilePath_1 = filePath + "zhongxing_id_uid_features_target.csv"
    # inFilePath_2 = filePath + "zhongxing_weibo_time_post.csv"
    # inFilePath_3 = filePath + "zhongxing_weibo_train_w2v_features.csv"
    # outfilePath = filePath + "zhongxing_train_all_features_target.csv"
    # merge_all_features(inFilePath_1, inFilePath_2, inFilePath_3, outfilePath)

    # inFilePath = filePath + "zhongxing_train_all_features_target.csv"
    # outfilePath = filePath + "zhongxing_train_all_features_target_std.csv"
    # graphlabDealwithData(inFilePath, outfilePath)

    # infilePath = filePath + 'weibo_uid_ugc_seg_clean_3words.csv'
    # divide_csv(infilePath)

    # inFilePath = filePath + "debit_infor_zhongtengxun.xlsx"
    # outFilePath = filePath + "debit_infor_zhongtengxun_2.csv"
    # complementaryData(inFilePath,outFilePath)

    # inFilePath = filePath + "debit_infor_zhongtengxun.xlsx"
    # inFilePath_temp  = filePath + u"2013中国城市商业信用环境指数" + ".xlsx"
    # outFilePath = filePath + "debit_infor_zhongtengxun.csv"
    # read_excel_byPanda_zhongtengxun(inFilePath,inFilePath_temp,outFilePath)