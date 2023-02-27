import os, sys, re, time
import datetime
import MySQLdb



def connecttoDB():
    dbconn = MySQLdb.connect(user="artb_Admin",passwd="cDLCntgtsjAOP%tw",host="191.101.0.14", port=3306, db="artb_Artbider_Prod")
    cursor = dbconn.cursor()
    return [dbconn, cursor]


def disconnectDB(dbconn, cursor):
    try:
        cursor.close
        dbconn.close()
        return True
    except:
        print("Error: %s"%sys.exc_info()[1].__str__())
        return False


