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
const auctionTitle = document.querySelector('#auctionTitle')
const estimatesId = document.querySelector('#estimatesId')
const estimatesUSDId = document.querySelector('#estimatesUSDId')
const soldPriceId = document.querySelector('#soldPriceId')
const soldPriceUSDId = document.querySelector('#soldPriceUSDId')
const artsitFollowUnfollowId = document.querySelector('#artsitFollowUnfollowId')
const artworkFollowUnfollowId = document.querySelector('#artworkFollowUnfollowId')
let descData = ''
let exhibitionData = ''
let literatureData = ''
let provenanceData = ''
let apiArtistId = undefined
let apiCategory = undefined
let apiArtworkId = undefined

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
                                            <h3>Estimate : <span>${auctionData.cah_auction_house_currency_code} ${auctionData.fal_lot_low_estimate} - ${auctionData.fal_lot_high_estimate}</span></h3>`
                                            if (auctionData.cah_auction_house_currency_code === 'USD') {
                                                if (auctionData.fal_lot_sale_price == 0) {
                                                    htmlData += `<h3>Price Sold : <span>Unsold</span></h3>`
                                                }
                                                else {
                                                htmlData += `<h3>Price Sold : <span>${auctionData.cah_auction_house_currency_code} ${auctionData.fal_lot_sale_price}</span></h3>`
                                                }
                                            }
                                            else {
                                                htmlData += `<h3>Estimate USD : <span>${auctionData.fal_lot_low_estimate_USD} - ${auctionData.fal_lot_high_estimate_USD}</span></h3>`
                                                if (auctionData.fal_lot_sale_price == 0) {
                                                    htmlData += `<h3>Price Sold : <span>Unsold</span></h3>`
                                                }
                                                else {
                                                    htmlData += `<h3>Price Sold : <span>${auctionData.cah_auction_house_currency_code} ${auctionData.fal_lot_sale_price}</span></h3>
                                                                <h3>Price Sold USD : <span>${auctionData.fal_lot_sale_price_USD}</span></h3>`
                                                }
                                            }
                                        htmlData += `
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
            apiArtworkId = body.fal_artwork_ID
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
            auctionTitle.innerHTML = `Auction : <span>${body.faac_auction_title}</span>`
            dimensionsId.innerHTML = `Dimensions : <span>${body.fal_lot_height} x ${body.fal_lot_width} x ${body.fal_lot_depth} ${body.fal_lot_measurement_unit}</span></h5>`
            nameLocationId.innerHTML = `<span>${body.cah_auction_house_name}, ${body.cah_auction_house_location}</span>`
            estimatesId.innerHTML = `Estimates <span>${body.cah_auction_house_currency_code} ${body.fal_lot_low_estimate} - ${body.fal_lot_high_estimate}</span>`
            // estimatesUSDId.innerHTML = `Estimates USD <span>${body.fal_lot_low_estimate_USD} - ${body.fal_lot_high_estimate_USD}</span>`
            if (body.cah_auction_house_currency_code === 'USD') {
                if (body.fal_lot_sale_price == 0) {
                    soldPriceId.innerHTML = `Sold Price <span>Unsold</span>`
                }
                else {
                    soldPriceId.innerHTML = `Sold Price <span>${body.cah_auction_house_currency_code} ${body.fal_lot_sale_price}</span>`
                }
            }
            else {
                estimatesUSDId.innerHTML = `Estimates USD <span>${body.fal_lot_low_estimate_USD} - ${body.fal_lot_high_estimate_USD}</span>`
                if (body.fal_lot_sale_price == 0) {
                    soldPriceId.innerHTML = `Sold Price <span>Unsold</span>`
                }
                else {
                    soldPriceId.innerHTML = `Sold Price <span>${body.cah_auction_house_currency_code} ${body.fal_lot_sale_price}</span>`
                    soldPriceUSDId.innerHTML = `Sold Price USD <span>${body.fal_lot_sale_price_USD}</span>`
                }
            }
            dateId.innerHTML = `<span>${body.fal_lot_sale_date}</span>`
            
            if (body.faa_artwork_material) {
                mediumId.classList.add('mb-2')
                mediumId.innerHTML = `Medium : <span>${body.faa_artwork_material}</span>`
            }

            if (body.faa_artwork_category) {
                categoryId.classList.add('mb-3')
                categoryId.innerHTML = `Category : <span>${body.faa_artwork_category}</span>`
            }

            if (body.faa_artwork_markings) {
                markingId.classList.add('mb-5')
                markingId.innerHTML = `Markings : <span>${body.faa_artwork_markings}</span>`
            }

            if (body.fal_lot_provenance) {
                provenanceId.classList.add('mb-2')
                provenanceData = body.fal_lot_provenance
                if (provenanceData.length >= 250)
                {
                    provenanceId.innerHTML = `<h6>Provenance : </h6>
                                                <div>
                                                    <p class="pl-md-2">${provenanceData.slice(0, 250)}</p>
                                                    <a href="javascript:readMore('provenance', 'more')" id="provenanceReadMoreId">Read More</a>
                                                </div>`
                }
                else {
                    provenanceId.innerHTML = `<h6>Provenance : </h6>
                                                <div>
                                                    <p class="pl-md-2">${provenanceData}</p>
                                                </div>`
                }
            }
            if (body.faa_artwork_literature) {
                literatureId.classList.add('mb-2')
                literatureData = body.faa_artwork_literature
                if (literatureData.length >= 250)
                {
                    literatureId.innerHTML = `<h6>Literature : </h6>
                                                <div>
                                                    <p class="pl-md-2">${literatureData.slice(0, 250)}</p>
                                                    <a href="javascript:readMore('literature', 'more')" id="literatureReadMoreId">Read More</a>
                                                </div>`
                }
                else {
                    literatureId.innerHTML = `<h6>Literature : </h6>
                                                <div>
                                                    <p class="pl-md-2">${literatureData}</p>
                                                </div>`
                }
            }

            if (body.faa_artwork_exhibition) {
                exhibitionId.classList.add("mb-2")
                exhibitionData = body.faa_artwork_exhibition
                if (exhibitionData.length >= 250)
                {
                    exhibitionId.innerHTML = `<h6>Exhibition : </h6>
                                                <div>
                                                    <p class="pl-md-2">${exhibitionData.slice(0, 250)}</p>
                                                    <a href="javascript:readMore('exhibition', 'more')" id="exhibiReadMoreId">Read More</a>
                                                </div>`
                }
                else {
                    exhibitionId.innerHTML = `<h6>Exhibition : </h6>
                                                <div>
                                                    <p class="pl-md-2">${exhibitionData}</p>
                                                </div>`
                }
            }
            
            if (body.faa_artwork_description) {
                descData = body.faa_artwork_description.replace('Description', '').replace(':', '').split('Provenance')[0].replaceAll('<br>', '').replaceAll('<strong>', '').replaceAll('</strong>', '')
                descriptionId.classList.add('mb-2')
                if (descData.length >= 250)
                {
                    descriptionId.innerHTML = `<h6>Description : </h6>
                                                <div>
                                                    <p class="pl-md-2">${descData.slice(0, 250)}</p>
                                                    <a href="javascript:readMore('desc', 'more')" id="descReadMoreId">Read More</a>
                                                </div>`
                }
                else {
                    descriptionId.innerHTML = `<h6>Description : </h6>
                                                <div>
                                                    <p class="pl-md-2">${descData}</p>
                                                </div>`
                }
            }
            getRelatedLotsDataSetter(0)
        })
}

function readMore(descExhibiStr, readLessOrMore) {
    if (readLessOrMore === 'more') {
        if (descExhibiStr === 'desc') {
            descriptionId.innerHTML = `<h6>Description : </h6>
                                        <div>
                                            <p class="pl-md-2">${descData}</p>
                                            <a href="javascript:readMore('desc', 'less')" id="descReadMoreId">Read Less</a>
                                        </div>`
        }

        if (descExhibiStr === 'exhibition') {
            exhibitionId.innerHTML = `<h6>Exhibition : </h6>
                                        <div>
                                            <p class="pl-md-2">${exhibitionData}</p>
                                            <a href="javascript:readMore('exhibition', 'less')" id="exhibiReadMoreId">Read Less</a>
                                        </div>`
        }
        
        if (descExhibiStr === 'literature') {
            literatureId.innerHTML = `<h6>Literature : </h6>
                                        <div>
                                            <p class="pl-md-2">${literatureData}</p>
                                            <a href="javascript:readMore('literature', 'less')" id="literatureReadMoreId">Read Less</a>
                                        </div>`
        }

        if (descExhibiStr === 'provenance') {
            provenanceId.innerHTML = `<h6>Provenance : </h6>
                                        <div>
                                            <p class="pl-md-2">${provenanceData}</p>
                                            <a href="javascript:readMore('provenance', 'less')" id="provenanceReadMoreId">Read Less</a>
                                        </div>`
        }
    }
    else {
        if (descExhibiStr === 'desc') {
            descriptionId.innerHTML = `<h6>Description : </h6>
                                        <div>
                                            <p class="pl-md-2">${descData.slice(0, 250)}</p>
                                            <a href="javascript:readMore('desc', 'more')" id="descReadMoreId">Read More</a>
                                        </div>`
        }

        if (descExhibiStr === 'exhibition') {
            exhibitionId.innerHTML = `<h6>Exhibition : </h6>
                                        <div>
                                            <p class="pl-md-2">${exhibitionData.slice(0, 250)}</p>
                                            <a href="javascript:readMore('exhibition', 'more')" id="exhibiReadMoreId">Read More</a>
                                        </div>`
        }
        
        if (descExhibiStr === 'literature') {
            literatureId.innerHTML = `<h6>Literature : </h6>
                                        <div>
                                            <p class="pl-md-2">${literatureData.slice(0, 250)}</p>
                                            <a href="javascript:readMore('literature', 'more')" id="literatureReadMoreId">Read More</a>
                                        </div>`
        }

        if (descExhibiStr === 'provenance') {
            provenanceId.innerHTML = `<h6>Provenance : </h6>
                                        <div>
                                            <p class="pl-md-2">${provenanceData.slice(0, 250)}</p>
                                            <a href="javascript:readMore('provenance', 'more')" id="provenanceReadMoreId">Read More</a>
                                        </div>`
        }
    }
}

function followUnfollowArtist(followUnfollowStr) {
    artsitFollowUnfollowId.innerHTML = '<button class="btn btn-login btn-round ml-0 d-block mb-2" style="font-size: 12px; width: 100%;" type="button">Please Wait!</button>'
    fetch(`/artist/followUnfollowArtist/?artistId=${apiArtistId}&followUnfollowStr=${followUnfollowStr}`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = `<button class="btn btn-login btn-round ml-0 d-block mb-2" style="font-size: 12px; width: 100%;" type="button" onclick="followUnfollowArtist('${body.msg}')">${body.msg} Artist</button>`
            artsitFollowUnfollowId.innerHTML = htmlData
        })
}

function followUnfollowArtwork(followUnfollowStr) {
    artworkFollowUnfollowId.innerHTML = `<button class="btn btn-login btn-round ml-0  d-block" style="font-size: 12px; width: 100%;" type="button">Please Wait!</button>`
    fetch(`/auction/followUnfollowArtwork/?artworkId=${apiArtworkId}&followUnfollowStr=${followUnfollowStr}`, {
        method: 'GET'
    })
        .then(response => response.json())
        .then(body => {
            let htmlData = `<button class="btn btn-login btn-round ml-0  d-block" style="font-size: 12px; width: 100%;" type="button" onclick="followUnfollowArtwork('${body.msg}')">${body.msg}</button>`
            artworkFollowUnfollowId.innerHTML = htmlData
        })
}

document.addEventListener('DOMContentLoaded', function () {
    getLotDetailsDataSetter()
})
