const totalFollowedArtistId  = document.querySelector('#totalFollowedArtistId')
const totalFollowedArtworksId = document.querySelector('#totalFollowedArtworksId')
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
                                <td class="forAlign">${artworkData.faa_artwork_category}</td>
                                <td class="forAlign"><strong>${artworkData.cah_auction_house_currency_code} </strong>`
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
                                if (artworkData.cah_auction_house_currency_code !== 'USD') {
                                    htmlData += `<br> <strong>USD </strong>`
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
                                }
                                htmlData += `</td>
                                <td class="forAlign"><strong>${artworkData.cah_auction_house_currency_code} </strong>`
                                if(artworkData.fal_lot_sale_price) {
                                    htmlData += `${artworkData.fal_lot_sale_price}`
                                }
                                else {
                                    htmlData += `Unsold`
                                }
                                if (artworkData.cah_auction_house_currency_code !== 'USD') {
                                    htmlData += `<br> <strong>USD </strong> `
                                    if (artworkData.fal_lot_sale_price_USD) {
                                        htmlData += `${artworkData.fal_lot_sale_price_USD}`
                                    }
                                    else {
                                        htmlData += 'Unsold'
                                    }
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
                                <td class="forAlign">${artistData.totalArtworkData}</td>
                                <td class="forAlign"><strong>USD </strong>${artistData.averageSellingPrice}</td>
                                <td class="forAlign">${artistData.averageSellingRate}%</td>
                                <td class="forAlign">${artistData.totalArtworkSoldInLast12Month}</td>
                                <td class="forAlign">${artistData.averageSellingPriceInLast12Month}</td>
                                <td class="forAlign">${artistData.averageSellingRateIn12Month}%</td>
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
            let xValues = [`Total Followed: ${body.user_artist_followed_counts}`, `Followed This Week: ${body.this_week_followed_artist_counts}`]
            let yValues = [body.user_artist_followed_counts, body.this_week_followed_artist_counts]
            let barColors = ["#85C1E9", "#F8C471"]
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
            let otherValues = body.user_artwork_followed_counts - (body.forPaintingsFollowed + body.forPrintsFollowed + body.forWorkOnPaperFollowed + body.forSculpturesFollowed + body.forPhotographsFollowed + body.forMiniaturesFollowed)
            let xValues = [`Paintings: ${body.forPaintingsFollowed}`, `Prints: ${body.forPrintsFollowed}`, `Works on Paper: ${body.forWorkOnPaperFollowed}`, `Sculptures: ${body.forSculpturesFollowed}`, `Photographs: ${body.forPhotographsFollowed}`, `Miniatures: ${body.forMiniaturesFollowed}`, `Others: ${otherValues}`]
            let yValues = [body.forPaintingsFollowed, body.forPrintsFollowed, body.forWorkOnPaperFollowed, body.forSculpturesFollowed, body.forPhotographsFollowed, body.forMiniaturesFollowed, otherValues]
            let barColors = ["#76D7C4", "#7FB3D5", "#F7DC6F", "#AF7AC5", "#F5B041", "#5499C7", "#5D6D7E"]
            chartMaker("Artworks", xValues, yValues, barColors)
        })
}

document.addEventListener('DOMContentLoaded', function () {
    getFollowedArtistsCounter()
    getFollowedArtworksCounter()
    getMyArtistsDetailsSetter()
    getMyArtworksDetailsSetter()
})