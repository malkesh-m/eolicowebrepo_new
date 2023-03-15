const totalFollowedArtistsId = document.querySelector('#totalFollowedArtistsId')
const thisWeekFollowedArtistsId = document.querySelector('#thisWeekFollowedArtistsId')
const totalFollowedArtistId  = document.querySelector('#totalFollowedArtistId')
const totalFollowedArtworksId = document.querySelector('#totalFollowedArtworksId')
const paintingsFollowedId = document.querySelector('#paintingsFollowedId')
const printsFollowedId = document.querySelector('#printsFollowedId')
const workOnPaperFollowedId = document.querySelector('#workOnPaperFollowedId')
const sculpturesFollowedId = document.querySelector('#sculpturesFollowedId')
const artistTableBodyId = document.querySelector('#artistTableBodyId')

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
})