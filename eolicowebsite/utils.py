import os, sys, re, time
import datetime
import MySQLdb


def connecttoDB():
    dbconn = MySQLdb.connect(user="websiteadmin", passwd="AVNS_UHIULiqroqLJ4x2ivN_", host="art-curv-db-mysql-lon1-59596-do-user-10661075-0.b.db.ondigitalocean.com", port=25060, db="staging")
    #dbconn = MySQLdb.connect(user="artb_Admin", passwd="cDLCntgtsjAOP%tw", host="191.101.0.14", port=3306, db="artb_Artbider_Prod")
    cursor = dbconn.cursor()
    return [dbconn, cursor]


def connectToDb():
    dbConn = MySQLdb.connect(user="websiteadmin", passwd="AVNS_UHIULiqroqLJ4x2ivN_", host="art-curv-db-mysql-lon1-59596-do-user-10661075-0.b.db.ondigitalocean.com", port=25060, db="staging")
    #dbConn = MySQLdb.connect(user="artb_Admin", passwd="cDLCntgtsjAOP%tw", host="191.101.0.14", port=3306, db="artb_Artbider_Prod")
    cursor = dbConn.cursor(MySQLdb.cursors.DictCursor)
    return dbConn, cursor


def disconnectDB(dbconn, cursor):
    try:
        cursor.close
        dbconn.close()
        return True
    except:
        print("Error: %s" % sys.exc_info()[1].__str__())
        return False


def disconnectDb(connList):
    connList[1].close()
    connList[0].close()
