const getTrendingArtistDiv = document.querySelector('#getTrendingArtistId')

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
                                <h4>${artistData.fa_artist_name}</h4>
                                <p>View Details</p>
                            </div>
                            <span>${artistData.fa_artist_nationality }, ${artistData.fa_artist_birth_year} - ${artistData.fa_artist_death_year}</span>
                        </div>
                    </a>
                    </div>`
                });
                getTrendingArtistDiv.innerHTML = htmlData;
                debugger
                var owl = $("#getTrendingArtistId");
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
            })
}

document.addEventListener('DOMContentLoaded', function () {

    trendingArtistSlider()

})
