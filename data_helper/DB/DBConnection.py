import MySQLdb

def getDBConnection():
    try:
        con = MySQLdb.connect(host = "123.57.237.131", user = 'root', passwd ='admin', db='sina_weibo',port=3306, charset='utf8')
        return (con,con.cursor())
    except MySQLdb.Error:
        print 'error....'
        raise