import datetime
from threading import Thread
import MySQLdb


def connectToDb():
    dbConn = MySQLdb.connect(user="artb_Admin", passwd="cDLCntgtsjAOP%tw", host="191.101.0.14", port=3306, db="artb_Artbider_Prod")
    cursor = dbConn.cursor(MySQLdb.cursors.DictCursor)
    return dbConn, cursor


def disconnectDb(connList):
    connList[1].close()
    connList[0].close()


def tableTruncater(truncateQuery):
    connList = connectToDb()
    connList[1].execute(truncateQuery)
    connList[0].commit()
    disconnectDb(connList)


def yoyTotalSaleForArtist():
    truncateThread = Thread(target=tableTruncater, args=("""TRUNCATE TABLE yoyTotalSaleAverage""",))
    truncateThread.start()
    artistSelectQuery = f"""SELECT fa_artist_ID FROM fineart_artists"""
    truncateThread.join()
    connList = connectToDb()
    connList[1].execute(artistSelectQuery)
    artistsDataList = connList[1].fetchall()
    dataInsertQuery = f"""INSERT INTO yoyTotalSaleAverage (artistID, totalSale, saleAverage, saleYear) VALUES(%s, %s, %s, %s)"""
    for artistData in artistsDataList:
        dataSelectQuery = f"""SELECT SUM(fal_lot_sale_price_USD) AS fal_lot_sale_price_USD_SUM, AVG(fal_lot_sale_price_USD) AS fal_lot_sale_price_USD_AVG, faa_artist_ID, YEAR(fal_lot_sale_date) AS fal_lot_sale_date_year FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID WHERE faa_artist_ID = {artistData['fa_artist_ID']} AND fal_lot_status = 'sold' GROUP BY YEAR(fal_lot_sale_date);"""
        connList[1].execute(dataSelectQuery)
        data = connList[1].fetchall()
        if data:
            dataList = []
            for rowData in data:
                dataList.append((rowData['faa_artist_ID'], rowData['fal_lot_sale_price_USD_SUM'] if rowData[
                    'fal_lot_sale_price_USD_SUM'] else '0', rowData['fal_lot_sale_price_USD_AVG'] if rowData[
                    'fal_lot_sale_price_USD_AVG'] else '0', rowData['fal_lot_sale_date_year']))
            connList[1].executemany(dataInsertQuery, dataList)
            connList[0].commit()
        break
    disconnectDb(connList)


def artistAnnualPerformanceForArtist():
    truncateThread = Thread(target=tableTruncater, args=("""TRUNCATE TABLE artistAnnualPerformance""",))
    truncateThread.start()
    artistSelectQuery = f"""SELECT fa_artist_ID FROM fineart_artists"""
    truncateThread.join()
    connList = connectToDb()
    connList[1].execute(artistSelectQuery)
    artistsDataList = connList[1].fetchall()
    dataInsertQuery = f"""INSERT INTO artistAnnualPerformance(artistID, numberOfLotsOffered, numberOfLotsSold, numberOfLotsUnsold, lotsYear, saleThroughRate) VALUES(%s, %s, %s, %s, %s, %s)"""
    for artistData in artistsDataList:
        allLotsCountSelectQuery = f"""SELECT COUNT(fal_lot_ID) AS allLots, faa_artist_ID, YEAR(fal_lot_sale_date) AS fal_lot_sale_date_year FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID WHERE faa_artist_ID = {artistData['fa_artist_ID']} GROUP BY YEAR(fal_lot_sale_date);"""
        soldLotsCountSelectQuery = f"""SELECT COUNT(fal_lot_ID) AS soldLots, faa_artist_ID, YEAR(fal_lot_sale_date) AS fal_lot_sale_date_year FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID WHERE faa_artist_ID = {artistData['fa_artist_ID']} AND fal_lot_status = 'sold' GROUP BY YEAR(fal_lot_sale_date);"""
        unsoldLotsCountSelectQuery = f"""SELECT COUNT(fal_lot_ID) AS unsoldLots, faa_artist_ID, YEAR(fal_lot_sale_date) AS fal_lot_sale_date_year FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID WHERE faa_artist_ID = {artistData['fa_artist_ID']} AND fal_lot_status = 'yet to be sold' GROUP BY YEAR(fal_lot_sale_date);"""
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
            saleThroughRate = 0
            for soldLotRowData in soldLotsData:
                if allLotRowData['fal_lot_sale_date_year'] == soldLotRowData['fal_lot_sale_date_year']:
                    numberOfLotsSold = soldLotRowData['soldLots']
                    saleThroughRate = (numberOfLotsSold / allLotRowData['allLots']) * 100
            for unsoldLotRowData in unsoldLotsData:
                if allLotRowData['fal_lot_sale_date_year'] == unsoldLotRowData['fal_lot_sale_date_year']:
                    numberOfLotsUnsold = unsoldLotRowData['unsoldLots']
            dataList.append((allLotRowData['faa_artist_ID'], allLotRowData['allLots'], numberOfLotsSold, numberOfLotsUnsold, allLotRowData['fal_lot_sale_date_year'], saleThroughRate))
        connList[1].executemany(dataInsertQuery, dataList)
        connList[0].commit()
    disconnectDb(connList)


def yoySellingCategoryForArtist():
    truncateThread = Thread(target=tableTruncater, args=("""TRUNCATE TABLE yoySellingCategory""",))
    truncateThread.start()
    artistSelectQuery = f"""SELECT fa_artist_ID FROM fineart_artists"""
    truncateThread.join()
    connList = connectToDb()
    connList[1].execute(artistSelectQuery)
    artistsDataList = connList[1].fetchall()
    dataInsertQuery = f"""INSERT INTO yoySellingCategory(artistID, totalSalePrice, averageSalePrice, lotsCategory, lotsYear) VALUES(%s, %s, %s, %s, %s)"""
    for artistData in artistsDataList:
        dataSelectQuery = f"""SELECT SUM(fal_lot_sale_price_USD) AS fal_lot_sale_price_USD_SUM, AVG(fal_lot_sale_price_USD) AS fal_lot_sale_price_USD_AVG, YEAR(fal_lot_sale_date) AS fal_lot_sale_date_year, faa_artist_ID, fal_lot_category FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID WHERE faa_artist_ID = {artistData['fa_artist_ID']} AND fal_lot_category != '' AND fal_lot_status = 'sold' GROUP BY fal_lot_category, YEAR(fal_lot_sale_date);"""
        connList[1].execute(dataSelectQuery)
        data = connList[1].fetchall()
        if data:
            dataList = []
            for rowData in data:
                dataList.append((rowData['faa_artist_ID'], rowData['fal_lot_sale_price_USD_SUM'] if rowData[
                    'fal_lot_sale_price_USD_SUM'] else '0', rowData['fal_lot_sale_price_USD_AVG'] if rowData[
                    'fal_lot_sale_price_USD_AVG'] else '0', rowData['fal_lot_category'],
                    rowData['fal_lot_sale_date_year']))
            connList[1].executemany(dataInsertQuery, dataList)
            connList[0].commit()
    disconnectDb(connList)


def artistPerformanceByCountryForArtist():
    truncateThread = Thread(target=tableTruncater, args=("""TRUNCATE TABLE artistPerformanceByCountry""",))
    truncateThread.start()
    artistSelectQuery = f"""SELECT fa_artist_ID FROM fineart_artists"""
    truncateThread.join()
    connList = connectToDb()
    connList[1].execute(artistSelectQuery)
    artistsDataList = connList[1].fetchall()
    dataInsertQuery = f"""INSERT INTO artistPerformanceByCountry(artistID, totalSalePrice, averageSalePrice, lotsCountry, lotsYear) VALUES(%s, %s, %s, %s, %s)"""
    for artistData in artistsDataList:
        dataSelectQuery = f"""SELECT SUM(fal_lot_sale_price_USD) AS fal_lot_sale_price_USD_SUM, AVG(fal_lot_sale_price_USD) AS fal_lot_sale_price_USD_AVG, YEAR(fal_lot_sale_date) AS fal_lot_sale_date_year, faa_artist_ID, cah_auction_house_country FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID INNER JOIN fineart_auction_calendar ON fal_auction_ID = faac_auction_ID INNER JOIN core_auction_houses ON faac_auction_house_ID = cah_auction_house_ID WHERE faa_artist_ID = {artistData['fa_artist_ID']} AND fal_lot_status = 'sold' GROUP BY cah_auction_house_country, YEAR(fal_lot_sale_date);"""
        connList[1].execute(dataSelectQuery)
        data = connList[1].fetchall()
        if data:
            dataList = []
            for rowData in data:
                dataList.append((rowData['faa_artist_ID'], rowData['fal_lot_sale_price_USD_SUM'] if rowData[
                    'fal_lot_sale_price_USD_SUM'] else '0', rowData['fal_lot_sale_price_USD_AVG'] if rowData[
                    'fal_lot_sale_price_USD_AVG'] else '0', rowData['cah_auction_house_country'],
                                 rowData['fal_lot_sale_date_year']))
            connList[1].executemany(dataInsertQuery, dataList)
            connList[0].commit()
    disconnectDb(connList)


def topLotsOfMonthsForArtMarket():
    truncateThread = Thread(target=tableTruncater, args=("""TRUNCATE TABLE topLotsOfMonth""",))
    truncateThread.start()
    lotsSelectQuery = f"""SELECT fal_lot_ID FROM fineart_lots WHERE fal_lot_status = 'sold' AND MONTH(fal_lot_sale_date) = MONTH(NOW()) AND YEAR(fal_lot_sale_date) = YEAR(fal_lot_sale_date) ORDER BY fal_lot_sale_price_USD LIMIT 5"""
    truncateThread.join()
    connList = connectToDb()
    connList[1].execute(lotsSelectQuery)
    lotsDataList = connList[1].fetchall()
    insertQuery = f"""INSERT INTO topLotsOfMonth(lotID, lotNum, currencyCode, lotHighEstimate, lotLowEstimate, lotSalePrice, lotHighEstimateUSD, lotLowEstimateUSD, lotSalePriceUSD, auctionTitle, artworkImage, artworkMaterial, artworkCategory, artworkTitle, artistName, auctionStartDate, auctionHouseName, auctionHouseLocation) VALUES (%s, %s, %s , %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    for lotData in lotsDataList:
        dataSelectQuery = f"""SELECT fal_lot_ID, fal_lot_no, cah_auction_house_currency_code, fal_lot_high_estimate, fal_lot_low_estimate, fal_lot_sale_price, fal_lot_high_estimate_USD, fal_lot_low_estimate_USD, fal_lot_sale_price_USD, faac_auction_title, faa_artwork_image1, faa_artwork_material, faac_auction_ID, faa_artwork_category, fal_artwork_ID, faa_artwork_title, fa_artist_ID, fa_artist_name, faac_auction_start_date, cah_auction_house_name, cah_auction_house_location FROM `fineart_lots` INNER JOIN `fineart_artworks` ON fal_artwork_ID = faa_artwork_ID INNER JOIN `fineart_auction_calendar` ON fal_auction_ID = faac_auction_ID INNER JOIN `fineart_artists` ON faa_artist_ID = fa_artist_ID INNER JOIN`core_auction_houses` ON faac_auction_house_ID = cah_auction_house_ID WHERE fal_lot_ID = {lotData['fal_lot_ID']}"""
        connList[1].execute(dataSelectQuery)
        data = connList[1].fetchone()
        dataList = []
        if data:
            dataList.append((data['fal_lot_ID'], data['fal_lot_no'], data['cah_auction_house_currency_code'], data['fal_lot_high_estimate'] if data['fal_lot_high_estimate'] else '0', data['fal_lot_low_estimate'] if data['fal_lot_low_estimate'] else '0', data['fal_lot_sale_price'] if data['fal_lot_sale_price'] else '0', data['fal_lot_high_estimate_USD'] if data['fal_lot_high_estimate_USD'] else '0', data['fal_lot_low_estimate_USD'] if data['fal_lot_low_estimate_USD'] else '0', data['fal_lot_sale_price_USD'] if data['fal_lot_sale_price_USD'] else '0', data['faac_auction_title'], data['faa_artwork_image1'], data['faa_artwork_material'], data['faa_artwork_category'], data['faa_artwork_title'], data['fa_artist_name'], data['faac_auction_start_date'], data['cah_auction_house_name'], data['cah_auction_house_location']))
        connList[1].executemany(insertQuery, dataList)
        connList[0].commit()
    disconnectDb(connList)


def topSalesOfMonth():
    truncateThread = Thread(target=tableTruncater, args=("""TRUNCATE TABLE topSalesOfMonth""",))
    truncateThread.start()
    auctionsSelectQuery = f"""SELECT fal_auction_ID FROM fineart_lots WHERE fal_lot_status = 'sold' AND MONTH(fal_lot_sale_date) = MONTH(NOW()) GROUP BY fal_auction_ID ORDER BY SUM(fal_lot_sale_price_USD) DESC LIMIT 5"""
    truncateThread.join()
    connList = connectToDb()
    connList[1].execute(auctionsSelectQuery)
    auctionsDataList = connList[1].fetchall()
    dataInsertQuery = f""""""
    for auctionData in auctionsDataList:
        pass


def main():
    artistAnnualPerformanceThread = Thread(target=artistAnnualPerformanceForArtist)
    yoyTotalSaleThread = Thread(target=yoyTotalSaleForArtist)
    yoySellingCategoryThread = Thread(target=yoySellingCategoryForArtist)
    artistPerformanceByCountryThread = Thread(target=artistPerformanceByCountryForArtist)
    yoyTotalSaleThread.start()
    artistAnnualPerformanceThread.start()
    yoySellingCategoryThread.start()
    artistPerformanceByCountryThread.start()
    yoyTotalSaleThread.join()
    artistAnnualPerformanceThread.join()
    yoySellingCategoryThread.join()
    artistPerformanceByCountryThread.join()


# main()
topLotsOfMonthsForArtMarket()
