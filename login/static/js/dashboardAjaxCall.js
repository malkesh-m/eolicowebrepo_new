const totalFollowedArtistsId = document.querySelector('#totalFollowedArtistsId')
const thisWeekFollowedArtistsId = document.querySelector('#thisWeekFollowedArtistsId')
const totalFollowedArtistId  = document.querySelector('#totalFollowedArtistId')
const totalFollowedArtworksId = document.querySelector('#totalFollowedArtworksId')
const paintingsFollowedId = document.querySelector('#paintingsFollowedId')
const printsFollowedId = document.querySelector('#printsFollowedId')
const workOnPaperFollowedId = document.querySelector('#workOnPaperFollowedId')
const sculpturesFollowedId = document.querySelector('#sculpturesFollowedId')
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
                                <td>`
                                if(artworkData.fal_lot_low_estimate) {
                                    htmlData += `${artworkData.fal_lot_low_estimate}`
                                }
                                else {
                                    htmlData += `0`
                                }
                                htmlData += `- ${artworkData.fal_lot_high_estimate}</td>
                                <td>`
                                if (artworkData.fal_lot_sale_price) {
                                    htmlData += `${artworkData.fal_lot_sale_price}`
                                }
                                else {
                                    htmlData += '0'
                                }
                                htmlData += `</td>
                                <td><strong>Lot No:</strong> ${artworkData.fal_lot_no} <br> <strong>Sale Title:</strong> ${artworkData.faac_auction_title} <br> <strong>Sale Name:</strong> ${artworkData.cah_auction_house_name} <br> <strong>Sale Location:</strong> ${artworkData.cah_auction_house_location} <br> <strong>Sale Date:</strong> ${artworkData.fal_lot_sale_date}</td>
                            </tr>`
            })
            artworksTableBodyId.innerHTML = htmlData
            $('#artworks').DataTable()
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
                                <td>${artistData.averageSellingPrice}</td>
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
            totalFollowedArtistsId.innerHTML = totalFollowedArtistId.innerHTML = body.user_artist_followed_counts
            thisWeekFollowedArtistsId.innerHTML = body.this_week_followed_artist_counts
        })
}

function getFollowedArtworksCounter() {
    fetch('/login/getFollowedArtworks/', {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            totalFollowedArtworksId.innerHTML = body.user_artwork_followed_counts
            paintingsFollowedId.innerHTML = body.forPaintingsFollowed
            printsFollowedId.innerHTML = body.forPrintsFollowed
            workOnPaperFollowedId.innerHTML = body.forWorkOnPaperFollowed
            sculpturesFollowedId.innerHTML = body.forSculpturesFollowed
        })
}

document.addEventListener('DOMContentLoaded', function () {
    getFollowedArtistsCounter()
    getFollowedArtworksCounter()
    getMyArtistsDetailsSetter()
    getMyArtworksDetailsSetter()
})