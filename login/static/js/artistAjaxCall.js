const alphabetSearchUlId = document.querySelector('#alphabetSearchUlId')
const getTrendingArtistDiv = document.querySelector('#getTrendingArtistId')

function alphabetUlSetter() {
    let htmlData = ''
    for (let i = 65; i <= 90; i++) {
        htmlData = htmlData + `
        <li class="list-alfabat"><button class="alphabetBtn" data-id="${String.fromCharCode(i)}" onclick="searchByAlphabet(event)">${String.fromCharCode(i)}</button></li>`
    }
    alphabetSearchUlId.innerHTML = htmlData
}

function trendingArtistData(start) {
    let limit = 30
    document.querySelector('#trendingArtistViewMoreId').remove()
    fetch(`/login/getTrendingArtist/?start=${start}&limit=${limit}`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = getTrendingArtistDiv.innerHTML
            body.forEach(artistData => {
                htmlData = htmlData + `
                <div class="col-md-4 mb-4 trendingArtistRowDataCls">
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
            let offSet = document.querySelectorAll('.trendingArtistRowDataCls').length + body.length
            if ( body.length == limit ) {
                htmlData = htmlData + `<div class="col-12 text-center mt-4" id="trendingArtistViewMoreId">
                    <button type="button" class="btn btn-login btn-round py-2" onclick="trendingArtistData(${offSet})">View More</button>
                </div>`
            }
            getTrendingArtistDiv.innerHTML = htmlData
        })
}

document.addEventListener('DOMContentLoaded', function () {
    alphabetUlSetter()
    trendingArtistData(0)
})
