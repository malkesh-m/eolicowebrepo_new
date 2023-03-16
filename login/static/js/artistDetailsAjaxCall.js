const urlParams = new URLSearchParams(location.search)
const artistId = urlParams.get('aid').replaceAll('"', '')
const artistNameID = document.querySelector('#artistNameId')
const nationalityBirthDeathId = document.querySelector('#nationalityBirthDeathId')
const artistImageId = document.querySelector('#artistImageId')
const aboutNameId = document.querySelector('#aboutNameId')
const artistBioId = document.querySelector('#artistBioId')
const lastYearSoldLotsId = document.querySelector('#lastYearSoldLotsId')
const lastYearSellRateId = document.querySelector('#lastYearSellRateId')
const lastYearAveSalePriceId = document.querySelector('#lastYearAveSalePriceId')
const lastYearSoldPriceEstimatesId = document.querySelector('#lastYearSoldPriceEstimatesId')
const auctionsDataDivID = document.querySelector('#pastauctions')
let pastUpcomingStrData = 'past'

function htmlDataBinder(auctionData) {
    let htmlData = `<div class="col-sm-12 col-md-6 col-lg-4 col-xl-4 mb-4 artworkData">
                        <div class="latest-artists">
                            <a href="/auction/details/?lid=${auctionData.fal_lot_ID}" class="latest-card">
                                <div class="thumb">
                                    <img src="https://f000.backblazeb2.com/file/fineart-images/${auctionData.faa_artwork_image1}" class="card-img" alt="img">
                                </div>
                                <div class="artist-card">
                                    <h3>Title : <span>${auctionData.faa_artwork_title}</span></h3>
                                    <h3>Artist : <span>${auctionData.fa_artist_name}</span></h3>
                                    <h3 class="mb-3">Lot : ${auctionData.fal_lot_no}</h3>

                                    <h3>Medium : <span>${auctionData.faa_artwork_material}</span></h3>
                                    <h3 class="mb-3">Category : <span>${auctionData.faa_artwork_category}</span>
                                    </h3>

                                    <h3>${auctionData.faac_auction_title}</h3>
                                    <h3><span>${auctionData.cah_auction_house_name}</span></h3>
                                    <h3 class="mb-3"><span>${auctionData.faac_auction_start_date} | ${auctionData.cah_auction_house_location}</span>
                                    </h3>

                                    <h3>Estimate : <span>${auctionData.cah_auction_house_currency_code} ${auctionData.fal_lot_low_estimate} - ${auctionData.fal_lot_high_estimate}</span></h3>`
                                    if (auctionData.cah_auction_house_currency_code === 'USD') {
                                        if (auctionData.fal_lot_sale_price == 0) {
                                            htmlData += `<h3>Price Sold : <span>Unsold</span></h3>`
                                        }
                                        else {
                                        htmlData += `<h3>Price Sold : <span>${auctionData.cah_auction_house_currency_code} ${auctionData.fal_lot_sale_price}</span></h3>`
                                        }
                                    }
                                    else {
                                        htmlData += `<h3>Estimate USD : <span>${auctionData.fal_lot_low_estimate_USD} - ${auctionData.fal_lot_high_estimate_USD}</span></h3>`
                                        if (auctionData.fal_lot_sale_price == 0) {
                                            htmlData += `<h3>Price Sold : <span>Unsold</span></h3>`
                                        }
                                        else {
                                            htmlData += `<h3>Price Sold : <span>${auctionData.cah_auction_house_currency_code} ${auctionData.fal_lot_sale_price}</span></h3>
                                                        <h3>Price Sold USD : <span>${auctionData.fal_lot_sale_price_USD}</span></h3>`
                                        }
                                    }
                                htmlData += `
                                </div>
                            </a>
                        </div>
                    </div>`
    return htmlData
}

function upcomingAuctionDataSet(queryParams, limit) {
    fetch(`/artist/getArtistUpcomingAuctions/?aid=${artistId}&${queryParams}limit=${limit}`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = ''
            body.forEach(auctionData => {
                htmlData += htmlDataBinder(auctionData)
            })
            auctionsDataDivID.innerHTML = htmlData
        })
}

function pastAuctionDataSet(queryParams, limit) {
    fetch(`/artist/getArtistPastAuctions/?aid=${artistId}&${queryParams}limit=${limit}`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = ''
            body.forEach(auctionData => {
                htmlData += htmlDataBinder(auctionData)
            })
            auctionsDataDivID.innerHTML = htmlData
        })
}

function pastUpcomingAuction(e, pastUpcomingStr, queryParams) {
    pastUpcomingStrData = pastUpcomingStr
    let limit = document.querySelector('#inputGroupSelect01').value
    if (pastUpcomingStrData === 'past') {
        pastAuctionDataSet(queryParams, limit)
    }
    else if (pastUpcomingStrData === 'upcoming') {
        upcomingAuctionDataSet(queryParams, limit)
    }
}

function selectChange(e) {
    let limit = e.target.value
    if (pastUpcomingStrData === 'past') {
        pastAuctionDataSet('', limit)
    }
    else if (pastUpcomingStrData === 'upcoming') {
        upcomingAuctionDataSet('', limit)
    }
}

function filterAuction(e) {
    const artworkTitleTextId = document.querySelector('#artworkTitleTextId')
    const lotLowToHighCheckId = document.querySelector('#lotLowToHighCheckId')
    const lotHighToLowCheckId = document.querySelector('#lotHighToLowCheckId')
    const priceLowToHighCheckId = document.querySelector('#priceLowToHighCheckId')
    const priceHighToLowCheckId = document.querySelector('#priceHighToLowCheckId')
    const paintingsCheckId = document.querySelector('#paintingsCheckId')
    const printsCheckId = document.querySelector('#printsCheckId')
    const photographsCheckId = document.querySelector('#photographsCheckId')
    const miniaturesCheckId = document.querySelector('#miniaturesCheckId')
    const othersCheckId = document.querySelector('#othersCheckId')
    const soldCheckId = document.querySelector('#soldCheckId')
    const yetToBeSoldCheckId = document.querySelector('#yetToBeSoldCheckId')
    const boughtInCehckId = document.querySelector('#boughtInCehckId')
    const withdrawnCheckId = document.querySelector('#withdrawnCheckId')
    const fromDateTextId = document.querySelector('#fromDateTextId')
    const toDateTextId = document.querySelector('#toDateTextId')

    let queryParams = ``

    if (artworkTitleTextId.value) {
        queryParams = queryParams + `artworkTitle=${artworkTitleTextId.value}&`
    }
    if (lotLowToHighCheckId.checked) {
        queryParams = queryParams + `lotLowToHigh=true&`
    }
    if (lotHighToLowCheckId.checked) {
        queryParams = queryParams + `lotHighToLow=true&`
    }
    if (priceLowToHighCheckId.checked) {
        queryParams = queryParams + `priceLowToHigh=true&`
    }
    if (priceHighToLowCheckId.checked) {
        queryParams = queryParams + `priceHighToLow=true&`
    }
    if (paintingsCheckId.checked) {
        queryParams = queryParams + `paintings=paintings&`
    }
    if (printsCheckId.checked) {
        queryParams = queryParams + `prints=prints&`
    }
    if (photographsCheckId.checked) {
        queryParams = queryParams + `photographs=photographs&`
    }
    if (miniaturesCheckId.checked) {
        queryParams = queryParams + `miniatures=miniatures&`
    }
    if (othersCheckId.checked) {
        queryParams = queryParams + 'others=all&'
    }
    if (soldCheckId.checked) {
        queryParams = queryParams + `sold=sold&`
    }
    if (yetToBeSoldCheckId.checked) {
        queryParams = queryParams + `yetToBeSold=yet to be sold&`
    }
    if (boughtInCehckId.checked) {
        queryParams = queryParams + `boughtIn=bought-in&`
    }
    if (withdrawnCheckId.checked) {
        queryParams = queryParams + `withdrawn=withdrawn&`
    }
    if (fromDateTextId.value) {
        queryParams = queryParams + `fromDate=${fromDateTextId.value}&`
    }
    if (toDateTextId.value) {
        queryParams = queryParams + `toDate=${toDateTextId.value}&`
    }

    pastUpcomingAuction(e, pastUpcomingStrData , queryParams)
}

function getArtistDetails() {
    fetch(`/artist/getArtistDetails/?aid=${artistId}`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            artistNameID.innerHTML = body.fa_artist_name
            nationalityBirthDeathId.innerHTML = `${body.fa_artist_nationality}, ${body.fa_artist_birth_year} - ${body.fa_artist_death_year}`
            artistImageId.src = `https://f000.backblazeb2.com/file/fineart-images/${body.fa_artist_image}`
            aboutNameId.innerHTML = aboutNameId.innerHTML + ' ' + body.fa_artist_name
            artistBioId.innerHTML = body.fa_artist_bio
            let htmlData = ''
            if (body.fa_artist_nationality !== 'na') {
                htmlData = htmlData + body.fa_artist_nationality
            }
            if (body.fa_artist_birth_year != 0) {
                htmlData = htmlData + ' , ' + body.fa_artist_birth_year
                if (body.fa_artist_death_year != 0) {
                    htmlData = htmlData + ` - ${body.fa_artist_death_year}`
                }
            }
            nationalityBirthDeathId.innerHTML = htmlData
            lastYearSoldLotsId.innerHTML = body.years_lot_sale
            lastYearSellRateId.innerHTML = body.sell_through_rate + '%'
            lastYearAveSalePriceId.innerHTML = body.avg_sale_price_usd
            lastYearSoldPriceEstimatesId.innerHTML = body.mean_price_usd
        })
}

document.addEventListener('DOMContentLoaded', function () {

    getArtistDetails()
    pastAuctionDataSet('', 50)

})
