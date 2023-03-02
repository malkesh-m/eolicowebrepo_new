const featuredshowsdiv = document.querySelector('#featuredshowsdiv')
const alphabetSearchUlId = document.querySelector('#alphabetSearchUlId')
let auctionHousesData = []

function searchByAlphabet(e) {
    let searchAuctionhousesKeyword = e.target.dataset.id
    fetch(`/auctionhouse/getFeaturedAuctionHouses/?keyword=${searchAuctionhousesKeyword}`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = ''
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
                        <a href="/auctionhouse/details/?ahid=${auctionHouseData.cah_auction_house_ID}}" style="color:#000000;">
                            <h4>${auctionHouseData.cah_auction_house_name} </h4>
                        </a>
                    </div>
                </div>`
            })
            featuredshowsdiv.innerHTML = htmlData
        })
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
    alphabetUlSetter()
    getFeaturedAuctionHousesData()
    getAuctionHousesData()

})