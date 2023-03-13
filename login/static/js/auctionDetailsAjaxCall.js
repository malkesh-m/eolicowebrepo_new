const urlParams = new URLSearchParams(location.search)
const auctionId = urlParams.get('aucid')
const artworkDataDiv = document.querySelector('#pastauctions')


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

                                    <h3>Estimate : <span>${auctionData.fal_lot_low_estimate_USD} - ${auctionData.fal_lot_high_estimate_USD}</span></h3>
                                    <h3>Price Sold : <span>${auctionData.fal_lot_sale_price_USD}</span></h3>
                                </div>
                            </a>
                        </div>
                    </div>`
    return htmlData
}

function getAuctionArtworksDataSetter(queryParamas, start, limit) {
    fetch(`/auction/getAuctionArtworksData/?aucid=${auctionId}&start=${start}&${queryParamas}limit=${limit}`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = ''
            body.forEach(artworkData => {
                htmlData += htmlDataBinder(artworkData)
            })
            artworkDataDiv.innerHTML = htmlData
        })
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
    let limit = document.querySelector('#inputGroupSelect01').value
    getAuctionArtworksDataSetter(queryParams, 0, limit)
}

function getAuctionDetailsData() {
    fetch(`/auction/getAuctionDetails/?aucid=${auctionId}`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            document.querySelector('#auctionTitle').innerHTML = body.faac_auction_title
            document.querySelector('#auctionImage').src = `https://f000.backblazeb2.com/file/fineart-images/${body.faac_auction_image}`
            document.querySelector('#auctionName').innerHTML = body.cah_auction_house_name
            document.querySelector('#auctionLocation').innerHTML = `${body.cah_auction_house_location}, ${body.cah_auction_house_country}`
            document.querySelector('#auctionDate').innerHTML = body.faac_auction_start_date
        })
}

document.addEventListener('DOMContentLoaded', function () {
    document.querySelector('#lotLowToHighCheckId').checked = true
    getAuctionDetailsData()
    getAuctionArtworksDataSetter('lotLowToHigh=true&', 0, 50)
})