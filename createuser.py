# from django.contrib.auth.models import User
import MySQLdb
from hashlib import sha1

# def old():
    # user = User.objects.create_user(username='admin', email='supriyom@theeolico.com', password='pa$$w0rd')


def connectToDb():
    dbConn = MySQLdb.connect(user="artb_Admin", passwd="cDLCntgtsjAOP%tw", host="191.101.0.14", port=3306, db="artb_Artbider_Prod")
    cursor = dbConn.cursor(MySQLdb.cursors.DictCursor)
    return dbConn, cursor


def disconnectDb(connList):
    connList[1].close()
    connList[0].close()


def new():
    rootHashPassword = sha1(b'root').hexdigest()
    dataInsertQuery = f"INSERT INTO user_accounts(full_name, username, login_email, login_password) VALUES('root admin', 'root', 'root@gmail.com', '{rootHashPassword}');"
    connList = connectToDb()
    connList[1].execute(dataInsertQuery)
    connList[0].commit()
    disconnectDb(connList)


new()
