import datetime
from threading import Thread
import MySQLdb

def connectToDb():
    dbConn = MySQLdb.connect(user="artb_Admin", passwd="cDLCntgtsjAOP%tw", host="191.101.0.14", port=3306, db="artb_Artbider_Prod")
    cursor = dbConn.cursor(MySQLdb.cursors.DictCursor)
    return dbConn, cursor


def disconnectDb(connList):
    connList[1].close
    connList[0].close()


def tableTruncater(truncateQuery):
    connList = connectToDb()
    connList[1].execute(truncateQuery)
    connList[0].commit()
    disconnectDb(connList)


def yoyTotalSaleForArtist():
    truncateThread = Thread(target=tableTruncater, args=("""TRUNCATE TABLE yoyTotalSaleAverage""", ))
    truncateThread.start()
    artistSelectQuery = f"""SELECT fa_artist_ID FROM fineart_artists"""
    truncateThread.join()
    connList = connectToDb()
    connList[1].execute(artistSelectQuery)
    artistsDataList = connList[1].fetchall()
    for artistData in artistsDataList:
        dataSelectQuery = f"""SELECT SUM(fal_lot_sale_price_USD) AS fal_lot_sale_price_USD_SUM, AVG(fal_lot_sale_price_USD) AS fal_lot_sale_price_USD_AVG, faa_artist_ID, YEAR(fal_lot_sale_date) AS fal_lot_sale_date_year FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID WHERE faa_artist_ID = {artistData['fa_artist_ID']} GROUP BY YEAR(fal_lot_sale_date);"""
        dataInsertQuery = f"""INSERT INTO yoyTotalSaleAverage (artistID, totalSale, saleAverage, saleYear) VALUES(%s, %s, %s, %s)"""
        connList[1].execute(dataSelectQuery)
        data = connList[1].fetchall()
        if data:
            dataList = []
            for rowData in data:
                dataList.append((rowData['faa_artist_ID'], rowData['fal_lot_sale_price_USD_SUM'] if rowData['fal_lot_sale_price_USD_SUM'] else '0', rowData['fal_lot_sale_price_USD_AVG'] if rowData['fal_lot_sale_price_USD_AVG'] else '0', rowData['fal_lot_sale_date_year']))
            connList[1].executemany(dataInsertQuery, dataList)
            connList[0].commit()
    disconnectDb(connList)


def artistAnnualPerformanceForArtist():
    truncateThread = Thread(target=tableTruncater, args=("""TRUNCATE TABLE artistAnnualPerformance""",))
    truncateThread.start()
    artistSelectQuery = f"""SELECT fa_artist_ID FROM fineart_artists"""
    truncateThread.join()
    connList = connectToDb()
    connList[1].execute(artistSelectQuery)
    artistsDataList = connList[1].fetchall()
    for artistData in artistsDataList:
        allLotsCountSelectQuery = f"""SELECT COUNT(fal_lot_ID) AS allLots, faa_artist_ID, YEAR(fal_lot_sale_date) AS fal_lot_sale_date_year FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID WHERE faa_artist_ID = {artistData['fa_artist_ID']} GROUP BY YEAR(fal_lot_sale_date);"""
        soldLotsCountSelectQuery = f"""SELECT COUNT(fal_lot_ID) AS soldLots, faa_artist_ID, YEAR(fal_lot_sale_date) AS fal_lot_sale_date_year FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID WHERE faa_artist_ID = {artistData['fa_artist_ID']} AND fal_lot_status = 'sold' GROUP BY YEAR(fal_lot_sale_date);"""
        unsoldLotsCountSelectQuery = f"""SELECT COUNT(fal_lot_ID) AS unsoldLots, faa_artist_ID, YEAR(fal_lot_sale_date) AS fal_lot_sale_date_year FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID WHERE faa_artist_ID = {artistData['fa_artist_ID']} AND fal_lot_status = 'yet to be sold' GROUP BY YEAR(fal_lot_sale_date);"""
        dataInsertQuery = f"""INSERT INTO artistAnnualPerformance(artistID, numberOfLotsOffered, numberOfLotsSold, numberOfLotsUnsold, lotsYear) VALUES(%s, %s, %s, %s, %s)"""
        connList[1].execute(allLotsCountSelectQuery)
        allLotsData = connList[1].fetchall()
        connList[1].execute(soldLotsCountSelectQuery)
        soldLotsData = connList[1].fetchall()
        connList[1].execute(unsoldLotsCountSelectQuery)
        unsoldLotsData = connList[1].fetchall()
        dataList = []
        for allLotRowData in allLotsData:
            numberOfLotsSold = 0
            numberOfLotsUnsold = 0
            for soldLotRowData in soldLotsData:
                if allLotRowData['fal_lot_sale_date_year'] == soldLotRowData['fal_lot_sale_date_year']:
                    numberOfLotsSold = soldLotRowData['soldLots']
            for unsoldLotRowData in unsoldLotsData:
                if allLotRowData['fal_lot_sale_date_year'] == unsoldLotRowData['fal_lot_sale_date_year']:
                    numberOfLotsUnsold = unsoldLotRowData['unsoldLots']
            dataList.append((allLotRowData['faa_artist_ID'], allLotRowData['allLots'], numberOfLotsSold, numberOfLotsUnsold, allLotRowData['fal_lot_sale_date_year']))
        connList[1].executemany(dataInsertQuery, dataList)
        connList[0].commit()
    disconnectDb(connList)

def main():
    yoyTotalSaleThread = Thread(target=yoyTotalSaleForArtist)
    yoyTotalSaleThread.start()
    artistAnnualPerformanceThread = Thread(target=artistAnnualPerformanceForArtist)
    artistAnnualPerformanceThread.start()
    yoyTotalSaleThread.join()
    artistAnnualPerformanceThread.join()


main()
