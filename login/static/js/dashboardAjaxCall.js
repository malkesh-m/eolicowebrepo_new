// const totalFollowedArtistsId = document.querySelector('#totalFollowedArtistsId')
// const thisWeekFollowedArtistsId = document.querySelector('#thisWeekFollowedArtistsId')
const totalFollowedArtistId  = document.querySelector('#totalFollowedArtistId')
const totalFollowedArtworksId = document.querySelector('#totalFollowedArtworksId')
// const paintingsFollowedId = document.querySelector('#paintingsFollowedId')
// const printsFollowedId = document.querySelector('#printsFollowedId')
// const workOnPaperFollowedId = document.querySelector('#workOnPaperFollowedId')
// const sculpturesFollowedId = document.querySelector('#sculpturesFollowedId')
const artistTableBodyId = document.querySelector('#artistTableBodyId')
const artworksTableBodyId = document.querySelector('#artworksTableBodyId')

function getMyArtworksDetailsSetter() {
    fetch('/login/getMyArtworksDetails/', {
        method: "GET",
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = ''
            body.forEach(artworkData => {
                htmlData += `<tr>
                                <td>${artworkData.faa_artwork_title}</td>
                                <td>${artworkData.fa_artist_name}</td>
                                <td>${artworkData.faa_artwork_category}</td>
                                <td><strong>${artworkData.cah_auction_house_currency_code}: </strong>`
                                if(artworkData.fal_lot_low_estimate) {
                                    htmlData += `${artworkData.fal_lot_low_estimate}`
                                }
                                else {
                                    htmlData += `0`
                                }
                                htmlData += `- `
                                if(artworkData.fal_lot_high_estimate) {
                                    htmlData += `${artworkData.fal_lot_high_estimate}`
                                }
                                else {
                                    htmlData += `0`
                                }
                                htmlData += `<br> <strong>USD: </strong>`
                                if(artworkData.fal_lot_low_estimate_USD) {
                                    htmlData += `${artworkData.fal_lot_low_estimate_USD}`
                                }
                                else {
                                    htmlData += `0`
                                }
                                htmlData += `- `
                                if(artworkData.fal_lot_high_estimate_USD) {
                                    htmlData += `${artworkData.fal_lot_high_estimate_USD}`
                                }
                                else {
                                    htmlData += `0`
                                }
                                htmlData += `</td>
                                <td><strong>${artworkData.cah_auction_house_currency_code}: </strong>`
                                if(artworkData.fal_lot_sale_price) {
                                    htmlData += `${artworkData.fal_lot_sale_price}`
                                }
                                else {
                                    htmlData += `Unsold`
                                }
                                htmlData += `<br> <strong>USD:</strong> `
                                if (artworkData.fal_lot_sale_price_USD) {
                                    htmlData += `${artworkData.fal_lot_sale_price_USD}`
                                }
                                else {
                                    htmlData += 'Unsold'
                                }
                                htmlData += `</td>
                                <td><strong>Lot No:</strong> ${artworkData.fal_lot_no} <br> <strong>Sale Title:</strong> ${artworkData.faac_auction_title} <br> <strong>Sale Name:</strong> ${artworkData.cah_auction_house_name} <br> <strong>Sale Location:</strong> ${artworkData.cah_auction_house_location} <br> <strong>Sale Date:</strong> ${artworkData.fal_lot_sale_date}</td>
                            </tr>`
            })
            artworksTableBodyId.innerHTML = htmlData
            $('#artworks').DataTable()
        })
}

function chartMaker(elementId, xValues, yValues, barColors) {
    new Chart(elementId, {
        type: "doughnut",
        data: {
                labels: xValues,
                datasets: [{
                                backgroundColor: barColors,
                                data: yValues,
                                
                }]
        },
        options: {
            title: {
                display: true,
                text: ""
            },
            legend: {
                display: true,
                position: 'bottom',
                labels: {
                    fontSize: 17,
                    fontFamily: 'GT Super Ds Trial Bd'
                }
            }
        }
    })
}

function getMyArtistsDetailsSetter() {
    fetch('/login/getMyArtistsDetails/', {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = ''
            body.forEach(artistData => {
                htmlData += `<tr>
                                <td>${artistData.artistName}</td>
                                <td>${artistData.totalArtworkData}</td>
                                <td><strong>USD: </strong>${artistData.averageSellingPrice}</td>
                                <td>${artistData.averageSellingRate}%</td>
                                <td>${artistData.averageSellingPriceInLast12Month}</td>
                                <td>${artistData.totalArtworkSoldInLast12Month}</td>
                            </tr>`
            })
            artistTableBodyId.innerHTML = htmlData 
            $('#artists').DataTable()
        })
}

function getFollowedArtistsCounter() {
    fetch('/login/getFollowedArtists/', {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            totalFollowedArtistId.innerHTML = body.user_artist_followed_counts
            // thisWeekFollowedArtistsId.innerHTML = body.this_week_followed_artist_counts
            let xValues = [`Total Followed: ${body.user_artist_followed_counts}`, `Followed This Week: ${body.this_week_followed_artist_counts}`]
            let yValues = [body.user_artist_followed_counts, body.this_week_followed_artist_counts]
            let barColors = ["#2b5797", "#00aba9"]
            chartMaker("Artits", xValues, yValues, barColors)
        })
}

function getFollowedArtworksCounter() {
    fetch('/login/getFollowedArtworks/', {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            totalFollowedArtworksId.innerHTML = body.user_artwork_followed_counts
            // paintingsFollowedId.innerHTML = body.forPaintingsFollowed
            // printsFollowedId.innerHTML = body.forPrintsFollowed
            // workOnPaperFollowedId.innerHTML = body.forWorkOnPaperFollowed
            // sculpturesFollowedId.innerHTML = body.forSculpturesFollowed
            let xValues = [`Paintings: ${body.forPaintingsFollowed}`, `Prints: ${body.forPrintsFollowed}`, `Works on Paper: ${body.forWorkOnPaperFollowed}`, `Sculptures: ${body.forSculpturesFollowed}`]
            let yValues = [body.forPaintingsFollowed, body.forPrintsFollowed, body.forWorkOnPaperFollowed, body.forSculpturesFollowed]
            let barColors = ["#00aba9", "#2b5797", "#e8c3b9", "#1e7145"]
            chartMaker("Artworks", xValues, yValues, barColors)
        })
}

async function dataBinder() {
    getFollowedArtistsCounter()
    getFollowedArtworksCounter()
    getMyArtistsDetailsSetter()
    getMyArtworksDetailsSetter()
}

document.addEventListener('DOMContentLoaded', function () {
    dataBinder()
})