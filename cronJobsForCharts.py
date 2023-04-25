import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import schedule
from threading import Thread
import MySQLdb
from statistics import median


def connectToDb():
    dbConn = MySQLdb.connect(user="artb_Admin", passwd="cDLCntgtsjAOP%tw", host="191.101.0.14", port=3306,
                             db="artb_Artbider_Prod")
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
        dataSelectQuery = f"""SELECT SUM(fal_lot_sale_price_USD) AS fal_lot_sale_price_USD_SUM, AVG(fal_lot_sale_price_USD) AS fal_lot_sale_price_USD_AVG, faa_artist_ID, YEAR(fal_lot_sale_date) AS fal_lot_sale_date_year FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID AND fal_lot_published = 'yes' WHERE faa_artist_ID = {artistData['fa_artist_ID']} AND fal_lot_status = 'sold' GROUP BY YEAR(fal_lot_sale_date);"""
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
        allLotsCountSelectQuery = f"""SELECT COUNT(fal_lot_ID) AS allLots, faa_artist_ID, YEAR(fal_lot_sale_date) AS fal_lot_sale_date_year FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID AND fal_lot_published = 'yes' WHERE faa_artist_ID = {artistData['fa_artist_ID']} GROUP BY YEAR(fal_lot_sale_date);"""
        soldLotsCountSelectQuery = f"""SELECT COUNT(fal_lot_ID) AS soldLots, faa_artist_ID, YEAR(fal_lot_sale_date) AS fal_lot_sale_date_year FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID AND fal_lot_published = 'yes' WHERE faa_artist_ID = {artistData['fa_artist_ID']} AND fal_lot_status = 'sold' GROUP BY YEAR(fal_lot_sale_date);"""
        unsoldLotsCountSelectQuery = f"""SELECT COUNT(fal_lot_ID) AS unsoldLots, faa_artist_ID, YEAR(fal_lot_sale_date) AS fal_lot_sale_date_year FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID AND fal_lot_published = 'yes' WHERE faa_artist_ID = {artistData['fa_artist_ID']} AND fal_lot_status = 'yet to be sold' GROUP BY YEAR(fal_lot_sale_date);"""
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
            dataList.append((allLotRowData['faa_artist_ID'], allLotRowData['allLots'], numberOfLotsSold,
                             numberOfLotsUnsold, allLotRowData['fal_lot_sale_date_year'], saleThroughRate))
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
        dataSelectQuery = f"""SELECT SUM(fal_lot_sale_price_USD) AS fal_lot_sale_price_USD_SUM, AVG(fal_lot_sale_price_USD) AS fal_lot_sale_price_USD_AVG, YEAR(fal_lot_sale_date) AS fal_lot_sale_date_year, faa_artist_ID, fal_lot_category FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID AND fal_lot_published = 'yes' WHERE faa_artist_ID = {artistData['fa_artist_ID']} AND fal_lot_category != '' AND fal_lot_status = 'sold' GROUP BY fal_lot_category, YEAR(fal_lot_sale_date);"""
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
        dataSelectQuery = f"""SELECT SUM(fal_lot_sale_price_USD) AS fal_lot_sale_price_USD_SUM, AVG(fal_lot_sale_price_USD) AS fal_lot_sale_price_USD_AVG, YEAR(fal_lot_sale_date) AS fal_lot_sale_date_year, faa_artist_ID, cah_auction_house_country FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID AND fal_lot_published = 'yes' INNER JOIN fineart_auction_calendar ON fal_auction_ID = faac_auction_ID AND faac_auction_published = 'yes' INNER JOIN core_auction_houses ON faac_auction_house_ID = cah_auction_house_ID WHERE faa_artist_ID = {artistData['fa_artist_ID']} AND fal_lot_status = 'sold' GROUP BY cah_auction_house_country, YEAR(fal_lot_sale_date);"""
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


def topPerformanceOfYearForArtMarket():
    truncateThread = Thread(target=tableTruncater,
                            args=("""DELETE FROM `topPerformanceOfYear` WHERE topPerformanceOfYearId > 0""",))
    truncateThread.start()
    yearSelectQuery = f"SELECT DISTINCT(YEAR(fal_lot_sale_date)) AS fal_lot_sale_date_year FROM fineart_lots WHERE fal_lot_published = 'yes'"
    truncateThread.join()
    connList = connectToDb()
    connList[1].execute(yearSelectQuery)
    yearsListData = connList[1].fetchall()
    for yearData in yearsListData:
        yearlySelectQuery = f"""SELECT YEAR(fal_lot_sale_date) AS fal_lot_sale_date_year, faa_artist_ID, SUM(fal_lot_sale_price_USD) AS fal_lot_sale_price_USD_SUM FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID AND fal_lot_published = 'yes' WHERE YEAR(fal_lot_sale_date) = {yearData['fal_lot_sale_date_year']} GROUP BY faa_artist_ID ORDER BY fal_lot_sale_price_USD_SUM DESC limit 5"""
        connList[1].execute(yearlySelectQuery)
        topArtistsListData = connList[1].fetchall()
        for topArtistData in topArtistsListData:
            yearlyInsertQuery = f"""INSERT INTO topPerformanceOfYear(artistID, totalSalePrice, saleYear) VALUES(%s, %s, %s)"""
            yearDataTuple = (topArtistData['faa_artist_ID'],
                             topArtistData['fal_lot_sale_price_USD_SUM'] if topArtistData[
                                 'fal_lot_sale_price_USD_SUM'] else 0, topArtistData['fal_lot_sale_date_year'])
            connList[1].execute(yearlyInsertQuery, yearDataTuple)
            connList[0].commit()
            connList[1].execute('SELECT LAST_INSERT_ID() AS topPerformanceOfYearId')
            topPerformanceOfYearData = connList[1].fetchone()
            monthlySelectQuery = f"""SELECT MONTH(fal_lot_sale_date) AS fal_lot_sale_date_month, SUM(fal_lot_sale_price_USD) AS fal_lot_sale_price_USD_SUM FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID AND fal_lot_published = 'yes' WHERE YEAR(fal_lot_sale_date) = {topArtistData['fal_lot_sale_date_year']} AND faa_artist_ID = {topArtistData['faa_artist_ID']} GROUP BY fal_lot_sale_date_month"""
            connList[1].execute(monthlySelectQuery)
            topArtistsListDataByMonth = connList[1].fetchall()
            for topArtistDataByMonth in topArtistsListDataByMonth:
                monthlyInsertQuery = f"""INSERT INTO topPerformanceOfYearByMonth(topPerformanceOfYearID, totalSalePriceByMonth, saleMonth) VALUES(%s, %s, %s)"""
                monthlyDataTuple = (topPerformanceOfYearData['topPerformanceOfYearId'],
                                    topArtistDataByMonth['fal_lot_sale_price_USD_SUM'] if topArtistDataByMonth[
                                        'fal_lot_sale_price_USD_SUM'] else 0,
                                    topArtistDataByMonth['fal_lot_sale_date_month'])
                connList[1].execute(monthlyInsertQuery, monthlyDataTuple)
                connList[0].commit()
    disconnectDb(connList)


def topLotsOfMonthForArtMarket():
    truncateThread = Thread(target=tableTruncater, args=("""TRUNCATE TABLE topLotsOfMonth""",))
    truncateThread.start()
    lotsSelectQuery = f"""SELECT fal_lot_ID FROM fineart_lots WHERE fal_lot_status = 'sold' AND MONTH(fal_lot_sale_date) = MONTH(NOW()) AND YEAR(fal_lot_sale_date) = YEAR(fal_lot_sale_date) AND fal_lot_published = 'yes' ORDER BY fal_lot_sale_price_USD LIMIT 5"""
    truncateThread.join()
    connList = connectToDb()
    connList[1].execute(lotsSelectQuery)
    lotsDataList = connList[1].fetchall()
    insertQuery = f"""INSERT INTO topLotsOfMonth(lotID, lotNum, currencyCode, lotHighEstimate, lotLowEstimate, lotSalePrice, lotHighEstimateUSD, lotLowEstimateUSD, lotSalePriceUSD, auctionTitle, artworkImage, artworkMaterial, artworkCategory, artworkTitle, artistName, auctionStartDate, auctionHouseName, auctionHouseLocation) VALUES (%s, %s, %s , %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    for lotData in lotsDataList:
        dataSelectQuery = f"""SELECT fal_lot_ID, fal_lot_no, cah_auction_house_currency_code, fal_lot_high_estimate, fal_lot_low_estimate, fal_lot_sale_price, fal_lot_high_estimate_USD, fal_lot_low_estimate_USD, fal_lot_sale_price_USD, faac_auction_title, faa_artwork_image1, faa_artwork_material, faac_auction_ID, faa_artwork_category, fal_artwork_ID, faa_artwork_title, fa_artist_ID, fa_artist_name, faac_auction_start_date, cah_auction_house_name, cah_auction_house_location FROM `fineart_lots` INNER JOIN `fineart_artworks` ON fal_artwork_ID = faa_artwork_ID AND fal_lot_published = 'yes' INNER JOIN `fineart_auction_calendar` ON fal_auction_ID = faac_auction_ID AND faac_auction_published = 'yes' INNER JOIN `fineart_artists` ON faa_artist_ID = fa_artist_ID INNER JOIN`core_auction_houses` ON faac_auction_house_ID = cah_auction_house_ID WHERE fal_lot_ID = {lotData['fal_lot_ID']}"""
        connList[1].execute(dataSelectQuery)
        data = connList[1].fetchone()
        dataList = []
        if data:
            dataList.append((data['fal_lot_ID'], data['fal_lot_no'], data['cah_auction_house_currency_code'],
                             data['fal_lot_high_estimate'] if data['fal_lot_high_estimate'] else '0',
                             data['fal_lot_low_estimate'] if data['fal_lot_low_estimate'] else '0',
                             data['fal_lot_sale_price'] if data['fal_lot_sale_price'] else '0',
                             data['fal_lot_high_estimate_USD'] if data['fal_lot_high_estimate_USD'] else '0',
                             data['fal_lot_low_estimate_USD'] if data['fal_lot_low_estimate_USD'] else '0',
                             data['fal_lot_sale_price_USD'] if data['fal_lot_sale_price_USD'] else '0',
                             data['faac_auction_title'], data['faa_artwork_image1'], data['faa_artwork_material'],
                             data['faa_artwork_category'], data['faa_artwork_title'], data['fa_artist_name'],
                             data['faac_auction_start_date'], data['cah_auction_house_name'],
                             data['cah_auction_house_location']))
        connList[1].executemany(insertQuery, dataList)
        connList[0].commit()
    disconnectDb(connList)


def topSalesOfMonthForArtMarket():
    truncateThread = Thread(target=tableTruncater, args=("""TRUNCATE TABLE topSalesOfMonth""",))
    truncateThread.start()
    auctionsSelectQuery = f"""SELECT fal_auction_ID FROM fineart_lots WHERE MONTH(fal_lot_sale_date) = MONTH(NOW()) AND YEAR(fal_lot_sale_date) = YEAR(NOW()) AND fal_lot_published = 'yes' GROUP BY fal_auction_ID ORDER BY SUM(fal_lot_sale_price_USD) DESC LIMIT 5"""
    truncateThread.join()
    connList = connectToDb()
    connList[1].execute(auctionsSelectQuery)
    auctionsDataList = connList[1].fetchall()
    dataInsertQuery = f"""INSERT INTO topSalesOfMonth(auctionID, auctionName, auctionHouseName, auctionHouseLocation, auctionImage, auctionStartDate, totalLotsOffered, totalLotsSold, sellThroughRate, soldPriceOverEstimate, totalSaleValue) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    dataList = []
    for auctionData in auctionsDataList:
        allLotsSelectQuery = f"""SELECT COUNT(fal_lot_ID) AS totalLotsOffered FROM fineart_lots WHERE fal_auction_ID = {auctionData['fal_auction_ID']}"""
        soldLotsSelectQuery = f"""SELECT COUNT(fal_lot_ID) AS totalLotsSold FROM fineart_lots WHERE fal_auction_ID = {auctionData['fal_auction_ID']} AND fal_lot_status = 'sold'"""
        totalSaleValueSelectQuery = f"""SELECT SUM(fal_lot_sale_price_USD) AS totalSaleValue FROM fineart_lots WHERE fal_auction_ID = {auctionData['fal_auction_ID']}"""
        highLowEstimateSelectQuery = f"""SELECT fal_lot_high_estimate_USD, fal_lot_low_estimate_USD FROM fineart_lots WHERE fal_auction_ID = {auctionData['fal_auction_ID']}"""
        auctionDetailsSelectQuery = f"""SELECT faac_auction_ID, faac_auction_title, faac_auction_start_date, faac_auction_image, cah_auction_house_name, cah_auction_house_location FROM fineart_auction_calendar INNER JOIN core_auction_houses ON faac_auction_house_ID = cah_auction_house_ID AND faac_auction_published = 'yes' WHERE faac_auction_ID = {auctionData['fal_auction_ID']}"""
        connList[1].execute(allLotsSelectQuery)
        totalLotsOffered = connList[1].fetchone()
        connList[1].execute(soldLotsSelectQuery)
        totalLotsSold = connList[1].fetchone()
        sellThroughRate = (totalLotsSold['totalLotsSold'] / totalLotsOffered['totalLotsOffered']) * 100
        connList[1].execute(totalSaleValueSelectQuery)
        totalSaleValue = connList[1].fetchone()
        connList[1].execute(highLowEstimateSelectQuery)
        highLowEstimate = connList[1].fetchall()
        sumOfHighLowEstimateMedian = 0
        for highLowData in highLowEstimate:
            sumOfHighLowEstimateMedian += median(
                [float(highLowData['fal_lot_low_estimate_USD']) if highLowData['fal_lot_low_estimate_USD'] else 0,
                 float(highLowData['fal_lot_high_estimate_USD']) if highLowData['fal_lot_high_estimate_USD'] else 0])
        soldPriceOverEstimate = (float(totalSaleValue['totalSaleValue']) / sumOfHighLowEstimateMedian) * 100
        connList[1].execute(auctionDetailsSelectQuery)
        auctionDetails = connList[1].fetchone()
        dataList.append((auctionDetails['faac_auction_ID'], auctionDetails['faac_auction_title'],
                         auctionDetails['cah_auction_house_name'], auctionDetails['cah_auction_house_location'],
                         auctionDetails['faac_auction_image'], auctionDetails['faac_auction_start_date'],
                         totalLotsOffered['totalLotsOffered'], totalLotsSold['totalLotsSold'], sellThroughRate,
                         soldPriceOverEstimate, totalSaleValue['totalSaleValue']))
    connList[1].executemany(dataInsertQuery, dataList)
    connList[0].commit()
    disconnectDb(connList)


def topArtistsOfMonthForArtMarket():
    truncateThread = Thread(target=tableTruncater, args=("""TRUNCATE TABLE topArtistsOfMonth""",))
    truncateThread.start()
    auctionsSelectQuery = f"""SELECT faa_artist_ID FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID AND fal_lot_published = 'yes' WHERE MONTH(fal_lot_sale_date) = MONTH(NOW()) AND YEAR(fal_lot_sale_date) = YEAR(NOW()) GROUP BY faa_artist_ID ORDER BY SUM(fal_lot_sale_price_USD) DESC LIMIT 5"""
    truncateThread.join()
    connList = connectToDb()
    connList[1].execute(auctionsSelectQuery)
    artistsDataList = connList[1].fetchall()
    dataInsertQuery = f"""INSERT INTO topArtistsOfMonth(artistID, artistName, artistImage, TotalSaleOfThisYear, averageSalePriceUSD, sellThroughRate, soldPriceAboveEstimate) VALUES(%s, %s, %s, %s, %s, %s, %s)"""
    dataList = []
    for artistData in artistsDataList:
        artistDetailsSelectQuery = f"""SELECT fa_artist_name, fa_artist_image FROM fineart_artists WHERE fa_artist_ID = {artistData['faa_artist_ID']}"""
        totalSaleSelectQuery = f"""SELECT SUM(fal_lot_sale_price_USD) AS totalSaleOfThisYear, COUNT(fal_lot_ID) AS TotalSoldLots FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID AND fal_lot_published = 'yes' WHERE YEAR(fal_lot_sale_date) = YEAR(NOW()) AND faa_artist_ID = {artistData['faa_artist_ID']} AND fal_lot_status = 'sold'"""
        totalLotsSelectQuery = f"""SELECT COUNT(fal_lot_ID) AS totalLots FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID AND fal_lot_published = 'yes' WHERE faa_artist_ID = {artistData['faa_artist_ID']} AND YEAR(fal_lot_sale_date) = YEAR(NOW())"""
        highLowMedianSelectQuery = f"""SELECT fal_lot_high_estimate_USD, fal_lot_low_estimate_USD, fal_lot_sale_price_USD FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID AND fal_lot_published = 'yes' WHERE faa_artist_ID = {artistData['faa_artist_ID']} AND MONTH(fal_lot_sale_date) = MONTH(NOW()) AND YEAR(fal_lot_sale_date) = YEAR(NOW())"""
        connList[1].execute(artistDetailsSelectQuery)
        artistDetails = connList[1].fetchone()
        connList[1].execute(totalSaleSelectQuery)
        totalSale = connList[1].fetchone()
        averageSalePrice = float(totalSale['totalSaleOfThisYear']) / float(totalSale['totalSoldLots'])
        connList[1].execute(totalLotsSelectQuery)
        totalLots = connList[1].fetchone()
        sellThroughRate = (float(totalSale['totalSoldLots']) / float(totalLots['totalLots'])) * 100
        connList[1].execute(highLowMedianSelectQuery)
        highLowMedian = connList[1].fetchall()
        sumOfHighLowEstimateMedian = 0
        sumOfSalePrice = 0
        for highLowData in highLowMedian:
            sumOfSalePrice += float(highLowData['fal_lot_sale_price_USD'])
            sumOfHighLowEstimateMedian += median(
                [float(highLowData['fal_lot_low_estimate_USD']) if highLowData['fal_lot_low_estimate_USD'] else 0,
                 float(highLowData['fal_lot_high_estimate_USD']) if highLowData['fal_lot_high_estimate_USD'] else 0])
        soldPriceOverEstimate = (sumOfSalePrice / sumOfHighLowEstimateMedian) * 100
        dataList.append((artistData['faa_artist_ID'], artistDetails['fa_artist_name'], artistDetails['fa_artist_image'],
                         totalSale['totalSaleOfThisYear'], averageSalePrice, sellThroughRate, soldPriceOverEstimate))
    connList[1].executemany(dataInsertQuery, dataList)
    connList[0].commit()
    disconnectDb(connList)


def topGeographicalLocationsForArtMarket():
    truncateThread = Thread(target=tableTruncater, args=("""TRUNCATE TABLE topGeographicalLocations""",))
    truncateThread.start()
    yearSelectQuery = f"SELECT DISTINCT(YEAR(fal_lot_sale_date)) AS fal_lot_sale_date_year FROM fineart_lots"
    truncateThread.join()
    connList = connectToDb()
    connList[1].execute(yearSelectQuery)
    yearsListData = connList[1].fetchall()
    dataInsertQuery = f"""INSERT INTO topGeographicalLocations(auctionHouseCountry, totalSalePrice, saleYear) VALUES(%s, %s, %s)"""
    for yearData in yearsListData:
        dataList = []
        selectQuery = f"""SELECT cah_auction_house_country, SUM(fal_lot_sale_price_USD) fal_lot_sale_price_USD_SUM FROM fineart_lots INNER JOIN fineart_auction_calendar ON fal_auction_ID = faac_auction_ID AND fal_lot_published = 'yes' AND faac_auction_published = 'yes' AND YEAR(fal_lot_sale_date) = {yearData['fal_lot_sale_date_year']} AND fal_lot_status = 'sold' INNER JOIN core_auction_houses ON faac_auction_house_ID = cah_auction_house_ID GROUP BY cah_auction_house_country ORDER BY fal_lot_sale_price_USD_SUM DESC LIMIT 10"""
        connList[1].execute(selectQuery)
        topGeographicalLocationsDataList = connList[1].fetchall()
        for topGeographicalLocationsData in topGeographicalLocationsDataList:
            dataList.append((topGeographicalLocationsData['cah_auction_house_country'],
                             topGeographicalLocationsData['fal_lot_sale_price_USD_SUM'] if topGeographicalLocationsData[
                                 'fal_lot_sale_price_USD_SUM'] else 0, yearData['fal_lot_sale_date_year']))
        connList[1].executemany(dataInsertQuery, dataList)
        connList[0].commit()
    disconnectDb(connList)


def sendEmail(htmlData):
    print('email sending')
    recieverEmail = 'umang2in@gmail.com'
    hostEmail = 'contactus@artbider.com'
    hostEmailPassword = 'Welcome#2023'
    hostEmailHostName = 'smtp.hostinger.com'
    hostEmailPort = 587
    msg = MIMEMultipart()
    msg['From'] = hostEmail
    msg['To'] = recieverEmail
    msg['Subject'] = "Unmatched HEX count"
    msg.attach(MIMEText(htmlData, 'html'))
    server = smtplib.SMTP(hostEmailHostName, hostEmailPort)
    server.starttls()
    server.login(hostEmail, hostEmailPassword)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
    print('email sent')


def htmlDataBinderForEmail(allArtistsDataList, userDetailDict):
    htmlData = f"""<!DOCTYPE html>
<html>

<head>
    <title>My Email</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>

<body style="font-family: Arial, sans-serif; font-size: 16px; line-height: 1.5; color: #333333; background-color: #f2f2f2; margin: 0; padding: 0;">
    <div class="container" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1); box-sizing: border-box;">
        <div class="header" style="display: flex; justify-content: space-between; margin-bottom: 20px; background-color: #E7e9f0; padding: 20px 30px; display: flex; align-items: center;">
            <h1 style="font-size: 24px; margin-top: 0; margin-bottom: 0;">My Email</h1>
            <h6 style="font-size: 15px; font-weight: 600; margin-top: 0; margin-bottom: 0;">Your Alert for {datetime.datetime.now().date()}</h6>
        </div>
        <div class="content" style="margin-bottom: 20px; padding: 0 50px;">
            <h2 style=" margin-top: 0; font-size: 30px; font-weight: 600; margin-bottom: 10px;"><span style="font-size: 24px; font-weight: 500;">Dear</span> {userDetailDict['username']}</h2>
            <p style=" margin: 0px; font-size: 15px;">The Following Artists in your collection have new artworks available</p>"""
    for rowArtistData in allArtistsDataList:
        htmlData += f"""<div class="mail-contani">
                <h2 style="font-size: 24px; font-weight: 600; margin: 10px 0 0 0;">{rowArtistData['artistName']}</h2>"""
        for rowSaleData in rowArtistData['saleDetails']:
            htmlData += f"""
                <h5 style="font-size: 15px; font-weight: 500; margin: 5px 0 0 0;"><span style="font-size: 18px; font-weight: 600; margin: 0;">{rowSaleData['lotsCountInSale']}</span> lots in {rowSaleData['auctionTitle']} sale</h5>
                <div class="mail-inner" style=" display: flex;">
                    <h6 style="font-size: 15px; margin: 6px 15px 0 0; font-weight: 600;">{rowSaleData['auctionHouseName']}</h6>
                    <h6 style="font-size: 15px; margin: 6px 15px 0 0; font-weight: 600;">{rowSaleData['auctionHouseLocation']}</h6>
                    <h6 style="font-size: 15px; margin: 6px 15px 0 0; font-weight: 600;">{rowSaleData['auctionSaleStartDate']}</h6>
                </div>
                <div class="mail-img" style="display: flex; justify-content: space-between;">"""
            for rowLotData in rowSaleData['lotData']:
                lotTitle = rowLotData['lotTitle']
                if len(lotTitle) > 18:
                    lotTitle = lotTitle[0:15] + '...'
                htmlData += f"""
                    <div class="img-contain" style="margin-right: 10px; margin-top: 15px; border: 1px solid #e1e1e1; border-radius: 10px;">
                        <img src="{rowLotData['lotImage']}" alt="" style="width: 200px; height:170px; border-radius: 10px 10px 0 0;">
                        <div class="img-text" style="padding: 0 10px 10px 10px;">
                            <h5 style="font-size: 20px; font-weight: 600; margin: 0 0 10px 0;">{lotTitle}</h5>
                            <a style="padding: 10px 30px; border: 0; font-size: 15px; font-weight: 500; background-color: #17375e; color: #ffffff; display: inline-block;">View Lot</a>
                        </div>
                    </div>"""
            htmlData += """</div>"""
        htmlData += """</div>"""
    htmlData += """<div style="text-align: center;">
                <a style="padding: 10px 30px; border: 0; font-size: 15px; font-weight: 500; background-color: #17375e; color: #ffffff; display: inline-block; margin-top: 20px; text-decoration:none;" href="http://localhost:8000/artist/index/">FOLLOW MORE ARTISTS</a>
            </div>
    </div>
        <div class="footer" style="background-color: #E7e9f0; padding: 20px 30px;">
            <div class="follow-contain" style="text-align: center;">
                <div class="logo">
                    <h1 style="margin: 0 0 10px 0;">mail</h1>
                </div>
                <div class="social-icon" style="display: flex; justify-content: center; margin-bottom: 15px;">
                    <a target="_blank" href="#" style="display: contents;">
                        <img src="image/instragram.png" alt="" style="width: 5%; padding: 0 5px;">
                    </a>
                    <a target="_blank" href="#" style="display: contents;">
                        <img src="image/facebook.png" alt="" style="width: 5%; padding: 0 5px;">
                    </a>
                    <a target="_blank" href="#" style="display: contents;">
                        <img src="image/linkdin.png" alt="" style="width: 5%; padding: 0 5px;">
                    </a>
                    <a target="_blank" href="#" style="display: contents;">
                        <img src="image/pintrest.png" alt="" style="width: 5%; padding: 0 5px;">
                    </a>
                </div>
                <h6 style="font-size: 16px; margin: 0;">Copyright © 2022 All rights reserved.</h6>
                <p style="font-size: 14px; width: 90%; margin: auto; margin: 5px 0 0 0;">Artbider respects your right to privacy. We sent you this email message
                    because you have signed up to receive emails from MutualArt. This email
                    may include advertising or promotional content. If you want to be
                    removed from this email list, please unsubscribe here.</p>
            </div>
        </div>
    </div>
</body>

</html>"""
    sendEmail(htmlData)


def emailAlert():
    usersSelectQuery = f"""SELECT DISTINCT(user_id) AS userId FROM `user_favorites` WHERE reference_table = 'fineart_artists'"""
    connList = connectToDb()
    connList[1].execute(usersSelectQuery)
    usersDataList = connList[1].fetchall()
    for userData in usersDataList:
        allDataList = []
        userDetailsDict = {}
        artistsSelectQuery = f"""SELECT referenced_table_id AS artistId FROM user_favorites WHERE user_id = {userData['userId']} AND reference_table = 'fineart_artists'"""
        connList[1].execute(artistsSelectQuery)
        artistsDataList = connList[1].fetchall()
        for artistData in artistsDataList:
            artistDataDict = {}
            saleCountsDataList = []
            artistNameSelectQuery = f"""SELECT fa_artist_name FROM fineart_artists WHERE fa_artist_ID = {artistData['artistId']}"""
            connList[1].execute(artistNameSelectQuery)
            rowArtistDataDict = connList[1].fetchone()
            datetimeObj = datetime.datetime.now() - datetime.timedelta(hours=24)
            datetimeObj = datetimeObj.strftime('%Y-%m-%d %H:%M:%S')
            upcomingSalesSelectQuery = f"""SELECT COUNT(fal_lot_ID) AS lotCounts, fal_auction_ID FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID AND faa_artist_ID = {artistData['artistId']} AND fal_lot_published = 'yes' GROUP BY fal_auction_ID"""
            connList[1].execute(upcomingSalesSelectQuery)
            salesDataList = connList[1].fetchall()
            for saleData in salesDataList:
                auctionDetailsSelectQuery = f"""SELECT TRIM(faac_auction_title) AS faac_auction_title, cah_auction_house_name, cah_auction_house_location, faac_auction_start_date FROM fineart_auction_calendar INNER JOIN core_auction_houses ON faac_auction_house_ID = cah_auction_house_ID AND faac_auction_ID = {saleData['fal_auction_ID']}"""
                connList[1].execute(auctionDetailsSelectQuery)
                auctionDetailsData = connList[1].fetchone()
                artistDataDict['artistName'] = rowArtistDataDict['fa_artist_name']
                saleDataDict = {'auctionTitle': auctionDetailsData['faac_auction_title'],
                                'auctionHouseName': auctionDetailsData['cah_auction_house_name'],
                                'auctionHouseLocation': auctionDetailsData['cah_auction_house_location'],
                                'auctionSaleStartDate': auctionDetailsData['faac_auction_start_date'],
                                'lotsCountInSale': saleData['lotCounts']}
                notificationLogsInsertQuery = f"""INSERT INTO notificationLogs(userId, artistId, auctionId, lotsCounts) VALUES({userData['userId']}, {artistData['artistId']}, {saleData['fal_auction_ID']}, '{saleData['lotCounts']}')"""
                print(notificationLogsInsertQuery)
                connList[1].execute(notificationLogsInsertQuery)
                connList[0].commit()
                lotsDetailsList = []
                upcomingLotsSelectQuery = f"""SELECT fal_lot_ID, fal_lot_image1, faa_artwork_title FROM fineart_lots INNER JOIN fineart_artworks ON fal_artwork_ID = faa_artwork_ID AND faa_artist_ID = {artistData['artistId']} AND fal_lot_published = 'yes' AND fal_auction_ID = {saleData['fal_auction_ID']}"""
                connList[1].execute(upcomingLotsSelectQuery)
                upcomingLotsDataList = connList[1].fetchall()
                for upcomingLotData in upcomingLotsDataList:
                    lotDataDict = {'lotId': upcomingLotData['fal_lot_ID'],
                               'lotTitle': upcomingLotData['faa_artwork_title'],
                                   'lotImage': f"https://f000.backblazeb2.com/file/fineart-images/{upcomingLotData['fal_lot_image1']}"}
                    lotsDetailsList.append(lotDataDict)
                    userSelectQuery = f"""SELECT user_id, login_email, username FROM user_accounts WHERE user_id = {userData['userId']}"""
                    connList[1].execute(userSelectQuery)
                    userEmailData = connList[1].fetchone()
                    userDetailsDict['userId'], userDetailsDict['email'], userDetailsDict['username'] = userEmailData[
                        'user_id'], userEmailData['login_email'], userEmailData['username']
                    break
                saleDataDict['lotData'] = lotsDetailsList
                saleCountsDataList.append(saleDataDict)
                break
            if salesDataList:
                artistDataDict['saleDetails'] = saleCountsDataList
                allDataList.append(artistDataDict)
        htmlDataBinderForEmail(allDataList, userDetailsDict)
        break
    disconnectDb(connList)


def dailyCronJobs():
    yoyTotalSaleThread = Thread(target=yoyTotalSaleForArtist)
    yoyTotalSaleThread.start()

    artistAnnualPerformanceThread = Thread(target=artistAnnualPerformanceForArtist)
    artistAnnualPerformanceThread.start()

    yoySellingCategoryThread = Thread(target=yoySellingCategoryForArtist)
    yoySellingCategoryThread.start()

    artistPerformanceByCountryThread = Thread(target=artistPerformanceByCountryForArtist)
    artistPerformanceByCountryThread.start()

    topPerformanceOfYearThread = Thread(target=topPerformanceOfYearForArtMarket)
    topPerformanceOfYearThread.start()

    topGeographicalLocationsThread = Thread(target=topGeographicalLocationsForArtMarket)
    topGeographicalLocationsThread.start()

    yoyTotalSaleThread.join()
    artistAnnualPerformanceThread.join()
    yoySellingCategoryThread.join()
    artistPerformanceByCountryThread.join()
    topPerformanceOfYearThread.join()
    topGeographicalLocationsThread.join()


def monthlyCronJobs():
    topArtistsOfMonthThread = Thread(target=topArtistsOfMonthForArtMarket)
    topArtistsOfMonthThread.start()

    topLotsOfMonthThread = Thread(target=topLotsOfMonthForArtMarket)
    topLotsOfMonthThread.start()

    topSalesOfMonthThread = Thread(target=topSalesOfMonthForArtMarket)
    topSalesOfMonthThread.start()

    topArtistsOfMonthThread.join()
    topLotsOfMonthThread.join()
    topSalesOfMonthThread.join()


def main():
    pass


emailAlert()
