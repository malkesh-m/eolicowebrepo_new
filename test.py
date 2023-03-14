from eolicowebsite.utils import connectToDb, disconnectDb

NullAuctionSelectQuery = f"""SELECT faac_auction_ID FROM `fineart_auction_calendar` WHERE faac_auction_lot_count IS NULL;"""
connList = connectToDb()
connList[1].execute(NullAuctionSelectQuery)
nullAuctionDataList = connList[1].fetchall()
disconnectDb(connList)

for nullAuctionData in nullAuctionDataList:
    lotCountSelectQuery = f"""SELECT COUNT(fal_lot_ID) as fal_lot_counts FROM `fineart_lots` WHERE fal_auction_ID = {nullAuctionData['faac_auction_ID']};"""
    connList = connectToDb()
    try:
        connList[1].execute(lotCountSelectQuery)
        counter = connList[1].fetchone()
        nullUpdateQuery = f"""UPDATE `fineart_auction_calendar` SET faac_auction_lot_count = {counter['fal_lot_counts']} WHERE faac_auction_ID = {nullAuctionData['faac_auction_ID']};"""
        connList[1].execute(nullUpdateQuery)
        connList[0].commit()
        print(nullAuctionData, counter)
    except Exception as e:
        print("ERROR:- ", e)
        connList[0].rollback()
    finally:
        disconnectDb(connList)
print(counter)
