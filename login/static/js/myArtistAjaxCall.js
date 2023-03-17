const getMyArtistDataDivId = document.querySelector('#getMyArtistDataDivId')

function getMyArtistsDataSetter(start) {
    document.querySelector('#viewMoreBtnId').remove()
    fetch(`/login/getMyArtists/?start=${start}&limit=9`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = getMyArtistDataDivId.innerHTML
            body.forEach(artistData => {
                htmlData += `<div class="col-md-4 mb-4 myArtistDataCls">
                                <a href="/login/myArtistDetails/?aid=${artistData.fa_artist_ID}" class="latest-card">
                                    <img src="https://f000.backblazeb2.com/file/fineart-images/${artistData.fa_artist_image}" class="card-img" alt="img">
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
            })
            let offset = document.querySelectorAll('.myArtistDataCls').length + body.length
            if ( body.length === 9 ) {
                htmlData += `<div class="col-12 text-center mt-4" id="viewMoreBtnId">
                                <button type="button" class="btn btn-login btn-round py-2" onclick="getMyArtistsDataSetter(${offset})">View More</button>
                            </div>`
            }
            getMyArtistDataDivId.innerHTML = htmlData
        })
}

    document.addEventListener('DOMContentLoaded', function () {
    getMyArtistsDataSetter(0)
})
