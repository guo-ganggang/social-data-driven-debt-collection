#! /usr/bin/python
# coding=utf-8
import codecs
from itertools import islice
import imp
import MySQLdb
import datetime
import time
import re

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

cursorObj = imp.load_source("dbCursor", "DB/WeiboDBConnection.py")

# 获取微博用户画像数据，主要是微博用户账户注册信息等
def obtain_DB_uid_profile(input_path,output_path):
    phone_uid = {}
    with codecs.open(input_path, "rb", "utf-8") as input_file:
        for line in islice(input_file.readlines(), 1, None):
            temp = line.strip().split('\t')
            # temp_list = []
            # temp_list.append(temp[0])
            # temp_list.append(temp[18])
            # phone_uid[temp[1]] = temp_list
            phone_uid[temp[1]] = temp[0]

    print len(phone_uid)

    try:
        con, cursor = cursorObj.getDBConnection()
        with open(output_path, 'w') as output_file:
            output_file.write(
                'phone' + '\t' + 'uid' + '\t' + 'created_days' + '\t' + 'gender' + '\t' + 'follower_num' + '\t' + \
                'followee_num' + '\t' + 'level' + '\t' + 'weibo_num' + '\n')
            now = int(time.time())
            for key in phone_uid.keys():
                uid = str(key)
                sql = "select id,created_at,gender,follower_num,followee_num,level,weibo_num from Chinese_stream.users_ggguo where id = '%s'" % uid + " #and weibo_num > 1500"
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    timeArray = time.strptime(str(row[1]), '%Y-%m-%d %H:%M:%S')
                    timeStamp = int(time.mktime(timeArray))
                    days =  (now - timeStamp) / 3600 / 24
                    # contract_uid = '\t'.join(phone_uid[key])
                    output_file.write(phone_uid[key] + '\t' + str(row[0]) + '\t' + str(days) + '\t' + str(row[2]) + '\t' + str(row[3]) + '\t' + \
                                       str(row[4]) + '\t' + str(row[5]) + '\t' + str(row[6]) + '\n')
        cursor.close()
        con.close()
    except MySQLdb.Error as e:
        print e


# 获取制定微博数据
def obtain_DB_uid_weibo(input_path,output_path):
    phone_uid = {}
    with codecs.open(input_path, "rb", "utf-8") as input_file:
        # for line in islice(input_file.readlines(), 1, None):
        for line in input_file.readlines():
            temp = line.strip().split(',')
            temp_list = []
            temp_list.append(temp[0])
            temp_list.append(temp[1])
            phone_uid[temp[-6]] = temp_list
            print temp[-6]
    print len(phone_uid)

    # phone_uid = {}
    # with codecs.open(input_path, "rb", "utf-8") as input_file:
    #     for line in islice(input_file.readlines(), 1, None):
    #         temp = line.strip().split('\t')
    #         phone_uid[temp[1]] = temp[0]
    # print len(phone_uid)

    try:
        con, cursor = cursorObj.getDBConnection()
        with open(output_path, 'w') as output_file:
            # output_file.write(
            #     'contract' + '\t' + 'phone' + '\t' + 'uid' + '\t' + 'text' + '\t' + 'app_source' + '\t' + 'created_at' + '\t' + \
            #     'repost_num' + '\t' + 'favourite_num' + '\t' + 'comment_num' + '\n')

            output_file.write('phone'  + '\t' + 'contract_uid' + '\t' + 'uid' + '\t' + 'text' + '\t' + 'app_source'+ '\t' + 'hour' + '\t' + 'created_at' + '\n')

            flag = 0
            for key in phone_uid.keys():
                uid = str(key)
                # sql = "select uid,text,app_source,created_at,repost_num,favourite_num,comment_num from Chinese_stream.timelines_ggguo where uid = '%s'" % uid
                sql = "select uid,text,app_source,created_at from Chinese_stream.timelines_ggguo where uid = '%s'" % uid
                cursor.execute(sql)
                rows = cursor.fetchall()
                if len(rows) >= 5:
                    print uid + ': ' + str(len(rows))
                    flag += 1
                    for row in rows:
                        timeArray = time.strptime(str(row[3]), '%Y-%m-%d %H:%M:%S')
                        hour = timeArray.tm_hour
                        # contract_phone = '\t'.join(phone_uid[key])
                        text = re.sub(r"\n",'',row[1].strip())
                        phone_contract_uid = '\t'.join(phone_uid[key])
                        # output_file.write(contract_phone + '\t' + str(row[0]) + '\t' + str(text) + '\t' + str(row[2]) + '\t' + str(hour) + '\t' + \
                        #                    str(row[4]) + '\t' + str(row[5]) + '\t' + str(row[6]) + '\n')
                        output_file.write(phone_contract_uid + '\t' + str(row[0]) + '\t' + str(text) + '\t' + str(row[2]) +
                                          '\t' + str(hour) + '\t' + str(row[3])  + '\n')
                else:
                    # print uid + ': ' + str(len(rows))
                    continue
            print 'flag: ' + str(flag)
        cursor.close()
        con.close()
    except MySQLdb.Error as e:
        print e


# 获取测试数据
def obtain_test_data(output_path_1,output_path_2):

    phone_uid = {}
    phone_uid['18570371378'] = ['5388605616']
    phone_uid['15700754669_1word'] = ['2418270695']
    phone_uid['15616258025_1word'] = ['5065824199']

    try:
        con, cursor = cursorObj.getDBConnection()
        with open(output_path_1, 'w') as output_file:
            output_file.write(
                'phone' + '\t' + 'uid' + '\t' + 'created_days' + '\t' + 'gender' + '\t' + 'follower_num' + '\t' + \
                'followee_num' + '\t' + 'level' + '\t' + 'weibo_num'  + '\t' +  'screen_name' + '\t' + 'location'+ '\n')
            now = int(time.time())
            for key in phone_uid.keys():
                uid = ''.join(phone_uid[key])
                sql = "select id,created_at,gender,follower_num,followee_num,level,weibo_num,screen_name,location from Chinese_stream.users_ggguo where id = '%s'" % uid + " #and weibo_num > 1500"
                # print sql
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    timeArray = time.strptime(str(row[1]), '%Y-%m-%d %H:%M:%S')
                    timeStamp = int(time.mktime(timeArray))
                    days = (now - timeStamp) / 3600 / 24
                    # contract_uid = '\t'.join(phone_uid[key])
                    output_file.write(
                        key + '\t' + str(row[0]) + '\t' + str(days) + '\t' + str(row[2]) + '\t' + str(
                            row[3]) + '\t' +  str(row[4]) + '\t' + str(row[5]) + '\t' + str(row[6]) + '\t' +  \
                        str(row[7]) + '\t' + str(row[8]) + '\n')
        cursor.close()
        con.close()
    except MySQLdb.Error as e:
        print e

    try:
        con, cursor = cursorObj.getDBConnection()
        with open(output_path_2, 'w') as output_file:
            output_file.write(
                'phone' + '\t' + 'uid' + '\t' + 'text' + '\t' + 'app_source' + '\t' + '\t' + 'hour' + '\t' + \
                'created_at' + '\t' +  'weibo_influence' + '\n')
            for key in phone_uid.keys():
                uid = ''.join(phone_uid[key])
                sql = "select uid,text,app_source,created_at,repost_num,favourite_num,comment_num from Chinese_stream.timelines_ggguo where uid = '%s'" % uid
                # print sql
                cursor.execute(sql)
                rows = cursor.fetchall()
                if len(rows) >= 1:
                    print uid + ': ' + str(len(rows))
                    forward_num = 0
                    for row in rows:
                        timeArray = time.strptime(str(row[3]), '%Y-%m-%d %H:%M:%S')
                        hour = timeArray.tm_hour
                        text = re.sub(r"\n", '', row[1].strip())
                        if u'转发' in text:
                            forward_num += 1
                        weibo_influence = int(row[4])+int(row[5])+int(row[6])
                        output_file.write(key + '\t' + str(row[0]) + '\t' + str(text) + '\t' + str(row[2]) + \
                                          '\t' + str(hour) + '\t' + str(row[3]) + '\t' + str(weibo_influence)+ '\t' + '\n')
                    original_ratio = round((float(len(rows) - forward_num) / len(rows)),4)
                    print 'original_ratio: ' + str(original_ratio)
                else:
                    continue
        cursor.close()
        con.close()
    except MySQLdb.Error as e:
        print e



if __name__ == "__main__":

    # filePath = "D:\\machine_learning_credit_risk\\data\\zhongtengxun\\"
    # input_path = filePath + "zhongtengxun_weibo_uid.txt"
    # output_path = filePath + "zhongtengxun_weibo_uid_profile.csv"
    # obtain_DB_uid_profile(input_path, output_path)

    # input_path = filePath + "zhongtengxun_all_features.csv"
    # output_path = filePath + "zhongtengxun_weibo_train_data.csv"
    # obtain_DB_uid_weibo(input_path, output_path)

    filePath = "D:\\yongxiong\\test_data\\"
    output_path_1 = filePath + "weibo_uid_profile.csv"
    output_path_2 = filePath + "weibo_uid_ugc.csv"
    obtain_test_data(output_path_1, output_path_2)