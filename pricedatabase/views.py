import datetime
import itertools
import re
import sys
import urllib
import stripe
import redis
import simplejson as json
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from artists.models import Artist, Artwork
from auctionhouses.models import AuctionHouse
from auctions.models import Auction, Lot
from eolicowebsite.utils import connecttoDB, connectToDb, disconnectDb
from login.views import default

# Caching related imports and variables

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


def removecontrolcharacters(s):
    all_chars = (chr(i) for i in range(sys.maxunicode))
    categories = {'Cc'}
    control_chars = ''.join(map(chr, itertools.chain(range(0x00, 0x20), range(0x7f, 0xa0))))
    control_char_re = re.compile('[%s]' % re.escape(control_chars))
    return control_char_re.sub('', s)


def advanceSearchPriceDatabase(artistName, artworkTitle, workOnPaper, sculpture, painting, installation, photography,
                               miniaturesArt, textTilesArt, others, selArtworkStart, selArtworkEnd, selAuctionHouse, auctionLocation,
                               saleTitle, auctionStartDate, auctionEndDate, saleCode, soldCheckId, yetToBeSoldCheckId, boughtInCheckId, withdrawnCheckId, start, limit):
    andFlag = False
    whereQuery = ""
    if artistName:
        whereQuery += f"""fa_artist_name = '{artistName}'"""
        andFlag = True
    if artworkTitle:
        if andFlag:
            whereQuery += """ AND """
        whereQuery += f"""faa_artwork_title = '{artworkTitle}'"""
        andFlag = True
    if workOnPaper:
        if andFlag:
            whereQuery += """ AND """
        whereQuery += f"""faa_artwork_category LIKE '%{workOnPaper}%'"""
        andFlag = True
    if sculpture:
        if andFlag:
            whereQuery += f""" AND """
        whereQuery += f"""faa_artwork_category LIKE '%{sculpture}%'"""
        andFlag = True
    if painting:
        if andFlag:
            whereQuery += f""" AND """
        whereQuery += f"""faa_artwork_category LIKE '%{painting}%'"""
        andFlag = True
    if installation:
        if andFlag:
            whereQuery += f""" AND """
        whereQuery += f"""faa_artwork_category LIKE '%{installation}%'"""
        andFlag = True
    if photography:
        if andFlag:
            whereQuery += f""" AND """
        whereQuery += f"""faa_artwork_category LIKE '%{photography}%'"""
        andFlag = True
    if miniaturesArt:
        if andFlag:
            whereQuery += f""" AND """
        whereQuery += f"""faa_artwork_category LIKE '%{miniaturesArt}%'"""
        andFlag = True
    if textTilesArt:
        if andFlag:
            whereQuery += """ AND """
        whereQuery += f"""faa_artwork_category LIKE '%{textTilesArt}%'"""
        andFlag = True
    if others:
        if andFlag:
            whereQuery += """ AND """
        whereQuery += f"""faa_artwork_category LIKE '%{others}%'"""
        andFlag = True
    if selArtworkStart:
        if andFlag:
            whereQuery += f""" AND """
        whereQuery += f"""faa_artwork_start_year = {selArtworkStart}"""
        andFlag = True
    if selArtworkEnd and selArtworkEnd != '':
        if andFlag:
            whereQuery += f""" AND """
        whereQuery += f"""faa_artwork_end_year = {selArtworkEnd}"""
        andFlag = True
    if soldCheckId:
        if andFlag:
            whereQuery += f""" AND """
        whereQuery += f"""fal_lot_status = '{soldCheckId}'"""
        andFlag = True
    if yetToBeSoldCheckId:
        if andFlag:
            whereQuery += """ AND """
        whereQuery += f"""fal_lot_status = '{yetToBeSoldCheckId}'"""
    if boughtInCheckId:
        if andFlag:
            whereQuery += """ AND """
        whereQuery += f"""fal_lot_status = '{boughtInCheckId}'"""
    if withdrawnCheckId:
        if andFlag:
            whereQuery += """ AND """
        whereQuery += f"""fal_lot_status = '{withdrawnCheckId}'"""
    if selAuctionHouse:
        if andFlag:
            whereQuery += f""" AND """
        whereQuery += f"""cah_auction_house_name LIKE '%{selAuctionHouse}%'"""
        andFlag = True
    if auctionLocation:
        if andFlag:
            whereQuery += f""" AND """
        whereQuery += f"""cah_auction_house_location LIKE '%{auctionLocation}%'"""
        andFlag = True
    if saleTitle and saleTitle != '':
        if andFlag:
            whereQuery += f""" AND """
        whereQuery += f"""faac_auction_title LIKE '%{saleTitle}%'"""
        andFlag = True
    if auctionStartDate:
        if andFlag:
            whereQuery += f""" AND """
        whereQuery += f"""faac_auction_start_date = '{auctionStartDate}'"""
        andFlag = True
    if auctionEndDate:
        if andFlag:
            whereQuery += f""" AND """
        whereQuery += f"""faac_auction_end_date = '{auctionEndDate}'"""
        andFlag = True
    if saleCode:
        if andFlag:
            whereQuery += f""" AND """
        whereQuery += f"""faac_auction_sale_code = '{saleCode}'"""
    selectQuery = """SELECT fal_lot_ID, fal_lot_no, cah_auction_house_currency_code, fal_lot_high_estimate, fal_lot_low_estimate, fal_lot_sale_price, fal_lot_high_estimate_USD, fal_lot_low_estimate_USD, fal_lot_sale_price_USD, faac_auction_title, faa_artwork_image1, faa_artwork_material, faac_auction_ID, faa_artwork_category, fal_artwork_ID, faa_artwork_title, fa_artist_ID, fa_artist_name, faac_auction_start_date, cah_auction_house_name, cah_auction_house_location FROM fineart_artworks INNER JOIN fineart_lots ON fineart_lots.fal_artwork_ID = fineart_artworks.faa_artwork_ID AND fal_lot_published = 'yes' INNER JOIN fineart_artists ON faa_artist_ID = fa_artist_ID INNER JOIN fineart_auction_calendar ON fineart_auction_calendar.faac_auction_ID = fineart_lots.fal_auction_ID AND faac_auction_published = 'yes' INNER JOIN core_auction_houses ON core_auction_houses.cah_auction_house_ID = fineart_auction_calendar.faac_auction_house_ID WHERE """ + whereQuery + f""" LIMIT {limit} OFFSET {start}"""
    connList = connectToDb()
    connList[1].execute(selectQuery)
    searchData = connList[1].fetchall()
    disconnectDb(connList)
    return searchData


# @cache_page(CACHE_TTL)
@csrf_exempt
def index(request):
    if request.method == 'POST':
        artistName = request.POST.get('txtartistname')
        artworkTitle = request.POST.get('txttitle')
        workOnPaper = request.POST.get('medium1')
        sculpture = request.POST.get('medium2')
        painting = request.POST.get('medium3')
        installation = request.POST.get('medium4')
        photography = request.POST.get('medium5')
        miniaturesArt = request.POST.get('medium6')
        textTilesArt = request.POST.get('medium7')
        others = request.POST.get('medium8')
        selArtworkStart = request.POST.get('sel_artwork_start')
        selArtworkEnd = request.POST.get('sel_artwork_end')
        selAuctionHouse = request.POST.get('sel_auctionhouses')
        auctionLocation = request.POST.get('txtauctionlocation')
        saleTitle = request.POST.get('txtsaletitle')
        auctionStartDate = request.POST.get('dtauctionstartdate')
        auctionEndDate = request.POST.get('dtauctionenddate')
        saleCode = request.POST.get('txtsalecode')
        soldCheckId = request.POST.get('soldCheckId')
        yetToBeSoldCheckId = request.POST.get('yetToBeSoldCheckId')
        boughtInCheckId = request.POST.get('boughtInCehckId')
        withdrawnCheckId = request.POST.get('withdrawnCheckId')
        start = request.GET.get('start')
        limit = request.GET.get('limit')
        advanceSearchData = advanceSearchPriceDatabase(artistName, artworkTitle, workOnPaper, sculpture, painting,
                                                       installation, photography, miniaturesArt, textTilesArt, others, selArtworkStart,
                                                       selArtworkEnd, selAuctionHouse, auctionLocation, saleTitle,
                                                       auctionStartDate, auctionEndDate, saleCode, soldCheckId, yetToBeSoldCheckId, boughtInCheckId, withdrawnCheckId, start, limit)
        return HttpResponse(json.dumps(advanceSearchData, default=default))
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    # page = "1"
    # if request.method == 'GET':
    #     if 'page' in request.GET.keys():
    #         page = str(request.GET['page'])
    # chunksize = 20
    # maxlotstoconsider = 500 # These would be the 2500 top high priced lots. For this page we won't consider lots beyond the top 2500.
    # rows = 6
    # rowstartctr = int(page) * rows - rows
    # rowendctr = int(page) * rows
    # fstartctr = int(page) * maxlotstoconsider - maxlotstoconsider
    # fendctr = int(page) * maxlotstoconsider
    # maxauctionhouses = 60
    # ahstartctr = int(page) * maxauctionhouses - maxauctionhouses
    # ahendctr = int(page) * maxauctionhouses
    # context = {}
    # date2weeksago = datetime.datetime.now() - datetime.timedelta(days=settings.PDB_LATESTPERIOD)
    # #entitieslist = []
    # filterpdb = []
    # auctionhouses = {}
    # uniquefilter = {}
    # connlist = connecttoDB()
    # dbconn = connlist[0]
    # cursor = connlist[1]
    # try:
    #     #entitieslist = pickle.loads(redis_instance.get('pd_entitieslist'))
    #     filterpdb = pickle.loads(redis_instance.get('pd_filterpdb'))
    #     auctionhouses = pickle.loads(redis_instance.get('pd_auctionhouses'))
    # except:
    #     #entitieslist = []
    #     filterpdb = []
    # if filterpdb.__len__() == 0:
    #     allauctionhousesqset = AuctionHouse.objects.order_by('-edited')[ahstartctr:ahendctr]
    #     for auctionhouseobj in allauctionhousesqset:
    #         auctionhouses[auctionhouseobj.housename] = auctionhouseobj.id
    #         if auctionhouseobj.housename not in uniquefilter.keys():
    #             autocompleteauctionhousename = auctionhouseobj.housename
    #             autocompleteauctionhousename = autocompleteauctionhousename.replace('"', "")
    #             autocompleteauctionhousename = removecontrolcharacters(autocompleteauctionhousename)
    #             filterpdb.append(autocompleteauctionhousename)
    #             uniquefilter[auctionhouseobj.housename] = 1
    #     lotsqset = Lot.objects.order_by('-soldpriceUSD')[fstartctr:fendctr] # Need a restriction on the number of objects, otherwise it might crash the system.
    #     artworkidslist = []
    #     auctionidslist = []
    #     artistidslist = []
    # print(lotsqset)
    # for lotobj in lotsqset:
    #     artworkidslist.append(str(lotobj.artwork_id))
    #     auctionidslist.append(str(lotobj.auction_id))
    #     #print(lotobj.artwork_id)
    # artworkidsstr = "(" + ",".join(artworkidslist) + ")"
    # artworksql = "select faa_artwork_ID, faa_artwork_title, faa_artwork_requires_review, faa_artwork_start_year, faa_artwork_end_year, faa_artwork_start_year_identifier, faa_artwork_end_year_identifier, faa_artwork_start_year_precision, faa_artwork_end_year_precision, faa_artist_ID, faa_artist2_ID, faa_artist3_ID, faa_artist4_ID, faa_artwork_size_details, faa_artwork_height, faa_artwork_width, faa_artwork_depth, faa_arwork_measurement_unit, faa_artwork_material, faa_artwork_edition, faa_artwork_category, faa_artwork_markings, faa_artwork_description, faa_artwork_literature, faa_artwork_exhibition, faa_artwork_image1, faa_artwork_record_created, faa_artwork_record_updated from fineart_artworks where faa_artwork_ID in %s"%artworkidsstr
    # #print(artworksql)
    # cursor.execute(artworksql)
    # allartworksqset = cursor.fetchall()
    # artworksdict = {}
    # for awrec in allartworksqset:
    #     awid = str(awrec[0])
    #     artworksdict[awid] = awrec
    #     artistid = str(awrec[9])
    #     artistidslist.append(artistid)
    # artistidsstr = "(" + ",".join(artistidslist) + ")"
    # auctionidsstr = "(" + ",".join(auctionidslist) + ")"
    # auctionsql = "select faac_auction_ID, faac_auction_title, faac_auction_sale_code, faac_auction_house_ID, faac_auction_source, faac_auction_start_date, faac_auction_end_date, faac_auction_lot_count, faac_auction_image, faac_auction_published, faac_auction_record_created, faac_auction_record_updated, faac_auction_record_createdby, faac_auction_record_updatedby from fineart_auction_calendar where faac_auction_ID in %s order by faac_auction_start_date desc"%auctionidsstr
    # artistsql = "SELECT fa_artist_name, fa_artist_ID, fa_artist_name_prefix, fa_artist_nationality, fa_artist_birth_year, fa_artist_death_year, fa_artist_description, fa_artist_aka, fa_artist_bio, fa_artist_genre, fa_artist_image, fa_artist_record_created from fineart_artists Where fa_artist_ID in %s"%artistidsstr
    # auctionsdict = {}
    # artistsdict = {}
    # ahidslist = []
    # cursor.execute(auctionsql)
    # auctionsqset = cursor.fetchall()
    # for auctionrec in auctionsqset:
    #     aucid = str(auctionrec[0])
    #     auctionsdict[aucid] = auctionrec
    #     ahid = auctionrec[3]
    #     ahidslist.append(ahid)
    # cursor.execute(artistsql)
    # artistsqset = cursor.fetchall()
    # for artistrec in artistsqset:
    #     aid = str(artistrec[1])
    #     artistsdict[aid] = artistrec
    # auctionhousesqset = AuctionHouse.objects.filter(id__in=ahidslist)
    # auctionhousesdict = {}
    # for auctionhouse in auctionhousesqset:
    #     auctionhousesdict[str(auctionhouse.id)] = auctionhouse
    # lotctr = 0
    # for lotobj in lotsqset:
    #     lotimage = settings.IMG_URL_PREFIX + str(lotobj.lotimage1)
    #     saledate = lotobj.saledate
    #     saledt = datetime.datetime.combine(saledate, datetime.time(0, 0))
    #     if saledt < date2weeksago:
    #         continue
    #     artworkobj = None
    #     try:
    #         artworkobj = artworksdict[str(lotobj.artwork_id)]
    #         if lotimage == settings.IMG_URL_PREFIX: # If there is no lot image, go for the artwork image, if any.
    #             lotimage = settings.IMG_URL_PREFIX + str(artworkobj[25])
    #     except:
    #         continue # If we can't find the corresponding artwork for this lot, then we skip it.
    #     if lotimage == settings.IMG_URL_PREFIX: # We will not show lots with no images.
    #         continue
    #     if lotctr > chunksize:
    #         break
    #     lotctr += 1
    #     lottitle = artworkobj[1]
    #     if lottitle not in uniquefilter.keys():
    #         autocompletelotname = lottitle
    #         autocompletelotname = autocompletelotname.replace('"', "")
    #         autocompletelotname = removecontrolcharacters(autocompletelotname)
    #         filterpdb.append(autocompletelotname)
    #         uniquefilter[lottitle] = 1
    #     auctionname, aucid, auctionperiod, auctionhousename = "", "", "", ""
    #     try:
    #         auctionobj = auctionsdict[str(lotobj.auction_id)]
    #         auctionname = auctionobj[1]
    #         aucid = auctionobj[0]
    #         auctionperiod = auctionobj[5].strftime('%d %b, %Y')
    #         if type(auctionobj[6]) is datetime.date and auctionobj[6].strftime('%d %b, %Y') != "01 Jan, 0001" and auctionobj[6].strftime('%d %b, %Y') != "01 Jan, 1":
    #             auctionperiod += " - " + auctionobj[6].strftime('%d %b, %Y')
    #         if auctionname not in uniquefilter.keys():
    #             autocompleteauctionname = auctionname
    #             autocompleteauctionname = autocompleteauctionname.replace('"', "")
    #             autocompleteauctionname = removecontrolcharacters(autocompleteauctionname)
    #             filterpdb.append(autocompleteauctionname)
    #             uniquefilter[auctionname] = 1
    #         ahid = auctionobj[3]
    #         try:
    #             auctionhouseobj = auctionhousesdict[str(ahid)]
    #             auctionhousename = auctionhouseobj.housename
    #         except:
    #             pass
    #     except:
    #         pass
    #     artistname = ""
    #     try:
    #         artistobj = artistsdict[str(artworkobj[9])]
    #         artistname = artistobj[0]
    #         if artistname not in uniquefilter.keys():
    #             autocompleteartistname = artistname
    #             autocompleteartistname = autocompleteartistname.replace('"', "")
    #             autocompleteartistname = removecontrolcharacters(autocompleteartistname)
    #             filterpdb.append(autocompleteartistname)
    #             uniquefilter[artistname] = 1
    #     except:
    #         pass
    #     d = {'artworkname' : artworkobj[1], 'saledate' : lotobj.saledate.strftime('%d %b, %Y'), 'soldprice' : lotobj.soldpriceUSD, 'size' : artworkobj[13], 'medium' : artworkobj[18], 'description' : artworkobj[22], 'lid' : lotobj.id, 'awid' : artworkobj[0], 'lotimage' : settings.IMG_URL_PREFIX + str(lotobj.lotimage1), 'auctionname' : auctionname, 'aucid' : aucid, 'auctionperiod' : auctionperiod, 'aid' : artworkobj[9], 'artistname' : artistname, 'soldprice' : lotobj.soldpriceUSD, 'auctionhouse' : auctionhousename}
    #     #entitieslist.append(d)
    # allartistsqset = FeaturedArtist.objects.all()[:30000]
    # We selected 30000 records as that is the optimum number for speed and content.
    # Also, these are the best selling artists, so most searches would be based on them.
    # for aobj in allartistsqset:
    #     artistname = aobj.artist_name
    #     if artistname not in uniquefilter.keys():
    #         autocompleteartistname = artistname
    #         autocompleteartistname = autocompleteartistname.replace('"', "")
    #         autocompleteartistname = removecontrolcharacters(autocompleteartistname)
    #         filterpdb.append(autocompleteartistname)
    #         uniquefilter[artistname] = 1
    # try:
    #     redis_instance.set('pd_filterpdb', pickle.dumps(filterpdb))
    # redis_instance.set('pd_entitieslist', pickle.dumps(entitieslist))
    #         redis_instance.set('pd_auctionhouses', pickle.dumps(auctionhouses))
    #     except:
    #         pass
    # cursor.close()
    # dbconn.close()
    # context['entities'] = entitieslist
    # context['filterpdb'] = filterpdb
    # context['auctionhouses'] = auctionhouses
    # context['artwork_year_list'] = {'pre-15th-century' : 'Pre-15th Century', '15th-century' : '15th Century', '16th-century' : '16th Century', '17th-century' : '17th Century', '18th-century' : '18th Century', '19th-century' : '19th Century', 'early-20th-century' : 'Early 20th Century', 'mid-20th-century' : 'Mid 20th Century', 'late-20th-century' : 'Late 20th Century', 'contemporary' : 'Contemporary'}
    # carouselentries = getcarouselinfo_new()
    # context['carousel'] = carouselentries
    context = {}
    userDict = request.session.get('user')
    if userDict:
        context['username'] = userDict['username']
    template = loader.get_template('pdb.html')
    return HttpResponse(template.render(context, request))


def searchAuctionHouses(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    searchKeyword = request.GET.get('search')
    auctionHouseSelectQuery = f"""SELECT DISTINCT(cah_auction_house_name) AS cah_auction_house_name FROM core_auction_houses"""
    if searchKeyword:
        auctionHouseSelectQuery += f""" WHERE cah_auction_house_name LIKE '%{searchKeyword}%'"""
    else:
        auctionHouseSelectQuery += f""" LIMIT 100 OFFSET 0"""
    connList = connectToDb()
    connList[1].execute(auctionHouseSelectQuery)
    auctionAuctionHouseData = connList[1].fetchall()
    disconnectDb(connList)
    return HttpResponse(json.dumps(auctionAuctionHouseData))


def searchArtists(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    searchKeyword = request.GET.get('search')
    artistSearchQuery = f"""SELECT DISTINCT(fa_artist_name) as fa_artist_name FROM fineart_artists"""
    if searchKeyword:
        artistSearchQuery += f""" WHERE fa_artist_name LIKE '%{searchKeyword}%'"""
    else:
        artistSearchQuery += """ LIMIT 100 OFFSET 0"""
    connList = connectToDb()
    connList[1].execute(artistSearchQuery)
    artistsData = connList[1].fetchall()
    disconnectDb(connList)
    return HttpResponse(json.dumps(artistsData))


def searchArtworks(request):
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    searchKeyword = request.GET.get('search')
    artworkSelectQuery = f"""SELECT DISTINCT(faa_artwork_title) AS faa_artwork_title FROM fineart_artworks"""
    if searchKeyword:
        artworkSelectQuery += f""" WHERE faa_artwork_title LIKE '%{searchKeyword}%'"""
    else:
        artworkSelectQuery += """ LIMIT 100 OFFSET 0"""
    connList = connectToDb()
    connList[1].execute(artworkSelectQuery)
    artworksData = connList[1].fetchall()
    disconnectDb(connList)
    return HttpResponse(json.dumps(artworksData))


def checkoutSession(request):
    domainUrl = str(request.build_absolute_uri()).split('price/')[0]
    if request.method != 'GET':
        return HttpResponse("Invalid method of call")
    userDict = request.session.get('user')
    if userDict:
        plansDetails = request.GET.get('plans')
        if plansDetails == 'basicDaily':
            productId = 'price_1MxmuPSFFk9gA4NXMxzkodQy'
        elif plansDetails == 'basicMonthly':
            productId = 'price_1MxnXbSFFk9gA4NXpAWP3mFO'
        elif plansDetails == 'basicYearly':
            productId = 'price_1MxnYzSFFk9gA4NXER2MmkfR'
        elif plansDetails == 'premiumDaily':
            productId = 'price_1MxnavSFFk9gA4NXV4FS7fax'
        elif plansDetails == 'premiumMonthly':
            productId = 'price_1MxnbuSFFk9gA4NXy5mnfUoE'
        elif plansDetails == 'premiumYearly':
            productId = 'price_1MxncPSFFk9gA4NXKSGyDV5W'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            checkoutSessionObj = stripe.checkout.Session.create(client_reference_id=userDict['user_id'],
                                                                customer_email=userDict['email'],
                                                                success_url=f"{domainUrl}price/success/",
                                                                cancel_url=f"{domainUrl}price/cancel/",
                                                                payment_method_types=['card'],
                                                                mode='subscription',
                                                                line_items=[
                                                                        {
                                                                            'price': productId,
                                                                            'quantity': 1,
                                                                        }
                                                                    ]
                                                                )
            return HttpResponse(json.dumps({'publicKey': settings.STRIPE_PUBLISHABLE_KEY, 'sessionId': checkoutSessionObj['id']}))
        except Exception as e:
            print(e)
            return HttpResponse(json.dumps({'error': str(e)}))
        return HttpResponse(json.dumps({'plans': plansDetails}))
    else:
        return HttpResponse(json.dumps({'msg': 'please register or login first!'}))

def details(request):
    pass


def search(request):
    """
    This should return a json response containing a list of dicts.
    The dict keys would be the attributes of auction, artist or lot object.
    The object type will be specified in the object with the 'obtype' key.
    """
    if request.method != 'GET':
        return HttpResponse(json.dumps({'err': "Invalid method of call"}))
    searchkey = None
    if request.method == 'GET':
        if 'q' in request.GET.keys():
            searchkey = str(request.GET['q']).strip()
    if not searchkey or searchkey == "":
        return HttpResponse(json.dumps({'err': "Invalid Request: Request is missing search key"}))
    searchkey = searchkey.replace("'", "\\'").replace('"', '\\"')  # Escape apostrophes and quotes.
    page = "1"
    if request.method == 'GET':
        if 'page' in request.GET.keys():
            page = request.GET['page']
    context = {}
    allsearchresults = []
    maxperobjectsearchresults = 30
    maxsearchresults = maxperobjectsearchresults * 3  # 3 types of objects are searched: auctions, artworks/lots and artists.
    startsearchctr = int(page) * maxsearchresults - maxsearchresults
    endsearchctr = int(page) * maxsearchresults + 1
    objectstartctr = maxperobjectsearchresults * int(page) - maxperobjectsearchresults
    objectendctr = maxperobjectsearchresults * int(page)
    connlist = connecttoDB()
    dbconn = connlist[0]
    cursor = connlist[1]
    idpattern = re.compile("\d+")
    # Remember to close db connection at the end of the function...
    auctionhouseqset = AuctionHouse.objects.filter(housename__icontains=searchkey)
    auctionhouseidslist = []
    for auctionhouseobj in auctionhouseqset:
        ah_id = str(auctionhouseobj.id)
        auctionhouseidslist.append(ah_id)
    auctionsdict = {}
    auctionhouseidsstr = "(" + ",".join(auctionhouseidslist) + ")"
    auctionsql = "select faac_auction_ID, faac_auction_title, faac_auction_sale_code, faac_auction_house_ID, faac_auction_source, faac_auction_start_date, faac_auction_end_date, faac_auction_lot_count, faac_auction_image, faac_auction_published, faac_auction_record_created, faac_auction_record_updated, faac_auction_record_createdby, faac_auction_record_updatedby from fineart_auction_calendar where faac_auction_house_ID in %s order by faac_auction_start_date desc" % auctionhouseidsstr
    # print(auctionsql)
    if re.search(idpattern, auctionhouseidsstr):
        cursor.execute(auctionsql)
        auctionsqset = cursor.fetchall()
    else:
        auctionsqset = []
    for auctionrec in auctionsqset:
        auchouseid = str(auctionrec[3])
        if auchouseid in auctionsdict.keys():
            auctionslist = auctionsdict[auchouseid]
            auctionslist.append(auctionrec)
            auctionsdict[auchouseid] = auctionslist
        else:
            auctionsdict[auchouseid] = [auctionrec, ]
    achctr = 0
    for auctionhouseobj in auctionhouseqset:
        auctionsqset = auctionsdict[str(auctionhouseobj.id)]
        auctionhousename = auctionhouseobj.housename
        ahid = auctionhouseobj.id
        for auctionobj in auctionsqset:
            auctionperiod = auctionobj[5].strftime("%d %b, %Y")
            if type(auctionobj[6]) == datetime.date and auctionobj[6].strftime("%d %b, %Y") != "01 Jan, 0001" and \
                    auctionobj[6].strftime("%d %b, %Y") != "01 Jan, 1":
                auctionperiod += " - " + auctionobj[6].strftime("%d %b, %Y")
            d = {'auctionname': auctionobj[1], 'aucid': auctionobj[2], 'auctionhouse': auctionhousename,
                 'coverimage': settings.IMG_URL_PREFIX + str(auctionobj[8]), 'ahid': ahid,
                 'auctionperiod': auctionperiod, 'aucid': auctionobj[0], 'lotcount': str(auctionobj[7]),
                 'obtype': 'auction'}
            if achctr > maxperobjectsearchresults * int(page):
                break
            achctr += 1
            allsearchresults.append(d)
    auctionsqset = Auction.objects.filter(auctionname__icontains=searchkey)[
                   objectstartctr:objectendctr]  # .order_by('priority')
    aucctr = 0
    auctionhouseidslist = []
    auctionhousedict = {}
    for auctionobj in auctionsqset:
        ah_id = str(auctionobj.auctionhouse_id)
        auctionhouseidslist.append(ah_id)
    auctionhouseidsstr = "(" + ",".join(auctionhouseidslist) + ")"
    auctionhousesql = "select cah_auction_house_ID, cah_auction_house_name from core_auction_houses where cah_auction_house_ID in %s" % auctionhouseidsstr
    if re.search(idpattern, auctionhouseidsstr):
        cursor.execute(auctionhousesql)
        ahqset = cursor.fetchall()
    else:
        ahqset = []
    for ahrec in ahqset:
        ah_id = str(ahrec[0])
        ah_name = ahrec[1]
        auctionhousedict[ah_id] = ah_name
    for auctionobj in auctionsqset:
        auctionhouseid = auctionobj.auctionhouse_id
        auctionhousename, ahid = "", ""
        try:
            auctionhousename = auctionhousedict[str(auctionhouseid)]
            ahid = auctionhouseid
        except:
            pass
        auctionperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y")
        if type(auctionobj.auctionenddate) == datetime.date and auctionobj.auctionenddate.strftime(
                "%d %b, %Y") != "01 Jan, 0001" and auctionobj.auctionenddate.strftime("%d %b, %Y") != "01 Jan, 1":
            auctionperiod += " - " + auctionobj.auctionenddate.strftime("%d %b, %Y")
        d = {'auctionname': auctionobj.auctionname, 'aucid': auctionobj.auctionid, 'auctionhouse': auctionhousename,
             'coverimage': settings.IMG_URL_PREFIX + str(auctionobj.coverimage), 'ahid': ahid,
             'auctionperiod': auctionperiod, 'aucid': auctionobj.id, 'lotcount': str(auctionobj.lotcount),
             'obtype': 'auction'}
        if aucctr > maxperobjectsearchresults * int(page):
            break
        aucctr += 1
        allsearchresults.append(d)
    """
    Here we would be using raw SQL to speed up the searches. The following
    SQL queries use MATCH/AGAINST searches on fields that are indexed using
    FULLTEXT indexing. -Supriyo.
    """
    artctr = 0
    quotaflag = 0
    searchartistsql = "select fa_artist_ID, fa_artist_name, fa_artist_nationality, fa_artist_birth_year, fa_artist_death_year, fa_artist_image from fineart_artists where MATCH(fa_artist_name) AGAINST ('" + searchkey + "') limit " + str(
        maxperobjectsearchresults) + " OFFSET " + str(objectstartctr)
    cursor.execute(searchartistsql)
    matchedartists = cursor.fetchall()
    artworkartistdict = {}
    lotartworkdict = {}
    artistidslist = []
    artworkidslist = []
    for artist in matchedartists:
        aid = str(artist[0])
        artistidslist.append(aid)
    artistidsstr = "(" + ",".join(artistidslist) + ")"
    artworksql = "select faa_artwork_ID, faa_artwork_title, faa_artwork_requires_review, faa_artwork_start_year, faa_artwork_end_year, faa_artwork_start_year_identifier, faa_artwork_end_year_identifier, faa_artist_ID, faa_artwork_size_details, faa_artwork_material, faa_artwork_edition, faa_artwork_category, faa_artwork_markings, faa_artwork_description, faa_artwork_literature, faa_artwork_exhibition, faa_artwork_image1, faa_artwork_record_created from fineart_artworks where faa_artist_ID in %s" % artistidsstr
    # artworklotartistsql = "select artist_id, artist_name, artist_price_usd, prefix, nationality, birthyear, deathyear, description, aka, bio, artistimage, genre, saledate, auctionid, lotstatus, medium, sizedetails, lotcategory, lotnum, artworkid, artworkname, highestimate, lowestimate, lotimage1, lotimage2, lotid from fa_artwork_lot_artist where artist_id in %s"%artistidsstr
    if re.search(idpattern, artistidsstr):
        cursor.execute(artworksql)
        artworksqset = cursor.fetchall()
    else:
        artworksqset = []
    for awrec in artworksqset:
        artistid = str(awrec[7])
        if artistid in artworkartistdict.keys():
            awlist = artworkartistdict[artistid]
            awlist.append(awrec)
            artworkartistdict[artistid] = awlist
        else:
            artworkartistdict[artistid] = [awrec, ]
        awid = str(awrec[0])
        artworkidslist.append(awid)
    awidsstr = "(" + ",".join(artworkidslist) + ")"
    lotsql = "select fal_lot_ID, fal_lot_no, fal_sub_lot_no, fal_artwork_ID, fal_auction_ID, fal_lot_sale_date, fal_lot_material, fal_lot_size_details, fal_lot_category, fal_lot_high_estimate_USD, fal_lot_low_estimate_USD, fal_lot_high_estimate, fal_lot_low_estimate, fal_lot_sale_price_USD, fal_lot_sale_price, fal_lot_condition, fal_lot_status, fal_lot_provenance, fal_lot_published, fal_lot_image1, fal_lot_image2 from fineart_lots where fal_artwork_ID in %s" % awidsstr
    if re.search(idpattern, awidsstr):
        cursor.execute(lotsql)
        lotsqset = cursor.fetchall()
    else:
        lotsqset = []
    for lotrec in lotsqset:
        awidstr = str(lotrec[3])
        if awidstr in lotartworkdict.keys():
            lotlist = lotartworkdict[awidstr]
            lotlist.append(lotrec)
            lotartworkdict[awidstr] = lotlist
        else:
            lotartworkdict[awidstr] = [lotrec, ]
    for artist in matchedartists:
        try:
            artistartworkqset = artworkartistdict[str(artist[0])]
        except:
            artistartworkqset = []
        for artwork in artistartworkqset:
            try:
                lotqset = lotartworkdict[str(artwork[0])]
            except:
                lotqset = []
            for lot in lotqset:
                soldprice = str(lot[13])
                soldprice = soldprice.replace("$", "")
                # print(artist[1] + " ########################")
                szdet = lot[7]
                if lot[7] is None:
                    szdet = ""
                d = {'artistname': artist[1], 'lottitle': artwork[1], 'medium': lot[6], 'size': szdet.encode('utf-8'),
                     'aid': artist[0], 'birthyear': artist[3], 'deathyear': artist[4], 'nationality': artist[2],
                     'artistimage': settings.IMG_URL_PREFIX + str(artist[5]),
                     'coverimage': settings.IMG_URL_PREFIX + str(lot[19]), 'awid': artwork[0], 'createdate': artwork[3],
                     'lid': lot[0], 'obtype': 'lot', 'aucid': lot[4], 'soldprice': soldprice}
                allsearchresults.append(d)
                artctr += 1
                if artctr > maxperobjectsearchresults:
                    quotaflag = 1  # Quota for this object (artists) has been emptied.
                    break
            if quotaflag == 1:
                break
        if quotaflag == 1:
            break
    searchartworksql = "select faa_artwork_ID, faa_artwork_title, faa_artwork_start_year, faa_artist_ID from fineart_artworks where MATCH(faa_artwork_title) AGAINST ('" + searchkey + "') limit " + str(
        maxperobjectsearchresults) + " OFFSET " + str(objectstartctr)
    cursor.execute(searchartworksql)
    matchedartworks = cursor.fetchall()
    # artworkqset = Artwork.objects.filter(artworkname__icontains=searchkey)[objectstartctr:objectendctr]
    # print(artworkqset.explain())
    awctr = 0
    quotaflag = 0
    artistdict = {}
    lotartworkdict = {}
    artistidslist = []
    artworkidslist = []
    for artwork in matchedartworks:
        artistid = str(artwork[3])
        artistidslist.append(artistid)
        artworkid = str(artwork[0])
        artworkidslist.append(artworkid)
    artistidsstr = "(" + ",".join(artistidslist) + ")"
    artworkidsstr = "(" + ",".join(artworkidslist) + ")"
    artistsql = "SELECT fa_artist_name, fa_artist_ID, fa_artist_name_prefix, fa_artist_nationality, fa_artist_birth_year, fa_artist_death_year, fa_artist_description, fa_artist_aka, fa_artist_bio, fa_artist_genre, fa_artist_image, fa_artist_record_created from fineart_artists Where fa_artist_ID in %s" % artistidsstr
    lotsql = "select fal_lot_ID, fal_lot_no, fal_sub_lot_no, fal_artwork_ID, fal_auction_ID, fal_lot_sale_date, fal_lot_material, fal_lot_size_details, fal_lot_category, fal_lot_high_estimate_USD, fal_lot_low_estimate_USD, fal_lot_high_estimate, fal_lot_low_estimate, fal_lot_sale_price_USD, fal_lot_sale_price, fal_lot_condition, fal_lot_status, fal_lot_provenance, fal_lot_published, fal_lot_image1, fal_lot_image2 from fineart_lots where fal_artwork_ID in %s" % artworkidsstr
    if re.search(idpattern, artistidsstr):
        cursor.execute(artistsql)
        artistsqset = cursor.fetchall()
    else:
        artistsqset = []
    for artistrec in artistsqset:
        artistidstr = str(artistrec[1])
        artistdict[artistidstr] = artistrec
    if re.search(idpattern, artworkidsstr):
        cursor.execute(lotsql)
        lotsqset = cursor.fetchall()
    else:
        lotsqset = []
    for lotrec in lotsqset:
        artworkid = str(lotrec[3])
        if artworkid in lotartworkdict.keys():
            lotslist = lotartworkdict[artworkid]
            lotslist.append(lotrec)
            lotartworkdict[artworkid] = lotslist
        else:
            lotartworkdict[artworkid] = [lotrec, ]
    for artwork in matchedartworks:
        artist = None
        try:
            artist = artistdict[str(artwork[3])]
        except:
            continue  # Skip the artwork if we can't identify the artist.
        try:
            lotqset = lotartworkdict[str(artwork[0])]
        except:
            lotqset = []
        for lot in lotqset:
            soldprice = str(lot[13])
            soldprice = soldprice.replace("$", "")
            # print(artist.artistname + " %%%%%%%%%%%%%%%%%%")
            szdet = lot[7]
            if lot[7] is None:
                szdet = ""
            d = {'artistname': artist[0], 'lottitle': artwork[1], 'medium': lot[6], 'size': szdet.encode('utf-8'),
                 'aid': artist[1], 'birthyear': artist[4], 'deathyear': artist[5], 'nationality': artist[3],
                 'artistimage': settings.IMG_URL_PREFIX + str(artist[10]),
                 'coverimage': settings.IMG_URL_PREFIX + str(lot[19]), 'awid': artwork[0], 'createdate': artwork[2],
                 'lid': lot[0], 'obtype': 'lot', 'aucid': lot[4], 'soldprice': soldprice}
            allsearchresults.append(d)
            awctr += 1
            if awctr > maxperobjectsearchresults:
                quotaflag = 1  # Quota for this object (artwork) has been emptied.
                break
        if quotaflag == 1:
            break
    context['allsearchresults'] = allsearchresults
    userDict = request.session.get('user')
    if userDict:
        context['username'] = userDict['username']
    cursor.close()
    dbconn.close()
    prevpage = int(page) - 1
    nextpage = int(page) + 1
    displayedprevpage1 = 0
    displayedprevpage2 = 0
    if prevpage > 0:
        displayedprevpage1 = prevpage - 1
        displayedprevpage2 = prevpage - 2
    displayednextpage1 = nextpage + 1
    displayednextpage2 = nextpage + 2
    firstpage = 1
    context['pages'] = {'prevpage': prevpage, 'nextpage': nextpage, 'firstpage': firstpage,
                        'displayedprevpage1': displayedprevpage1, 'displayedprevpage2': displayedprevpage2,
                        'displayednextpage1': displayednextpage1, 'displayednextpage2': displayednextpage2,
                        'currentpage': int(page)}
    return HttpResponse(json.dumps(context))


@csrf_exempt
def dofilter(request):
    if request.method != 'POST':
        return HttpResponse('{ "error" : "Invalid request method"}')
    artistname, lottitle, medium, auctionhouseids, saletitle, auclocation, salecode, salestartdate, saleenddate, artworkstartperiod, artworkendperiod = "", "", "", "", "", "", "", "", "", "", ""
    page = "1"
    requestbody = str(request.body)
    bodycomponents = requestbody.split("&")
    requestdict = {}
    for comp in bodycomponents:
        compparts = comp.split("=")
        if compparts.__len__() > 1:
            compparts[0] = compparts[0].replace("b'", "")
            requestdict[compparts[0]] = urllib.parse.unquote(compparts[1])
    endbarPattern = re.compile("\|\s*$")
    onlyspacesPattern = re.compile("^\s+$")
    if 'pageno' in requestdict.keys():
        page = requestdict['pageno'].strip()
    if 'artistname' in requestdict.keys():
        artistname = requestdict['artistname'].strip()
        artistname = artistname.replace("'", "\\'").replace('"', '\\"')  # Escape apostrophes and quotes.
    if 'lottitle' in requestdict.keys():
        lottitle = requestdict['lottitle'].strip()
        lottitle = lottitle.replace("'", "\\'").replace('"', '\\"')  # Escape apostrophes and quotes.
    if 'medium' in requestdict.keys():
        medium = requestdict['medium'].lower()
        medium = endbarPattern.sub("", medium)
    if 'auctionhouses' in requestdict.keys():
        auctionhouseids = requestdict['auctionhouses'].strip()
        auctionhouseids = endbarPattern.sub("", auctionhouseids)
        auctionhouseids = onlyspacesPattern.sub("", auctionhouseids)
    if 'saletitle' in requestdict.keys():
        saletitle = requestdict['saletitle']
    if 'salecode' in requestdict.keys():
        salecode = requestdict['salecode']
    if 'auclocation' in requestdict.keys():
        auclocation = requestdict['auclocation']
    if 'salestartdate' in requestdict.keys():
        salestartdate = requestdict['salestartdate'].strip()
    if 'saleenddate' in requestdict.keys():
        saleenddate = requestdict['saleenddate'].strip()
    if 'artwork_start' in requestdict.keys():
        artworkstartperiod = requestdict['artwork_start'].strip()
    if 'artwork_end' in requestdict.keys():
        artworkendperiod = requestdict['artwork_end'].strip()
    try:
        page = int(page)
    except:
        page = 1
    startctr = page * settings.PDB_MAXSEARCHRESULT - settings.PDB_MAXSEARCHRESULT
    endctr = page * settings.PDB_MAXSEARCHRESULT + 1
    artworkstartctr = page * settings.PDB_ARTWORKSLIMIT - settings.PDB_ARTWORKSLIMIT
    artworkendctr = page * settings.PDB_ARTWORKSLIMIT
    artiststartctr = page * settings.PDB_ARTISTSLIMIT - settings.PDB_ARTISTSLIMIT
    artistendctr = page * settings.PDB_ARTISTSLIMIT
    maxartworkmatches = 500  # This is the maximum number of artworks by a single artist that would be considered for searching.
    ahidlist = []
    mediumlist = []
    solist = []
    sizelist = []
    ahidlist = auctionhouseids.split("|")
    ahctr = 0
    for ah in ahidlist:
        if ah == "":
            ahidlist.pop(ahctr)
        ahctr += 1
    mediumlist = medium.split("|")
    mctr = 0
    for m in mediumlist:
        if m == "":
            mediumlist.pop(mctr)
        mctr += 1
    entitieslist = []
    context = {}
    connlist = connecttoDB()
    dbconn = connlist[0]
    cursor = connlist[1]
    l_entities = []
    if lottitle != "":
        filterartworksql = "select faa_artwork_ID, faa_artwork_title, faa_artwork_image1, faa_artist_ID from fineart_artworks where MATCH(faa_artwork_title) AGAINST ('" + lottitle + "') limit %s OFFSET %s" % (
        settings.PDB_ARTWORKSLIMIT, artworkstartctr)
        cursor.execute(filterartworksql)
        filterartworks = cursor.fetchall()
        artworkidlist = []
        artistidlist = []
        for artwork in filterartworks:
            artworkidlist.append(artwork[0])
            artistidlist.append(artwork[3])
        lotqset = Lot.objects.filter(artwork_id__in=artworkidlist)
        lotbyartworkiddict = {}
        auctionbyiddict = {}
        aucidlist = []
        for lot in lotqset:
            lotbyartworkiddict[str(lot.artwork_id)] = [lot, ]  # Should contain only a single object
            aucidlist.append(lot.auction_id)
        artistbyiddict = {}
        artistqset = Artist.objects.filter(id__in=artistidlist)
        for artist in artistqset:
            artistbyiddict[str(artist.id)] = artist
        auctionqset = Auction.objects.filter(id__in=aucidlist)
        auchousebyiddict = {}
        auchouseidlist = []
        for auction in auctionqset:
            auctionbyiddict[str(auction.id)] = auction
            auchouseidlist.append(auction.auctionhouse_id)
        auchouseqset = AuctionHouse.objects.filter(id__in=auchouseidlist)
        for auchouse in auchouseqset:
            auchousebyiddict[str(auchouse.id)] = auchouse
        for artwork in filterartworks:
            artworkname = artwork[1]
            # print(artworkname + " #######################")
            awid = artwork[0]
            lotqset = lotbyartworkiddict[str(artwork[0])]  # We need only one referenced lot.
            artistobj = None
            lartistname, aid = "", ""
            try:
                artistobj = artistbyiddict[str(artwork[3])]
                lartistname = artistobj.artistname
                aid = artistobj.id
            except:
                pass
            lmedium, lsize, lsaledate, lsoldprice, lminestimate, lmaxestimate, lcategory, lestimate, lid, lh, lw, ld, limage = "", "", "", "", "", "", "", "", "", "", "", "", ""
            auctionname, aucid, auctionperiod, auctionhousename, ahid = "", "", "", "", ""
            if lotqset.__len__() > 0:
                lmedium = lotqset[0].medium.lower()
                if type(lotqset[0].sizedetails) == str:
                    lsize = lotqset[0].sizedetails.encode('utf-8')
                else:
                    lsize = ""
                lsaledate = lotqset[0].saledate.strftime("%d %b, %Y")
                lsoldprice = lotqset[0].soldpriceUSD
                lminestimate = lotqset[0].lowestimateUSD
                lmaxestimate = lotqset[0].highestimateUSD
                lestimate = str(lminestimate)
                if lmaxestimate and lmaxestimate > 0.00:
                    lestimate += " - " + str(lmaxestimate)
                lcategory = lotqset[0].category
                lid = lotqset[0].id
                lh = lotqset[0].height
                lw = lotqset[0].width
                ld = lotqset[0].depth
                limage = settings.IMG_URL_PREFIX + str(lotqset[0].lotimage1)
                if limage == "":
                    limage = settings.IMG_URL_PREFIX + str(artwork[2])
                if limage == "":  # If we still don't have an image, just skip it.
                    continue
                auctionobj = None
                try:
                    auctionobj = auctionbyiddict[str(lotqset[0].auction_id)]
                    auctionname = auctionobj.auctionname
                    aucid = auctionobj.id
                    auctionperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y")
                    if auctionobj.auctionenddate.strftime(
                            "%d %b, %Y") != "01 Jan, 0001" and auctionobj.auctionenddate.strftime(
                            "%d %b, %Y") != "01 Jan, 1":
                        auctionperiod += " - " + auctionobj.auctionenddate.strftime("%d %b, %Y")
                    auchouseobj = auchousebyiddict[str(auctionobj.auctionhouse_id)]
                    auctionhousename = auchouseobj.housename
                    ahid = auchouseobj.id
                except:
                    pass
            d = {'lottitle': artworkname, 'artistname': lartistname, 'aid': aid, 'awid': awid, 'medium': lmedium,
                 'size': lsize, 'saledate': lsaledate, 'soldprice': lsoldprice, 'estimate': lestimate, 'lid': lid,
                 'auctionname': auctionname, 'auctionperiod': auctionperiod, 'aucid': aucid,
                 'auctionhouse': auctionhousename, 'ahid': ahid, 'obtype': 'lot', 'coverimage': limage}
            # Now check all parameters against user's selected values to determine if this dict should be appended to 'entitieslist'.
            artistflag, titleflag, mediumflag, sizeflag, soldpriceflag, estimateflag, auctionhouseflag = -1, 1, -1, -1, -1, -1, -1
            if artistname != "" and artistname.lower() in lartistname.lower():  # Partial match is considered.
                artistflag = 1
            elif artistname != "":
                artistflag = 0
            else:
                pass
            for m in mediumlist:
                if m in lmedium:  # If a single medium component matches, we set the flag to True and break out.
                    mediumflag = 1
                    break
            if mediumlist.__len__() > 0 and mediumflag == -1:
                mediumflag = 0
            ahctr = 0
            for ad in ahidlist:
                if ad == "" or ahid == "":
                    continue
                ahctr += 1
                if int(ad) == int(ahid):
                    auctionhouseflag = 1
                    break
            if ahctr > 0 and auctionhouseflag == -1:
                auctionhouseflag = 0
            if type(soldmin) == str:
                soldmin = soldmin.strip()
            if type(soldmax) == str:
                soldmax = soldmax.strip()
            if soldmin is not None and soldmin != "" and lsoldprice is not None and lsoldprice != "" and float(
                    soldmin) < float(lsoldprice):
                if soldmax is not None and soldmax != "" and float(soldmax) > float(lsoldprice):
                    soldpriceflag = 1
                elif soldmax is None or soldmax == "":
                    soldpriceflag = 1
            elif soldmin is not None and soldmin != "" and lsoldprice is not None and lsoldprice != "" and float(
                    soldmin) > float(lsoldprice):
                soldpriceflag = 0
            else:
                pass
            sizeparts = [lh, lw]
            if ld != "":
                sizeparts.append(ld)
            for sz in sizelist:
                if sz == "small":
                    for sp in sizeparts:
                        try:
                            sp = sp.strip()
                            fsp = float(sp)
                            if fsp < 40:  # Check if any of the dimensions is less than 40 cm.
                                sizeflag = 1
                                break
                            else:
                                sizeflag = 0
                        except:
                            pass
                elif sz == "medium":
                    for sp in sizeparts:
                        try:
                            sp = sp.strip()
                            fsp = float(sp)
                            if fsp > 40 and fsp < 100:  # Check if any of the dimensions is between 40 and 100 cm.
                                sizeflag = 1
                                break
                            else:
                                sizeflag = 0
                        except:
                            pass
                elif sz == "large":
                    for sp in sizeparts:
                        try:
                            sp = sp.strip()
                            fsp = float(sp)
                            if fsp > 100:  # Check if any of the dimensions is greater than 100 cm.
                                sizeflag = 1
                                break
                            else:
                                sizeflag = 0
                        except:
                            pass
                else:
                    pass
            try:
                if type(estimatemax) == str:
                    estimatemax = estimatemax.strip()
                if type(estimatemin) == str:
                    estimatemin = estimatemin.strip()
                if float(lminestimate) < float(estimatemin) and float(lmaxestimate) > float(estimatemax):
                    estimateflag = 1
                else:
                    estimateflag = 0
            except:  # If user didn't specify any estimate values, then the flag remains -1.
                pass
            # print(str(estimateflag) + " ## " + str(sizeflag) + " ## " + str(soldpriceflag) + " ## " + str(auctionhouseflag) + " ## " + str(mediumflag) + " ## " + str(artistflag))
            if estimateflag != 0 and sizeflag != 0 and soldpriceflag != 0 and auctionhouseflag != 0 and mediumflag != 0 and artistflag != 0:
                l_entities.append(d)
    else:  # Handle case with parameters other than artwork name.
        filterartists = []
        if artistname != "":
            filterartistsql = "select fa_artist_ID, fa_artist_name, fa_artist_nationality, fa_artist_birth_year, fa_artist_death_year, fa_artist_image from fineart_artists where MATCH(fa_artist_name) AGAINST ('%s') limit %s offset %s" % (
            artistname, settings.PDB_ARTISTSLIMIT, artiststartctr)
            cursor.execute(filterartistsql)
            filterartists = cursor.fetchall()
        else:
            filterartistsql = "select fa_artist_ID, fa_artist_name, fa_artist_nationality, fa_artist_birth_year, fa_artist_death_year, fa_artist_image from fineart_artists limit %s offset %s" % (
            settings.PDB_ARTISTSLIMIT, artiststartctr)
            cursor.execute(filterartistsql)
            filterartists = cursor.fetchall()
        artistidlist = []
        artworkbyartistiddict = {}
        artworkidlist = []
        lotbyawiddict = {}
        for artist in filterartists:
            artistidlist.append(artist[0])
        artworkqset = Artwork.objects.filter(artist_id__in=artistidlist).order_by('-edited')
        for aw in artworkqset:
            if str(aw.artist_id) not in artworkbyartistiddict.keys():
                artworkbyartistiddict[str(aw.artist_id)] = [aw, ]
            else:
                awlist = artworkbyartistiddict[str(aw.artist_id)]
                awlist.append(aw)
                artworkbyartistiddict[str(aw.artist_id)] = awlist
            artworkidlist.append(aw.id)
        lotsqset = Lot.objects.filter(artwork_id__in=artworkidlist)
        aucidlist = []
        aucbyiddict = {}
        for lotobj in lotsqset:
            if str(lotobj.artwork_id) not in lotbyawiddict.keys():
                lotbyawiddict[str(lotobj.artwork_id)] = [lotobj, ]
            else:
                lotslist = lotbyawiddict[str(lotobj.artwork_id)]
                lotslist.append(lotobj)
                lotbyawiddict[str(lotobj.artwork_id)] = lotslist
            aucidlist.append(lotobj.auction_id)
        auctionsqset = Auction.objects.filter(id__in=aucidlist)
        auchouseidlist = []
        auchousebyiddict = {}
        for aucobj in auctionsqset:
            aucbyiddict[str(aucobj.id)] = aucobj
            auchouseidlist.append(aucobj.auctionhouse_id)
        auchouseqset = AuctionHouse.objects.filter(id__in=auchouseidlist)
        for auchouse in auchouseqset:
            auchousebyiddict[str(auchouse.id)] = auchouse
        for artist in filterartists:
            aid = artist[0]
            if aid in settings.BLACKLISTED_ARTISTS:
                continue
            artistnm = artist[1]
            # for artwork in Artwork.objects.filter(artist_id=artist[0]).order_by('-edited')[:maxartworkmatches].iterator():
            try:
                awqset = artworkbyartistiddict[str(artist[0])]
            except:
                awqset = []
            for artwork in awqset[:maxartworkmatches]:
                if artwork.image1 == "":
                    continue
                awid = artwork.id
                artworkname = artwork.artworkname
                lotqset = lotbyawiddict[str(artwork.id)]
                lmedium, lsize, lsaledate, lsoldprice, lminestimate, lmaxestimate, lcategory, lestimate, lid = "", "", "", "", "", "", "", "", ""
                auctionname, aucid, auctionperiod, auctionhousename, ahid = "", "", "", "", ""
                if lotqset.__len__() > 0:
                    lmedium = lotqset[0].medium.lower()
                    if type(lotqset[0].sizedetails) == str:
                        lsize = lotqset[0].sizedetails.encode('utf-8')
                    else:
                        lsize = ""
                    lsaledate = lotqset[0].saledate.strftime("%d %b, %Y")
                    lsoldprice = lotqset[0].soldpriceUSD
                    lminestimate = lotqset[0].lowestimateUSD
                    lmaxestimate = lotqset[0].highestimateUSD
                    lestimate = str(lminestimate)
                    if lmaxestimate and lmaxestimate > 0.00:
                        lestimate += " - " + str(lmaxestimate)
                    lcategory = lotqset[0].category
                    lid = lotqset[0].id
                    auctionobj = None
                    try:
                        auctionobj = aucbyiddict[str(lotqset[0].auction_id)]
                        auctionname = auctionobj.auctionname
                        aucid = auctionobj.id
                        auctionperiod = auctionobj.auctionstartdate.strftime("%d %b, %Y")
                        if auctionobj.auctionenddate.strftime(
                                "%d %b, %Y") != "01 Jan, 0001" and auctionobj.auctionenddate.strftime(
                                "%d %b, %Y") != "01 Jan, 1":
                            auctionperiod += " - " + auctionobj.auctionenddate.strftime("%d %b, %Y")
                        auchouseobj = auchousebyiddict[str(auctionobj.auctionhouse_id)]
                        auctionhousename = auchouseobj.housename
                        ahid = auchouseobj.id
                    except:
                        pass
                d = {'lottitle': artworkname, 'artistname': artistnm, 'aid': aid, 'awid': awid, 'medium': lmedium,
                     'size': lsize, 'saledate': lsaledate, 'soldprice': lsoldprice, 'estimate': lestimate, 'lid': lid,
                     'auctionname': auctionname, 'auctionperiod': auctionperiod, 'aucid': aucid,
                     'auctionhouse': auctionhousename, 'ahid': ahid, 'obtype': 'lot',
                     'coverimage': settings.IMG_URL_PREFIX + str(artwork.image1)}
                entitieslist.append(d)
        l_entities = []
        if entitieslist.__len__() > 0:
            for entity in entitieslist:
                mediumflag, sizeflag, soldpriceflag, estimateflag, auctionhouseflag = -1, -1, -1, -1, -1
                for m in mediumlist:
                    if m in entity['medium'].lower():
                        mediumflag = 1
                        break
                if mediumlist.__len__() > 0 and mediumflag == -1:
                    mediumflag = 0  # User specified medium, but none of them matched this entity's medium.
                for ah in ahidlist:
                    try:
                        if int(ah) == int(entity['ahid']):
                            auctionhouseflag = 1
                            break
                    except:
                        pass
                if ahidlist.__len__() > 0 and auctionhouseflag == -1:
                    auctionhouseflag = 0
                try:
                    if entity['soldprice'] is None:
                        entity['soldprice'] = 0.00
                    if type(entity['soldprice']) == str:
                        entity['soldprice'] = entity['soldprice'].strip()
                        entity['soldprice'] = float(entity['soldprice'])
                    if type(soldmin) == str:
                        soldmin = soldmin.strip()
                        if soldmin == "":
                            soldmin = '0.00'
                    if type(soldmax) == str:
                        soldmax = soldmax.strip()
                        if soldmax == "":
                            soldmax = '0.00'
                    if entity['soldprice'] > float(soldmin) and entity['soldprice'] < float(soldmax):
                        soldpriceflag = 1
                    else:
                        soldpriceflag = 0
                except:
                    print("ERROR: %s '%s'" % (
                    sys.exc_info()[1].__str__(), entity['soldprice']))  # This should be logged - TODO
                estimateparts = entity['estimate'].split(" - ")
                lminestimate = estimateparts[0]
                lmaxestimate = ""
                if estimateparts.__len__() > 1:
                    lmaxestimate = estimateparts[1]
                try:
                    if type(lminestimate) == str:
                        lminestimate = lminestimate.strip()
                    if type(lmaxestimate) == str:
                        lmaxestimate = lmaxestimate.strip()
                    if float(lminestimate) < float(estimatemin) and float(lmaxestimate) > float(estimatemax):
                        estimateflag = 1
                    else:
                        estimateflag = 0
                except:
                    pass
                if mediumflag != 0 and soldpriceflag != 0 and estimateflag != 0 and auctionhouseflag != 0:
                    l_entities.append(entity)
                # print(str(estimateflag) + " ## " + str(soldpriceflag) + " ## " + str(auctionhouseflag) + " ## " + str(mediumflag))
        else:  # Control should never come here.
            pass
    dbconn.close()  # Closed db connection!
    r_entitieslist = []
    if l_entities.__len__() > settings.PDB_MAXSEARCHRESULT:
        for d in l_entities[startctr:endctr]:
            r_entitieslist.append(d)
    else:
        for d in l_entities:
            r_entitieslist.append(d)
    context['allsearchresults'] = r_entitieslist
    userDict = request.session['user']
    if userDict:
        context['username'] = userDict['username']
    prevpage = int(page) - 1
    nextpage = int(page) + 1
    displayedprevpage1 = 0
    displayedprevpage2 = 0
    if prevpage > 0:
        displayedprevpage1 = prevpage - 1
        displayedprevpage2 = prevpage - 2
    displayednextpage1 = nextpage + 1
    displayednextpage2 = nextpage + 2
    firstpage = 1
    context['pages'] = {'prevpage': prevpage, 'nextpage': nextpage, 'firstpage': firstpage,
                        'displayedprevpage1': displayedprevpage1, 'displayedprevpage2': displayedprevpage2,
                        'displayednextpage1': displayednextpage1, 'displayednextpage2': displayednextpage2,
                        'currentpage': int(page)}
    return HttpResponse(json.dumps(context))


def showplans(request):
    if request.method != 'GET':
        return HttpResponse(json.dumps({'err': 'Invalid method of call'}))
    context = {}
    userDict = request.session.get('user')
    if userDict:
        context['username'] = userDict['username']
    template = loader.get_template('plans.html')
    return HttpResponse(template.render(context, request))
