const workDataDiv =  document.querySelector('#Work')
const collapseThreeDiv = document.querySelector('#collapseThree')
const collapseFourDiv = document.querySelector('#collapseFour')

function pastTrendingAuctionSetter (queryParamas, start, limit) {
    fetch(`/login/getRecentAuctions/?start=${start}&${queryParamas}limit=${limit}`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = ''
            body.forEach(recentAuctionData => {
                htmlData += `<div class="col-sm-12 col-md-6 col-lg-4 col-xl-4 mb-4 auctionData">
                                <div class="latest-artists">
                                    <a href="/auction/showauction/?aucid=${recentAuctionData.faac_auction_ID}" class="latest-card">
                                        <div class="thumb">
                                            <img src="https://f000.backblazeb2.com/file/fineart-images/${recentAuctionData.faac_auction_image}" class="card-img" alt="img">
                                        </div>
                                        <div class="down-content">
                                            <h6><span>Sale Code:</span> ${recentAuctionData.faac_auction_sale_code}
                                            </h6>
                                            <div class="d-flex justify-content-between align-items-start">
                                                <p class="auction-text p-0">${recentAuctionData.faac_auction_title}</p>
                                                <p>View Lots</p>
                                            </div>
                                            <h5 class="mb-0 py-2">${recentAuctionData.cah_auction_house_name}</h5>
                                            <span>${recentAuctionData.faac_auction_start_date} | ${recentAuctionData.cah_auction_house_location}</span>
                                        </div>
                                    </a>
                                </div>
                            </div>`
            })
            workDataDiv.innerHTML =  `<div class="row" id='pastauctions'>
                                        ${htmlData}
                                    </div>
                                    <div class="row">
                                        <div class="col-lg-12 text-center">
                                            <a class="btn btn-login btn-round ml-0" href="">View More</a>
                                        </div>
                                    </div>`
        })
}

function filterAuction(e) {
    const auctionTitle = document.querySelector('#auctionTitle')
    const saleDate = document.querySelector('#defaultCheck1')
    const fromDate = document.querySelector('#fromDate')
    const toDate = document.querySelector('#toDate')
    const forHousesCls = document.querySelectorAll('.forHousesCls')
    const forLocationsCls = document.querySelectorAll('.forLocationsCls')
    let queryParams = ''

    if (auctionTitle.value) {
        queryParams += `auctionTitle=${auctionTitle.value}&`
    }
    if (saleDate.checked) {
        queryParams += `saleDate=true&`
    }
    if (fromDate.value) {
        queryParams += `fromDate=${fromDate.value}&`
    }
    if (toDate.value) {
        queryParams += `toDate=${toDate.value}&`
    }
    let housesStr = ''
    let locationsStr = ''
    forHousesCls.forEach(houses => {
        if (houses.checked) {
            housesStr += houses.value + ','
        }
    })
    forLocationsCls.forEach(locations => {
        if (locations.checked) {
            locationsStr += locations.value + ','
        }
    })
    if (housesStr) {
        queryParams += `houses=${housesStr}&`
    }
    if (locationsStr) {
        queryParams += `locations=${locationsStr}&`
    }
    start = document.querySelectorAll('.auctionData').length
    pastTrendingAuctionSetter(queryParams, start, 50)
}

function housesSetter(apiData) {
    document.querySelector('#housesShowMoreIdBtn').remove()
    let htmlData = collapseThreeDiv.innerHTML
    apiData.forEach(auctionHousesData => {
        htmlData += `<div class="form-check">
                        <input class="form-check-input forHousesCls" type="checkbox" value="${auctionHousesData.cah_auction_house_name}" id="${auctionHousesData.cah_auction_house_name}" onblur="filterAuction(event)">
                        <label class="form-check-label" for="${auctionHousesData.cah_auction_house_name}">${auctionHousesData.cah_auction_house_name}</label>
                    </div>`
    })
    if (10 === apiData.length) {
        start = collapseThreeDiv.querySelectorAll('.forHousesCls').length - 4 + apiData.length
        htmlData += `<button id="housesShowMoreIdBtn" class="show-more" data-start="${start}" onclick="getauctionHouses(event, 'houses')">Show More</button>`
    }
    collapseThreeDiv.innerHTML = htmlData
}

function locationsSetter(apiData) {
    document.querySelector('#locationsShowMoreIdBtn').remove()
    let htmlData = collapseFourDiv.innerHTML
    apiData.forEach(auctionHousesData => {
        htmlData += `<div class="form-check">
                        <input class="form-check-input forLocationsCls" type="checkbox" value="" id="${auctionHousesData.cah_auction_house_location}" onblur="filterAuction(event)">
                        <label class="form-check-label" for="${auctionHousesData.cah_auction_house_location}">${auctionHousesData.cah_auction_house_location}</label>
                    </div>`
    })
    if (10 === apiData.length) {
        start = collapseFourDiv.querySelectorAll('.forLocationsCls').length - 4 + apiData.length
        htmlData += `<button id="locationsShowMoreIdBtn" data-start="${start}" class="show-more" onclick="getauctionHouses(event, 'locations')">Show More</button>`
    }
    collapseFourDiv.innerHTML = htmlData
}

async function getauctionHouses(e, housesOrLocationsStr) {
    queryParams = ''
    if (housesOrLocationsStr === 'houses') {
        start = e.target.dataset.start
        queryParams += `start=${start}&houses=true&`
    }
    if (housesOrLocationsStr === 'locations') {
        start = e.target.dataset.start
        queryParams += `start=${start}&locations=true&`
    }
    const apiData = await fetch(`/auction/getAuctionHousesOrLocations/?${queryParams}limit=10`, {
                        method: 'GET',
                    })
                        .then(response => response.json())
                        .then(body => body)
    if (housesOrLocationsStr === 'houses') {
        housesSetter(apiData)
    }
    if (housesOrLocationsStr === 'locations') {
        locationsSetter(apiData)
    }

}

document.addEventListener('DOMContentLoaded', function () {
    pastTrendingAuctionSetter('', 0, 50)
})
