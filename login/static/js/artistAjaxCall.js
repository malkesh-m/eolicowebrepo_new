const alphabetSearchUlId = document.querySelector('#alphabetSearchUlId')
const getTrendingArtistDiv = document.querySelector('#getTrendingArtistId')
const filterHeaderId = document.querySelector('#filterHeaderId')
const featuredshowsDivId = document.querySelector('#featuredartistsdiv')
const mainFilterLoaderId = document.querySelector('#mainFilterLoaderId')
let passwordShowHideFlag = false

function searchByAlphabet(e, start) {
    let limit = 100
    filterHeaderId.parentElement.className = "col-lg-12 text-center"
    mainFilterLoaderId.style.display = 'inline-block'
    filterHeaderId.style.display = 'none'
    getTrendingArtistDiv.style.display = 'none'
    if (e.target.dataset.alphabet) {
        document.querySelectorAll(".alphabetrtistSearch").forEach(el => el.remove())
    }
    let searchArtistKeyword = e.target.dataset.id
    fetch(`/artist/searchArtists/?keyword=${searchArtistKeyword}&start=${start}&limit=${limit}`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            document.querySelectorAll(".trendingArtistRowDataCls").forEach(el => el.remove())
            if (document.querySelector('#trendingArtistViewMoreId')) {
                document.querySelector('#trendingArtistViewMoreId').remove()
            }
            let htmlData = getTrendingArtistDiv.innerHTML
            mainFilterLoaderId.style.display = 'none'
            filterHeaderId.style.display = 'block'
            filterHeaderId.parentElement.className = "col-lg-12 text-left"
            filterHeaderId.innerHTML = searchArtistKeyword
            body.forEach(artistData => {
                htmlData = htmlData + `<div class="col-sm-6 col-md-3 col-xl-2 mb-4 alphabetrtistSearch">
                                        <a href=/artist/details/?aid="${artistData.fa_artist_ID}" style="color:#000000;">
                                        <h6 class="lineSplitSetter">${artistData.fa_artist_name}</h6>`
                if (artistData.fa_artist_nationality !== 'na') {
                    htmlData = htmlData + `<p>${artistData.fa_artist_nationality}</p>`
                }
                if (artistData.fa_artist_birth_year != 0) {
                    htmlData = htmlData + `<p>${artistData.fa_artist_birth_year}`
                    if (artistData.fa_artist_death_year != 0) {
                        htmlData = htmlData + ` - ${artistData.fa_artist_death_year}`
                    }
                    htmlData = htmlData + '</p>'
                }
                htmlData = htmlData + `</a></div>`
            })
            let offSet = document.querySelectorAll('.alphabetrtistSearch').length + body.length
            if ( body.length == limit ) {
                htmlData = htmlData + `<div class="col-12 text-center mt-4" id="trendingArtistViewMoreId">
                    <button type="button" class="btn btn-login btn-round py-2" data-id="${searchArtistKeyword}" onclick="searchByAlphabet(event,${offSet})">View More</button>
                </div>`
            }
            getTrendingArtistDiv.style.display = 'flex'
            getTrendingArtistDiv.innerHTML = htmlData
        })
}

function alphabetUlSetter() {
    let htmlData = ''
    for (let i = 65; i <= 90; i++) {
        htmlData = htmlData + `
        <li class="list-alfabat"><button class="alphabetBtn" data-id="${String.fromCharCode(i)}" data-alphabet="${String.fromCharCode(i)}" onclick="searchByAlphabet(event, 0)">${String.fromCharCode(i)}</button></li>`
    }
    alphabetSearchUlId.innerHTML = htmlData
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
            })
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
    mainFilterLoaderId.style.display = 'none'
    alphabetUlSetter()
    trendingArtistData(0)
})
