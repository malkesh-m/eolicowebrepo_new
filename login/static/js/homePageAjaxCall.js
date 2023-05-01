const getTrendingArtistDiv = document.querySelector('#getTrendingArtistId')
const getUpcomingAuctionsDiv = document.querySelector('#getUpcomingAuctionsId')
const getRecentAuctionsDiv = document.querySelector('#getRecentAuctionsId')
const myCarousel = document.querySelector('#myCarousel')
const subscribeFormId = document.querySelector('#subscribeFormId')

let passwordShowHideFlag = false

function owlSlider(sliderId) {
    let owl = $(sliderId);
    owl.owlCarousel({
        items: 3,
        margin: 10,
        loop: false,
        nav: true,
        responsive: {
            0: {
                items: 1,
                nav: false
            },
            600: {
                items: 2,
                nav: false
            },
            1000: {
                items: 3,
                nav: true,
                loop: true
            }
        }
    });
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

function trendingArtistSlider() {
    fetch('/login/getTrendingArtist/?start=0&limit=6', {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = ``
            body.forEach(artistData => {
                htmlData = htmlData + `
                    <div class="item">
                    <a href=/artist/details/?aid="${artistData.fa_artist_ID}" class="latest-card">
                        <img src="https://f000.backblazeb2.com/file/fineart-images/${artistData.fa_artist_image}"
                            class="card-img" alt="img" />
                        <div class="down-content">
                            <div class="d-flex justify-content-between">
                                <h4 class="lineSplitSetter">${artistData.fa_artist_name}</h4>
                                <p>View Details</p>
                            </div>
                            <span>${artistData.fa_artist_nationality}, ${artistData.fa_artist_birth_year}` 
                            if (artistData.fa_artist_death_year != 0) {
                                htmlData = htmlData + ` - ${artistData.fa_artist_death_year}`
                            }
                            htmlData = htmlData + `</span></div></a></div>`
            });
            getTrendingArtistDiv.innerHTML = htmlData;
            owlSlider('#getTrendingArtistId')
        })
}

function upcomingAuctionSlider() {
    fetch('/login/getUpcomingAuctions/?start=0&limit=6', {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = ''
            body.forEach(upcomigAuctionData => {
                htmlData = htmlData + `
                    <div class="item">
                    <a href="/auction/showauction/?aucid=${upcomigAuctionData.faac_auction_ID}"
                        class="latest-card">
                        <img src="https://f000.backblazeb2.com/file/fineart-images/${upcomigAuctionData.faac_auction_image}"
                            class="card-img" alt="img" />
                        <div class="down-content">
                            <div class="d-flex justify-content-between">
                                <h4 class="lineSplitSetter">${upcomigAuctionData.faac_auction_title}</h4>
                                <p>View Details</p>
                            </div>
                            <h5>${upcomigAuctionData.cah_auction_house_name}</h5>
                            <span>${upcomigAuctionData.faac_auction_start_date} | ${upcomigAuctionData.cah_auction_house_location}</span>
                        </div>
                    </a>
                </div>`
            })
            getUpcomingAuctionsDiv.innerHTML = htmlData
            owlSlider('#getUpcomingAuctionsId')
        })
}

subscribeFormId.addEventListener('submit', function(event) {
    event.preventDefault()

    const subName = event.target.elements['subName'].value
    const subEmail = event.target.elements['subEmail'].value
    const formData = new FormData()
    formData.append('subName', subName)
    formData.append('subEmail', subEmail)

    fetch(`/login/subcribeContact/`, {
        method: 'POST',
        body: formData,
    })
        .then(response => response.json())
        .then(body => {
            console.log(body)
        })
})

function recentAuctionSlider() {
    fetch('/login/getRecentAuctions/?start=0&limit=6', {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = ''
            body.forEach(recentAuctionData => {
                htmlData = htmlData + `
                    <div class="item">
                    <a href="/auction/showauction/?aucid=${recentAuctionData.faac_auction_ID}"
                        class="latest-card">
                        <img src="https://f000.backblazeb2.com/file/fineart-images/${recentAuctionData.faac_auction_image}"
                            class="card-img" alt="img" />
                        <div class="down-content">
                            <div class="d-flex justify-content-between">
                                <h4 class="lineSplitSetter">${recentAuctionData.faac_auction_title}</h4>
                                <p>View Details</p>
                            </div>
                            <h5>${recentAuctionData.cah_auction_house_name}</h5>
                            <span>${recentAuctionData.faac_auction_start_date} | ${recentAuctionData.cah_auction_house_location}</span>
                        </div>
                    </a>
                </div>`
            })
            getRecentAuctionsDiv.innerHTML = htmlData
            owlSlider('#getRecentAuctionsId')
        })
}

function topUpcomingLotsOfWeek() {
    fetch(`/login/topUpcomingLotsOfWeek/`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = `<div class="carousel-inner">`
            let i = 0
            body.forEach(lotData => {
                htmlData += `<div class="carousel-item ${i == 0 ? ' active': ''}">
                                <div class="mask flex-center">
                                    <div class="container">
                                        <div class="row align-items-center">
                                            <div class="col-md-7 col-12 order-md-1 order-2">
                                                <h4>${lotData.faa_artwork_title}</h4>
                                                <h4 class="h5-style">${lotData.faa_artist_name}</h4>
                                                <h4 class="h5-style mb-4">USD ${lotData.fal_lot_low_estimate_USD} – ${lotData.fal_lot_high_estimate_USD}</h4>
                                                <p class="mb-2">${lotData.faac_auction_title}</p>
                                                <p class="mb-4">${lotData.cah_auction_house_name}, ${lotData.cah_auction_house_location} | ${lotData.faac_auction_start_date}</p>
                                                <a href="/auction/showauction/?aucid=${lotData.faac_auction_ID}">View Auction</a>
                                            </div>
                                            <div class="col-md-5 col-12 order-md-2 order-1">
                                                <div class="slider-img">
                                                    <img src="https://f000.backblazeb2.com/file/fineart-images/${lotData.faa_artwork_image1}?maxwidth=1010&maxheight=650" class="mx-auto" alt="slide">
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>`
                            i += 1
            })
            htmlData += `</div>
                        <a class="carousel-control-prev" href="#myCarousel" role="button" data-slide="prev">
                            <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                            <span class="sr-only">Previous</span> 
                        </a>
                        <a class="carousel-control-next" href="#myCarousel"role="button" data-slide="next"> <span class="carousel-control-next-icon" aria-hidden="true"></span>
                            <span class="sr-only">Next</span>
                        </a>`
            myCarousel.innerHTML = htmlData
            // $('#myCarousel').carousel({
            //     interval: 300,
            // })
        })
}

async function setSlider() {
    // trendingArtistSlider()
    // upcomingAuctionSlider()
    // recentAuctionSlider()
    topUpcomingLotsOfWeek()
}

document.addEventListener('DOMContentLoaded', function () {

    setSlider()

})
