from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.template.context_processors import csrf
from django.views.generic import View
from django.http import HttpResponseBadRequest, HttpResponse , HttpResponseRedirect, HttpRequest
from django.urls import reverse
from django.template import RequestContext
from django.db.models import Q
from django.template.response import TemplateResponse
from django.template import Template
from django.contrib.auth.models import User as djUser
from django.core.mail import send_mail
from django.template.loader import get_template

import os, sys, datetime, re
from django.core.mail import send_mail
import glob, base64
import simplejson as json
import shutil
import MySQLdb
import unicodedata, itertools

from auctionhouses.models import AuctionHouse
from login.models import EmailAlerts
from eolicowebsite.utils import connecttoDB, disconnectDB

def get_fav_info():
    dbconn, cursor = None, None
    connlist = connecttoDB()
    dbconn, cursor = connlist[0], connlist[1]
    # First, get all users and their favourites
    favsql = "select user_id, reference_table, referenced_table_id from user_favorites"
    cursor.execute(favsql)
    allrecords = cursor.fetchall()
    favdict = {}
    artistsidlist = []
    artworksidlist = []
    auctionsidlist = []
    for rec in allrecords:
        userid = rec[0]
        reftable = rec[1]
        refid = rec[2]
        try:
            userobj = djUser.objects.get(id=userid)
            username = userobj.username
            emailaddress = userobj.email
            if str(userid) not in favdict.keys():
                favdict[str(userid)] = [{'reftable' : reftable, 'refid' : refid, 'username' : username, 'emailaddress' : emailaddress},]
                if reftable == "fineart_artists":
                    if str(refid) not in artistsidlist:
                        artistsidlist.append(str(refid))
                elif reftable == "fineart_artworks":
                    if str(refid) not in artworksidlist:
                        artworksidlist.append(str(refid))
                elif reftable == "fineart_auction_calendar":
                    if str(refid) not in auctionsidlist:
                        auctionsidlist.append(str(refid))
            else:
                favlist = favdict[str(userid)]
                d = {'reftable' : reftable, 'refid' : refid, 'username' : username, 'emailaddress' : emailaddress}
                favlist.append(d)
                favdict[str(userid)] = favlist
        except:
            print("Encountered error on user Id %s: %s"%(userid, sys.exc_info()[1].__str__()))
    returndict = {'favdata' : favdict, 'artist_ids' : artistsidlist, 'artwork_ids' : artworksidlist, 'auction_ids' : auctionsidlist}
    disconnectDB(dbconn, cursor)
    return returndict


def sendemail(username, emailaddr, datatype, datalist, auctionslist):
    tmpl = get_template('email_alert.html')
    context = {}
    emailalert = EmailAlerts()
    userobj = djUser.objects.get(username=username)
    fromemail = settings.FROM_EMAIL_USER
    subject = ""
    request = None
    context['username'] = username
    context['datatype'] = datatype
    curdatetime = datetime.datetime.now()
    currentdate = curdatetime.strftime("%d %b, %Y")
    context['currentdate'] = currentdate
    context['address'] = ["", "", "", ""]
    if datatype == "artist":
        context['artistname'] = datalist[0]
        context['nationality'] = datalist[1]
        context['lifetime'] = datalist[2]
        context['artistdesc'] = datalist[3]
        context['artistbio'] = datalist[4]
        context['artistimg'] = datalist[5]
        context['aid'] = datalist[6]
    if datatype == "artwork":
        context['artworkname'] = datalist[9]
        context['lotnum'] = datalist[0]
        context['auction_id'] = datalist[1]
        context['material'] = datalist[2]
        context['sizedetails'] = datalist[3]
        context['estimate'] = datalist[4]
        context['saleprice'] = datalist[5]
        context['provenance'] = datalist[6]
        context['artworkimg'] = datalist[7]
        context['awid'] = datalist[8]
    if datatype == "auction":
        context['auctionname'] = datalist[0]
        context['auctioncode'] = datalist[1]
        context['auctionhouse'] = datalist[2]
        context['source'] = datalist[3]
        context['auctionstart'] = datalist[4]
        context['auctionend'] = datalist[5]
        context['auctionperiod'] = datalist[9]
        context['lotcount'] = datalist[6]
        context['auctionimg'] = datalist[7]
        context['aucid'] = datalist[8]
    message = tmpl.render(context, request)
    try:
        send_mail(subject, message, fromemail, [emailaddr,])
        emailalert.sendstatus = True
    except:
        emailalert.sendstatus = False
    emailalert.user = userobj
    emailalert.emailcontent = message
    emailalert.emailtype = datatype
    emailalert.emaildate = curdatetime
    try:
        emailalert.save()
    except:
        print("Error saving email: %s"%sys.exc_info()[1].__str__())
    return emailalert.sendstatus


def send_email_alerts():
    datadict = get_fav_info()
    favdict = datadict['favdata']
    artist_ids = datadict['artist_ids']
    artwork_ids = datadict['artwork_ids']
    auction_ids = datadict['auction_ids']
    auctionidslist = "(" + ",".join(auction_ids) + ")"
    artworkidslist = "(" + ",".join(artwork_ids) + ")"
    artistidslist = "(" + ",".join(artist_ids) + ")"
    upcoming_artists_dict = {}
    upcoming_artworks_dict = {}
    upcoming_auctions_dict = {}
    artworkartists = []
    artist_auction_dict = {}
    artwork_auction_dict = {}
    dbconn, cursor = None, None
    connlist = connecttoDB()
    dbconn, cursor = connlist[0], connlist[1]
    dateafter2weeks = datetime.datetime.now() + datetime.timedelta(days=2*7)
    auctionsql = "select faac_auction_ID, faac_auction_title, faac_auction_sale_code, faac_auction_house_ID, faac_auction_source, faac_auction_start_date, faac_auction_end_date, faac_auction_lot_count, faac_auction_image from fineart_auction_calendar where faac_auction_ID in %s and faac_auction_start_date > now() and faac_auction_start_date < %s"%(auctionidslist, dateafter2weeks)
    cursor.execute(auctionsql)
    allauctionrecords = cursor.fetchall()
    for aucrec in allauctionrecords:
        aucid = aucrec[0]
        auctitle = aucrec[1]
        salecode = aucrec[2]
        auchouse = AuctionHouse.objects.get(id=aucrec[3])
        auchousename = auchouse.housename
        aucsrc = aucrec[4]
        aucstart = aucrec[5]
        aucend = aucrec[6]
        aucperiod = aucstart.strftime("%d %b, %Y")
        if str(aucend) != "0000-00-00" and str(aucend) != "01 Jan, 1":
            aucperiod = aucperiod + " - " + str(aucend)
        lotcount = aucrec[7]
        aucimg = aucrec[8]
        upcoming_auctions_dict[str(aucid)] = [auctitle, salecode, auchousename, aucsrc, aucstart, aucend, lotcount, settings.IMG_URL_PREFIX + str(aucimg), aucid, aucperiod]
        # List out all artworks available in the auction
        lotsql = "select fal_lot_ID, fal_lot_no, fal_artwork_ID, fal_auction_ID, fal_lot_material, fal_lot_size_details, fal_lot_high_estimate_USD, fal_lot_low_estimate_USD, fal_lot_sale_price_USD, fal_lot_provenance, fal_lot_image1 from fineart_lots where fal_auction_ID=%s"%aucid
        cursor.execute(lotsql)
        alllotsrecords = cursor.fetchall()
        for lotrec in alllotsrecords:
            artworkid = lotrec[2]
            estimatesUSD = str(lotrec[7]) + " - " + str(lotrec[6])
            upcoming_artworks_dict[str(artworkid)] = [lotrec[1], lotrec[3], lotrec[4], lotrec[5], estimatesUSD, lotrec[8], lotrec[9], settings.IMG_URL_PREFIX + str(lotrec[10]), artworkid]
            artworksql = "select faa_artist_ID, faa_artwork_title from fineart_artworks where faa_artwork_ID=%s"%artworkid
            cursor.execute(artworksql)
            artworkrecords = cursor.fetchall() # This will just be a single record
            if artworkrecords.__len__() == 0:
                continue
            artworkartists.append(str(artworkrecords[0][0]))
            upcoming_artworks_dict[str(artworkid)].append(artworkrecords[0][1]) # Got artwork name
            if str(artworkrecords[0][0]) not in artist_auction_dict.keys():
                artist_auction_dict[str(artworkrecords[0][0])] = [aucid,]
            else:
                auclist = artist_auction_dict[str(artworkrecords[0][0])]
                if aucid not in auclist:
                    auclist.append(aucid)
                artist_auction_dict[str(artworkrecords[0][0])] = auclist
            if str(artworkid) not in artwork_auction_dict.keys():
                artwork_auction_dict[str(artworkid)] = [aucid,]
            else:
                auclist = artwork_auction_dict[str(artworkid)]
                if aucid not in auclist:
                    auclist.append(aucid)
                artwork_auction_dict[str(artworkid)] = auclist
    artworkartists_str = "(" + ",".join(artworkartists) + ")"
    artistsql = "select fa_artist_ID, fa_artist_name, fa_artist_nationality, fa_artist_birth_year, fa_artist_death_year, fa_artist_description, fa_artist_bio, fa_artist_image from fineart_artists where fa_artist_ID in %s"%artworkartists_str
    cursor.execute(artistsql)
    allartistrecords = cursor.fetchall(artistsql)
    for artistrec in allartistrecords:
        lifetime = str(artistrec[3]) + " - " + str(artistrec[4])
        upcoming_artists_dict[str(artistrec[0])] = [artistrec[1], artistrec[2], lifetime, artistrec[5], artistrec[6], artistrec[7], settings.IMG_URL_PREFIX + str(artistrec[0])]
    # Now iterate through every user and find out what they are interested in. If there is any id that exists in the respective table, send an email to the email address.
    for useridstr in favdict.keys():
        favlist = favdict[useridstr]
        for d in favlist:
            emailaddr = d['emailaddress']
            username = d['username']
            reftable = d['reftable']
            refid = str(d['refid'])
            if reftable == 'fineart_artists':
                if refid in upcoming_artists_dict.keys():
                    artistinfo = upcoming_artists_dict[refid]
                    try:
                        aucidlist = artist_auction_dict[str(refid)]
                        auctioninfolist = []
                        for aucid in aucidlist:
                            auctioninfo = upcoming_auctions_dict[str(aucid)]
                            auctioninfolist.append(auctioninfo)
                        sendemail(username, emailaddr, 'artist', artistinfo, auctioninfolist)
                    except:
                        print("Failed to send email alert. Error: %s"%sys.exc_info()[1].__str__())
            elif reftable == 'fineart_artworks':
                if refid in upcoming_artworks_dict.keys():
                    artworkinfo = upcoming_artworks_dict[refid]
                    try:
                        aucidlist = artwork_auction_dict[str(refid)]
                        auctioninfolist = []
                        for aucid in aucidlist:
                            auctioninfo = upcoming_auctions_dict[str(aucid)]
                            auctioninfolist.append(auctioninfo)
                        sendemail(username, emailaddr, 'artwork', artworkinfo, auctioninfolist)
                    except:
                        print("Failed to send email alert. Error: %s"%sys.exc_info()[1].__str__())
            elif reftable == 'fineart_auction_calendar':
                if refid in upcoming_auctions_dict.keys():
                    try:
                        auctioninfo = upcoming_auctions_dict[refid]
                        sendemail(username, emailaddr, 'auction', auctioninfo, [])
                    except:
                        print("Failed to send email alert. Error: %s"%sys.exc_info()[1].__str__())
    disconnectDB(dbconn, cursor)
    print("Done sending email alerts.")
        

