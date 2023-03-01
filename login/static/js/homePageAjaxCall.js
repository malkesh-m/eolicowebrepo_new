const getTrendingArtistDiv = document.querySelector('#getTrendingArtistId')
const getUpcomingAuctionsDiv = document.querySelector('#getUpcomingAuctionsId')
const getRecentAuctionsDiv = document.querySelector('#getRecentAuctionsId')

function owlSlider(sliderId) {
    var owl = $(sliderId);
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

function trendingArtistSlider() {
    fetch('/login/getTrendingArtist/', {
        method: 'GET',
    })
        .then(response => response.json())
            .then(body => {
                let htmlData = ``
                body.forEach(artistData => {
                    htmlData = htmlData + `
                    <div class="item">
                    <a href=/artist/details/?aid="${artistData.fa_artist_ID }" class="latest-card">
                        <img src="https://f000.backblazeb2.com/file/fineart-images/${ artistData.fa_artist_image}"
                            class="card-img" alt="img" />
                        <div class="down-content">
                            <div class="d-flex justify-content-between">
                                <h4 class="lineSplitSetter">${artistData.fa_artist_name}</h4>
                                <p>View Details</p>
                            </div>
                            <span>${artistData.fa_artist_nationality }, ${artistData.fa_artist_birth_year} - ${artistData.fa_artist_death_year}</span>
                        </div>
                    </a>
                    </div>`
                });
                getTrendingArtistDiv.innerHTML = htmlData;
                owlSlider('#getTrendingArtistId')
            })
}

function upcomingAuctionSlider() {
    fetch('/login/getUpcomingAuctions/', {
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

function recentAuctionSlider() {
    fetch('/login/getRecentAuctions/', {
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

async function setSlider() {

    trendingArtistSlider()
    upcomingAuctionSlider()
    recentAuctionSlider()

}

document.addEventListener('DOMContentLoaded', function () {

    setSlider()

})
