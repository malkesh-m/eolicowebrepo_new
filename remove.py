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
    nullAuctionImageSelectQuery = f"""SELECT faac_auction_ID FROM fineart_auction_calendar WHERE faac_auction_image = '3114852522.jpg' OR faac_auction_image IS NULL OR faac_auction_image = 'None' OR faac_auction_image = '' ORDER BY faac_auction_ID DESC"""
    connList = connectToDb()
    connList[1].execute(nullAuctionImageSelectQuery)
    nullAuctionImageDataList = connList[1].fetchall()
    for nullAuctionImageData in nullAuctionImageDataList:
        imageSelectQuery = f"""SELECT fal_lot_image1 FROM fineart_lots WHERE fal_auction_ID = {nullAuctionImageData['faac_auction_ID']} AND fal_lot_image1 IS NOT NULL AND fal_lot_image1 != '' LIMIT 1"""
        connList[1].execute(imageSelectQuery)
        imageData = connList[1].fetchone()
        if imageData:
            imageSource = imageData['fal_lot_image1']
        else:
            imageSource = None
        auctionImageUpdateQuery = f"""UPDATE fineart_auction_calendar SET faac_auction_image = %s WHERE faac_auction_ID = %s"""
        print(imageSource, nullAuctionImageData['faac_auction_ID'])
        connList[1].execute(auctionImageUpdateQuery, (imageSource, nullAuctionImageData['faac_auction_ID']))
        connList[0].commit()
    disconnectDb(connList)


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


def artistsReportGenerate():
    artistsSelectQuery = f"""SELECT fa_artist_ID, fa_artist_name, fa_artist_birth_year, fa_artist_death_year, fa_artist_nationality, fa_artist_genre FROM fineart_artists"""
    connList = connectToDb()
    connList[1].execute(artistsSelectQuery)
    artistsDataList = list(connList[1].fetchall())
    artistsDataFrame = pd.DataFrame(artistsDataList)
    artistsDataFrame.to_excel('D:\\artistsData.xlsx', index=False)


def artworksTesting():
    getArtworkSelectQuery = f"""SELECT faa_artwork_title, faa_artwork_ID FROM fineart_artworks WHERE faa_artwork_title LIKE '%\t%' OR faa_artwork_title LIKE '%\r%' OR faa_artwork_title LIKE '%\n%'"""
    connList = connectToDb()
    connList[1].execute(getArtworkSelectQuery)
    artworksDataList = connList[1].fetchall()
    print(artworksDataList)
    for artworkData in artworksDataList:
        artworkTitle = artworkData['faa_artwork_title'].replace('\t', '').replace('\n', '').replace('\r', '')
        updateArtworkQuery = f"""UPDATE fineart_artworks SET faa_artwork_title = %s WHERE faa_artwork_ID = %s"""
        print(updateArtworkQuery)
        connList[1].execute(updateArtworkQuery, (artworkTitle, artworkData['faa_artwork_ID']))
        connList[0].commit()
    disconnectDb(connList)


artworksTesting()
