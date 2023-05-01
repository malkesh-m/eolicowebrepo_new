const urlParams = new URLSearchParams(location.search)
const pastauctionsDiv = document.querySelector('#pastauctions')
const collapseThreeDiv = document.querySelector('#collapseThree')
const collapseFourDiv = document.querySelector('#collapseFour')
const auctionHouseId = urlParams.get('ahid')
const auctionHouseHeaderId = document.querySelector('#auctionHouseHeaderId')
const forPaginationDivId = document.querySelector('#forPaginationDivId')
let pastUpcomingStrData = 'past'
let auctionHouseName = ''
let passwordShowHideFlag = false
let start = 0
let limit = 50

function htmlBinder(recentAuctionData) {
    htmlData = `<div class="col-sm-12 col-md-6 col-lg-4 col-xl-3 mb-4 auctionData">
                <div class="latest-artists">
                    <a href="/auction/showauction/?aucid=${recentAuctionData.faac_auction_ID}"
                        class="latest-card">
                        <img src="https://f000.backblazeb2.com/file/fineart-images/${recentAuctionData.faac_auction_image}"
                            class="card-img" alt="img" style="height: 245px;" />
                        <div class="down-content">
                            <div class="d-flex justify-content-between">
                                <p class="lineSplitSetter">${recentAuctionData.faac_auction_title}</p>
                            
                            </div>
                            <h5>${recentAuctionData.cah_auction_house_name}</h5>
                            <span>${recentAuctionData.faac_auction_start_date} | ${recentAuctionData.cah_auction_house_location}</span>
                        </div>
                    </a>
                    </div>
                </div>`
    return htmlData
}

function paginationSetter(reposeBodyLength) {
    if (reposeBodyLength < limit) {
        document.querySelector('#paginationNextBtnId').classList.add('disabled')
    }
    if (start > 0) {
        document.querySelector('#paginationPrevBtnId').classList.remove('disabled')
    }
    forPaginationDivId.style.display = 'inline-block'
}

function pastAuctionHousesSetter(queryParams) {
    fetch(`/login/getRecentAuctions/?auctionHouseName=${auctionHouseName}&start=${start}&${queryParams}limit=${limit}`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = ''
            body.forEach(auctionData => {
                htmlData += htmlBinder(auctionData)
            })
            pastauctionsDiv.innerHTML = htmlData
            paginationSetter(body.length)
        })
}

function passwordShowHide(elementId) {
    const passwordEle = document.querySelector(elementId)
    if (passwordShowHideFlag) {
        passwordEle.type = 'text'
        passwordShowHideFlag = false
    }
    else {
        passwordEle.type = 'password'
        passwordShowHideFlag = true
    }
}

function upcomingAuctionHousesSetter(queryParams) {
    fetch(`/login/getUpcomingAuctions/?auctionHouseName=${auctionHouseName}&start=${start}&${queryParams}limit=${limit}`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = ''
            body.forEach(auctionData => {
                htmlData += htmlBinder(auctionData)
            })
            pastauctionsDiv.innerHTML = htmlData
            paginationSetter(body.length)
        })
}

function filterAuction(event) {
    const auctionTitle = document.querySelector('#auctionTitleTextId')
    const defaultCheck1 = document.querySelector('#defaultCheck1')
    const forLocationsCls = document.querySelectorAll('.forLocationsCls')
    const fromDate = document.querySelector('#fromDate')
    const toDate = document.querySelector('#toDate')
    let queryParams = ''

    if (auctionTitle.value) {
        queryParams += `auctionTitle=${auctionTitle.value}&`
    }
    if (defaultCheck1.checked) {
        queryParams += `saleDate=true&`
    }
    if (fromDate.value) {
        queryParams += `fromDate=${fromDate.value}&`
    }
    if (toDate.value) {
        queryParams += `toDate=${toDate.value}&`
    }
    let locationsStr = ''
    forLocationsCls.forEach(locations => {
        if (locations.checked) {
            locationsStr += locations.value + ','
        }
    })
    if (locationsStr) {
        queryParams += `locations=${locationsStr}&`
    }
    if (pastUpcomingStrData === 'past') {
        pastAuctionHousesSetter(queryParams)
    }
    else if (pastUpcomingStrData === 'upcoming') {
        upcomingAuctionHousesSetter(queryParams)
    }
}

function perPageSetter(event) {
    start = 0
    limit = document.querySelector('#inputGroupSelect01').value
    filterAuction(event)
}

function paginationNextPrevious(event, nextOrPrevStr) {
    if (nextOrPrevStr === 'next') {
        start = start + limit
    }
    else {
        start = Math.abs(limit - start)
    }
    filterAuction(event)
}

function pastUpcomingAuction(e, pastUpcomingStr) {
    pastUpcomingStrData = pastUpcomingStr
    filterAuction(e)
}

function locationsSetter(apiData) {
    document.querySelector('#locationsShowMoreIdBtn').remove()
    let htmlData = collapseFourDiv.innerHTML
    apiData.forEach(auctionHousesData => {
        htmlData += `<div class="form-check">
                        <input class="form-check-input forLocationsCls" type="checkbox" value="${auctionHousesData.cah_auction_house_location}" id="${auctionHousesData.cah_auction_house_location}" onblur="filterAuction(event)">
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
    let queryParams = ''
    if (housesOrLocationsStr === 'locations') {
        start = e.target.dataset.start
        queryParams += `start=${start}&locations=true&`
    }
    const apiData = await fetch(`/auction/getAuctionHousesOrLocations/?${queryParams}limit=10&ahid=${auctionHouseId}`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => body)
    if (housesOrLocationsStr === 'locations') {
        locationsSetter(apiData)
    }
}

function getAuctionHouseData() {
    fetch(`/auctionhouse/getCurrentAuctionHouse/?ahid=${auctionHouseId}`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            auctionHouseName = body.cah_auction_house_name
            auctionHouseHeaderId.innerHTML = auctionHouseName
            pastAuctionHousesSetter('', 0, 50)
        })
}

document.addEventListener('DOMContentLoaded', function () {
    forPaginationDivId.style.display = 'none'
    getAuctionHouseData()
    // pastTrendingAuctionSetter('', 0, 50)
})