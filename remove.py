import MySQLdb
from hashlib import sha1
import datetime
import pandas as pd


def connectToDb():
    dbConn = MySQLdb.connect(user="artb_Admin", passwd="cDLCntgtsjAOP%tw", host="191.101.0.14", port=3306,
                             db="artb_Artbider_Prod")
    cursor = dbConn.cursor(MySQLdb.cursors.DictCursor)
    return dbConn, cursor


def disconnectDb(connList):
    connList[1].close()
    connList[0].close()


def userAccountsReport():
    userSelectQuery = f"""SELECT user_id, login_email FROM user_accounts WHERE DATE(created) != '{datetime.now().date()}'"""
    connList = connectToDb()
    connList[1].execute(userSelectQuery)
    userData = connList[1].fetchall()
    disconnectDb(connList)
    userDf = pd.DataFrame(list(userData))
    userDf.to_excel("D:\\userAccounts.xlsx", index=False)


def userPasswordChange():
    hashPassword = sha1(b'@Rtb1d3r#$01').hexdigest()
    userPasswordUpdateQuery = f"""SELECT user_id, login_email FROM user_accounts WHERE login_password = '{hashPassword}'"""
    connList = connectToDb()
    connList[1].execute(userPasswordUpdateQuery)
    userData = connList[1].fetchall()
    disconnectDb(connList)


def testing():
    datetimeFormat = datetime.datetime.now() - datetime.timedelta(hours=24)
    datetimeFormat = datetimeFormat.strftime('%Y-%m-%d %H:%M:%S')
    selectQuery = f"""SELECT COUNT(fal_lot_ID), fal_auction_ID FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID AND faa_artist_ID = 692983 AND fal_lot_published = 'yes' AND fal_lot_record_created >= '{datetimeFormat}' GROUP BY fal_auction_ID"""
    connList = connectToDb()
    connList[1].execute(selectQuery)
    auctionData = connList[1].fetchall()
    print(selectQuery)
    disconnectDb(connList)
    print(auctionData)


def auctionImageSetter():
    nullAuctionImageSelectQuery = f"""SELECT faac_auction_ID FROM fineart_auction_calendar WHERE faac_auction_image IS NULL"""
    connList = connectToDb()
    connList[1].execute(nullAuctionImageSelectQuery)
    nullAuctionImageDataList = connList[1].fetchall()
    for nullAuctionImageData in nullAuctionImageDataList:
        imageSelectQuery = f"""SELECT MAX(fal_lot_low_estimate), fal_lot_image1 FROM fineart_lots WHERE fal_auction_ID = {nullAuctionImageData['faac_auction_ID']} AND fal_lot_image1 IS NOT NULL"""
        connList[1].execute(imageSelectQuery)
        imageData = connList[1].fetchone()
        auctionImageUpdateQuery = f"""UPDATE fineart_auction_calendar SET faac_auction_image = '{imageData['fal_lot_image1']}' WHERE faac_auction_ID = {nullAuctionImageData['faac_auction_ID']}"""
        connList[1].execute(auctionImageUpdateQuery)
        connList[0].commit()
        print(auctionImageUpdateQuery)
    disconnectDb(connList)


def auctionStartDateUpdate():
    auctionStartDateUpdateQuery1 = f"""UPDATE fineart_auction_calendar SET faac_auction_start_date = '{datetime.datetime.now().date() + datetime.timedelta(days=1)}' WHERE faac_auction_ID = 9915"""
    auctionStartDateUpdateQuery2 = f"""UPDATE fineart_auction_calendar SET faac_auction_start_date = '{datetime.datetime.now().date() + datetime.timedelta(days=2)}' WHERE faac_auction_ID = 9918"""
    auctionStartDateUpdateQuery3 = f"""UPDATE fineart_auction_calendar SET faac_auction_start_date = '{datetime.datetime.now().date() + datetime.timedelta(days=3)}' WHERE faac_auction_ID = 9919"""
    auctionStartDateUpdateQuery4 = f"""UPDATE fineart_auction_calendar SET faac_auction_start_date = '{datetime.datetime.now().date() + datetime.timedelta(days=4)}' WHERE faac_auction_ID = 9925"""
    auctionStartDateUpdateQuery5 = f"""UPDATE fineart_auction_calendar SET faac_auction_start_date = '{datetime.datetime.now().date() + datetime.timedelta(days=5)}' WHERE faac_auction_ID = 9931"""

    auctionStartDateUpdateQuery6 = f"""UPDATE fineart_auction_calendar SET faac_auction_start_date = '{datetime.datetime.now().date() + datetime.timedelta(days=6)}' WHERE faac_auction_ID = 126330"""
    auctionStartDateUpdateQuery7 = f"""UPDATE fineart_auction_calendar SET faac_auction_start_date = '{datetime.datetime.now().date() + datetime.timedelta(days=7)}' WHERE faac_auction_ID = 126889"""
    auctionStartDateUpdateQuery8 = f"""UPDATE fineart_auction_calendar SET faac_auction_start_date = '{datetime.datetime.now().date() + datetime.timedelta(days=8)}' WHERE faac_auction_ID = 130643"""
    auctionStartDateUpdateQuery9 = f"""UPDATE fineart_auction_calendar SET faac_auction_start_date = '{datetime.datetime.now().date() + datetime.timedelta(days=9)}' WHERE faac_auction_ID = 130940"""
    auctionStartDateUpdateQuery10 = f"""UPDATE fineart_auction_calendar SET faac_auction_start_date = '{datetime.datetime.now().date() + datetime.timedelta(days=10)}' WHERE faac_auction_ID = 132471"""

    auctionStartDateUpdateQuery11 = f"""UPDATE fineart_auction_calendar SET faac_auction_start_date = '{datetime.datetime.now().date() + datetime.timedelta(days=11)}' WHERE faac_auction_ID = 49469"""
    auctionStartDateUpdateQuery12 = f"""UPDATE fineart_auction_calendar SET faac_auction_start_date = '{datetime.datetime.now().date() + datetime.timedelta(days=12)}' WHERE faac_auction_ID = 50685"""
    auctionStartDateUpdateQuery13 = f"""UPDATE fineart_auction_calendar SET faac_auction_start_date = '{datetime.datetime.now().date() + datetime.timedelta(days=13)}' WHERE faac_auction_ID = 55467"""
    auctionStartDateUpdateQuery14 = f"""UPDATE fineart_auction_calendar SET faac_auction_start_date = '{datetime.datetime.now().date() + datetime.timedelta(days=14)}' WHERE faac_auction_ID = 56665"""
    auctionStartDateUpdateQuery15 = f"""UPDATE fineart_auction_calendar SET faac_auction_start_date = '{datetime.datetime.now().date() + datetime.timedelta(days=15)}' WHERE faac_auction_ID = 60386"""

    auctionStartDateUpdateQuery16 = f"""UPDATE fineart_auction_calendar SET faac_auction_start_date = '{datetime.datetime.now().date() + datetime.timedelta(days=16)}' WHERE faac_auction_ID = 39532"""
    auctionStartDateUpdateQuery17 = f"""UPDATE fineart_auction_calendar SET faac_auction_start_date = '{datetime.datetime.now().date() + datetime.timedelta(days=17)}' WHERE faac_auction_ID = 39782"""
    auctionStartDateUpdateQuery18 = f"""UPDATE fineart_auction_calendar SET faac_auction_start_date = '{datetime.datetime.now().date() + datetime.timedelta(days=18)}' WHERE faac_auction_ID = 40071"""
    auctionStartDateUpdateQuery19 = f"""UPDATE fineart_auction_calendar SET faac_auction_start_date = '{datetime.datetime.now().date() + datetime.timedelta(days=19)}' WHERE faac_auction_ID = 40725"""
    auctionStartDateUpdateQuery20 = f"""UPDATE fineart_auction_calendar SET faac_auction_start_date = '{datetime.datetime.now().date() + datetime.timedelta(days=20)}' WHERE faac_auction_ID = 41824"""

    connList = connectToDb()
    connList[1].execute(auctionStartDateUpdateQuery1)
    connList[1].execute(auctionStartDateUpdateQuery2)
    connList[1].execute(auctionStartDateUpdateQuery3)
    connList[1].execute(auctionStartDateUpdateQuery4)
    connList[1].execute(auctionStartDateUpdateQuery5)
    connList[1].execute(auctionStartDateUpdateQuery6)
    connList[1].execute(auctionStartDateUpdateQuery7)
    connList[1].execute(auctionStartDateUpdateQuery8)
    connList[1].execute(auctionStartDateUpdateQuery9)
    connList[1].execute(auctionStartDateUpdateQuery10)
    connList[1].execute(auctionStartDateUpdateQuery11)
    connList[1].execute(auctionStartDateUpdateQuery12)
    connList[1].execute(auctionStartDateUpdateQuery13)
    connList[1].execute(auctionStartDateUpdateQuery14)
    connList[1].execute(auctionStartDateUpdateQuery15)
    connList[1].execute(auctionStartDateUpdateQuery16)
    connList[1].execute(auctionStartDateUpdateQuery17)
    connList[1].execute(auctionStartDateUpdateQuery18)
    connList[1].execute(auctionStartDateUpdateQuery19)
    connList[1].execute(auctionStartDateUpdateQuery20)
    connList[0].commit()
    disconnectDb(connList)
    print('Done!')


# auctionStartDateUpdate()

def auctionStatus():
    with open('auctionId.txt') as f:
        lines = f.readlines()
    for line in lines:
        updateAuctionQuery = f"""UPDATE fineart_auction_calendar SET faac_auction_published = 'yes' WHERE faac_auction_ID = {int(line)}"""
        connList = connectToDb()
        connList[1].execute(updateAuctionQuery)
        connList[0].commit()
        print(updateAuctionQuery)
    print('Done')
        

auctionStatus()
