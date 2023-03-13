const urlParams = new URLSearchParams(location.search)
const lotId = urlParams.get('lid')
const headerTitleId = document.querySelector('#headerTitleId')
const image1Id = document.querySelector('#image1Id')
const image2Id = document.querySelector('#image2Id')
const image3Id = document.querySelector('#image3Id')
const image4Id = document.querySelector('#image4Id')
const image5Id = document.querySelector('#image5Id')
const titleId = document.querySelector('#titleId')
const artistId = document.querySelector('#artistId')
const headerLotNoId = document.querySelector('#headerLotNoId')
const lotNoId = document.querySelector('#lotNoId')
const mediumId = document.querySelector('#mediumId')
const categoryId = document.querySelector('#categoryId')
const dimensionsId = document.querySelector('#dimensionsId')
const markingId = document.querySelector('#markingId')
const nameLocationId = document.querySelector('#nameLocationId')
const dateId = document.querySelector('#dateId')
const provenanceId = document.querySelector('#provenanceId')
const literatureId = document.querySelector('#literatureId')
const exhibitionId = document.querySelector('#exhibitionId')
const descriptionId = document.querySelector('#descriptionId')
const relatedLotsId = document.querySelector('#relatedLotsId')
let descData = ''
let apiArtistId = undefined
let apiCategory = undefined

function getRelatedLotsDataSetter(start) {
    document.querySelector('#relatedArtworkViewMoreId').remove()
    fetch(`/auction/getRelatedLotsData/?start=${start}&artistId=${apiArtistId}&category=${apiCategory}&lotId=${lotId}&limit=9`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = relatedLotsId.innerHTML
            body.forEach(auctionData => {
                htmlData += `<div class="col-sm-12 col-md-6 col-lg-4 col-xl-4 mb-4 artworkData">
                                <div class="latest-artists">
                                    <a href="/auction/details/?lid=${auctionData.fal_lot_ID}" class="latest-card">
                                        <div class="thumb">
                                            <img src="https://f000.backblazeb2.com/file/fineart-images/${auctionData.faa_artwork_image1}" class="card-img" alt="img">
                                        </div>
                                        <div class="artist-card">
                                            <h3>Title : <span>${auctionData.faa_artwork_title}</span></h3>
                                            <h3>Artist : <span>${auctionData.fa_artist_name}</span></h3>
                                            <h3 class="mb-3">Lot : ${auctionData.fal_lot_no}</h3>
                                            <h3>Medium : <span>${auctionData.faa_artwork_material}</span></h3>
                                            <h3 class="mb-3">Category : <span>${auctionData.faa_artwork_category}</span></h3>
                                            <h3>${auctionData.faac_auction_title}</h3>
                                            <h3><span>${auctionData.cah_auction_house_name}</span></h3>
                                            <h3 class="mb-3"><span>${auctionData.faac_auction_start_date} | ${auctionData.cah_auction_house_location}</span></h3>
                                            <h3>Estimate : <span>Login to view</span></h3>
                                            <h3>Price Sold : <span>Login to view</span></h3>
                                        </div>
                                    </a>
                                </div>
                            </div>`
            })
            if (body.length === 9) {
                let start = document.querySelectorAll('.artworkData').length + body.length
                htmlData += `<div class="col-12 text-center mt-4" id="relatedArtworkViewMoreId">
                <button type="button" class="btn btn-login btn-round py-2" onclick="getRelatedLotsDataSetter(${start})">View More</button>
            </div>`
            } 
            relatedLotsId.innerHTML = htmlData
        })
}

function getLotDetailsDataSetter() {
    fetch(`/auction/getLotDetails/?lid=${lotId}`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            apiArtistId = body.fa_artist_ID
            apiCategory = body.faa_artwork_category
            headerTitleId.innerHTML = body.faa_artwork_title
            image1Id.src = `https://f000.backblazeb2.com/file/fineart-images/${body.fal_lot_image1}`
            image2Id.src = `https://f000.backblazeb2.com/file/fineart-images/${body.fal_lot_image2}`
            image3Id.src = `https://f000.backblazeb2.com/file/fineart-images/${body.fal_lot_image3}`
            image4Id.src = `https://f000.backblazeb2.com/file/fineart-images/${body.fal_lot_image4}`
            image5Id.src = `https://f000.backblazeb2.com/file/fineart-images/${body.fal_lot_image5}`
            artistId.innerHTML = `Artist : <span>${body.fa_artist_name}</span>`
            titleId.innerHTML = `Title : <span>${body.faa_artwork_title}</span>`
            headerLotNoId.innerHTML = lotNoId.innerHTML = `Lot : ${body.fal_lot_no}`
            mediumId.innerHTML = `Medium : <span>${body.faa_artwork_material}</span>`
            categoryId.innerHTML = `Category : <span>${body.faa_artwork_category}</span>`
            dimensionsId.innerHTML = `Dimensions : <span>${body.fal_lot_height} x ${body.fal_lot_width} x ${body.fal_lot_depth} ${body.fal_lot_measurement_unit}</span></h5>`
            markingId.innerHTML = `Markings : <span>${body.faa_artwork_markings}</span>`
            nameLocationId.innerHTML = `<span>${body.cah_auction_house_name}, ${body.cah_auction_house_location}</span>`
            dateId.innerHTML = `<span>${body.fal_lot_sale_date}</span>`
            provenanceId.innerHTML = body.fal_lot_provenance
            literatureId.innerHTML = body.faa_artwork_literature
            exhibitionId.innerHTML = body.faa_artwork_exhibition
            descData = body.faa_artwork_description.replace('Description', '').replace(':', '').split('Provenance')[0]
            descriptionId.innerHTML = descData.slice(0, 250)
            getRelatedLotsDataSetter(0)
        })
}

function readMore(descExhibiStr, elementId) {
    const aElement = document.querySelector(elementId)
    if (descExhibiStr === 'desc') {
        descriptionId.innerHTML = descData
    }
    aElement.style.display = 'none'
}

document.addEventListener('DOMContentLoaded', function () {
    getLotDetailsDataSetter()
})
