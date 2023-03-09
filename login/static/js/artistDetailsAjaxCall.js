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
    let htmlData = `<div class="col-sm-12 col-md-6 col-lg-4 col-xl-4 mb-4">
                        <div class="latest-artists">
                            <a href="/auction/showauction/?aucid=${auctionData.faac_auction_ID}" class="latest-card">
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

                                    <h3>Contemporary Curated</h3>
                                    <h3><span>${auctionData.cah_auction_house_name}</span></h3>
                                    <h3 class="mb-3"><span>${auctionData.faac_auction_start_date} | ${auctionData.cah_auction_house_location}</span>
                                    </h3>

                                    <h3>Estimate : <span>Login to view</span></h3>
                                    <h3>Price Sold : <span>Login to view</span></h3>
                                </div>
                            </a>
                        </div>
                    </div>`
    return htmlData
}

function upcomingAuctionDataSet(limit) {
    fetch(`/artist/getArtistUpcomingAuctions/?aid=${artistId}&limit=${limit}`, {
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

function pastAuctionDataSet(limit) {
    fetch(`/artist/getArtistPastAuctions/?aid=${artistId}&limit=${limit}`, {
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

function pastUpcomingAuction(e, pastUpcomingStr) {
    pastUpcomingStrData = pastUpcomingStr
    let limit = document.querySelector('#inputGroupSelect01').value
    if (pastUpcomingStrData === 'past') {
        pastAuctionDataSet(limit)
    }
    else if (pastUpcomingStrData === 'upcoming') {
        upcomingAuctionDataSet(limit)
    }
}

function selectChange(e) {
    let limit = e.target.value
    if (pastUpcomingStrData === 'past') {
        pastAuctionDataSet(limit)
    }
    else if (pastUpcomingStrData === 'upcoming') {
        upcomingAuctionDataSet(limit)
    }
}

// function getArtistPastAuctions() {
//     fetch(`/artist/getArtistPastAuctions/?aid=${artistId}&limit=50`, {
//         method: 'GET',
//     })
//         .then(response => response.json())
//         .then(body => {        })
// }

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
    pastAuctionDataSet(50)

})
