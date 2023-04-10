const featuredshowsDivId = document.querySelector('#featuredshowsDivId')
const alphabetSearchUlId = document.querySelector('#alphabetSearchUlId')
const filterHeaderId = document.querySelector('#filterHeaderId')
const mainFilterLoaderId = document.querySelector('#mainFilterLoaderId')
let auctionHousesData = []
let passwordShowHideFlag = false

function searchByAlphabet(e) {
    filterHeaderId.parentElement.className = "col-lg-12 text-center"
    mainFilterLoaderId.style.display = 'inline-block'
    filterHeaderId.style.display = 'none'
    featuredshowsDivId.style.display = 'none'
    let searchAuctionhousesKeyword = e.target.dataset.id
    fetch(`/auctionhouse/getFeaturedAuctionHouses/?keyword=${searchAuctionhousesKeyword}`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = ''
            mainFilterLoaderId.style.display = 'none'
            filterHeaderId.style.display = 'block'
            filterHeaderId.parentElement.className = "col-lg-12 text-left"
            filterHeaderId.innerHTML = searchAuctionhousesKeyword
            body.forEach(auctionHouseData => {
                htmlData = htmlData + `
                                        <div class="col-sm-6 col-md-3 col-xl-2 mb-4">
                                        <a href="/auctionhouse/details/?ahid=${auctionHouseData.cah_auction_house_ID}" style="color:#000000;">
                                        <h6 class="lineSplitSetter">${auctionHouseData.cah_auction_house_name}</h6> <p>${auctionHouseData.cah_auction_house_location}</p></a>
                                        </div>`
            })
            featuredshowsDivId.style.display = 'flex'
            featuredshowsDivId.innerHTML = htmlData
        })
}

function alphabetUlSetter() {
    let htmlData = ''
    for(let i=65; i<=90; i++) {
        htmlData = htmlData + `
        <li class="list-alfabat"><button class="alphabetBtn" data-id="${String.fromCharCode(i)}" onclick="searchByAlphabet(event)">${String.fromCharCode(i)}</button></li>`
    }
    alphabetSearchUlId.innerHTML = htmlData
}

function getFeaturedAuctionHousesData() {
    fetch('/auctionhouse/getFeaturedAuctionHouses/', {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = ''
            body.forEach(auctionHouseData => {
                htmlData = htmlData + `
                    <div class="col-sm-6 col-md-3 col-xl-2 mb-4">
                    <div class="img-box m-0">
                        <a href="/auctionhouse/details/?ahid=${auctionHouseData.cah_auction_house_ID}"><img src="${auctionHouseData.cah_auction_house_image}" alt="" style='width:100px;height:100px;display:flex; margin: auto; border-radius:100% ;' /></a>
                        <a href="/auctionhouse/details/?ahid=${auctionHouseData.cah_auction_house_ID}" style="color:#000000;">
                            <h4>${auctionHouseData.cah_auction_house_name} </h4>
                        </a>
                    </div>
                </div>`
            })
            featuredshowsDivId.innerHTML = htmlData
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

function getAuctionHousesData() {
    fetch('/auctionhouse/getAuctionHouses/', {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            auctionHousesData = body
        })
}

document.addEventListener('DOMContentLoaded', function () {
    mainFilterLoaderId.style.display = 'none'
    alphabetUlSetter()
    getFeaturedAuctionHousesData()
    getAuctionHousesData()

})