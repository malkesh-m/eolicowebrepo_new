const urlParams = new URLSearchParams(location.search)
const lotId = urlParams.get('lid')
const headerTitleId = document.querySelector('#headerTitleId')
const headerPdfTitleId = document.querySelector('#headerPdfTitleId')

const image1Id = document.querySelector('#image1Id')
const image11Id = document.querySelector('#image11Id')
const image1PdfId = document.querySelector('#image1PdfId')

const image2Id = document.querySelector('#image2Id')
const image22Id = document.querySelector('#image22Id')
const image2PdfId = document.querySelector('#image2PdfId')

const image3Id = document.querySelector('#image3Id')
const image33Id = document.querySelector('#image33Id')
const image3PdfId = document.querySelector('#image3PdfId')

const image4Id = document.querySelector('#image4Id')
const image44Id = document.querySelector('#image44Id')
const image4PdfId = document.querySelector('#image4PdfId')

const image5Id = document.querySelector('#image5Id')
const image55Id = document.querySelector('#image55Id')
const image5PdfId = document.querySelector('#image5PdfId')

const titleId = document.querySelector('#titleId')
const titlePdfId = document.querySelector('#titlePdfId')

const artistId = document.querySelector('#artistId')
const artistPdfId = document.querySelector('#artistPdfId')

const headerLotNoId = document.querySelector('#headerLotNoId')
const headerLotNoPdfId = document.querySelector('#headerLotNoPdfId')

const lotNoId = document.querySelector('#lotNoId')
const lotNoPdfId = document.querySelector('#lotNoPdfId')

const mediumId = document.querySelector('#mediumId')
const mediumPdfId = document.querySelector('#mediumPdfId')

const categoryId = document.querySelector('#categoryId')
const categoryPdfId = document.querySelector('#categoryPdfId')

const dimensionsId = document.querySelector('#dimensionsId')
const dimensionsPdfId = document.querySelector('#dimensionsPdfId')

const markingId = document.querySelector('#markingId')
const markingPdfId = document.querySelector('#markingPdfId')

const nameLocationId = document.querySelector('#nameLocationId')
const nameLocationPdfId = document.querySelector('#nameLocationPdfId')

const dateId = document.querySelector('#dateId')
const datePdfId = document.querySelector('#datePdfId')

const provenanceId = document.querySelector('#provenanceId')
const provenancePdfId = document.querySelector('#provenancePdfId')

const literatureId = document.querySelector('#literatureId')
const literaturePdfId = document.querySelector('#literaturePdfId')

const exhibitionId = document.querySelector('#exhibitionId')
const exhibitionPdfId = document.querySelector('#exhibitionPdfId')

const descriptionId = document.querySelector('#descriptionId')
const descriptionpdfId = document.querySelector('#descriptionpdfId')

const auctionTitle = document.querySelector('#auctionTitle')
const auctionTitlePdf = document.querySelector('#auctionTitlePdf')

const estimatesId = document.querySelector('#estimatesId')
const estimatesPdfId = document.querySelector('#estimatesPdfId')

const estimatesUSDId = document.querySelector('#estimatesUSDId')
const estimatesUSDPdfId = document.querySelector('#estimatesUSDPdfId')

const soldPriceId = document.querySelector('#soldPriceId')
const soldPricePdfId = document.querySelector('#soldPricePdfId')

const soldPriceUSDId = document.querySelector('#soldPriceUSDId')
const soldPriceUSDPdfId = document.querySelector('#soldPriceUSDPdfId')

const relatedLotsId = document.querySelector('#relatedLotsId')
const artsitFollowUnfollowId = document.querySelector('#artsitFollowUnfollowId')
const artworkFollowUnfollowId = document.querySelector('#artworkFollowUnfollowId')
const saveToPdfBtnId = document.querySelector('#saveToPdfBtnId')

const imageShowOnModalCls = document.querySelectorAll('.imageShowOnModalCls')

let descData = ''
let exhibitionData = ''
let literatureData = ''
let provenanceData = ''
let apiArtistId = undefined
let apiCategory = undefined
let apiArtworkId = undefined
let passwordShowHideFlag = false

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
                                            <h3 class="mb-3"><span>${auctionData.faac_auction_start_date} | ${auctionData.cah_auction_house_location}</span></h3>`
                                            if (auctionData.fal_lot_low_estimate != 0 & auctionData.fal_lot_high_estimate != 0) {
                                                htmlData += `<h3>Estimate : <span>${auctionData.cah_auction_house_currency_code} ${auctionData.fal_lot_low_estimate} - ${auctionData.fal_lot_high_estimate}</span></h3>`
                                            }
                                            if (auctionData.cah_auction_house_currency_code === 'USD') {
                                                if (auctionData.fal_lot_sale_price == 0) {
                                                    htmlData += `<h3>Price Sold : <span>Unsold</span></h3>`
                                                }
                                                else {
                                                htmlData += `<h3>Price Sold : <span>${auctionData.cah_auction_house_currency_code} ${auctionData.fal_lot_sale_price}</span></h3>`
                                                }
                                            }
                                            else {
                                                if (auctionData.fal_lot_low_estimate_USD != 0 & auctionData.fal_lot_high_estimate_USD != 0) {
                                                    htmlData += `<h3>Estimate USD : <span>${auctionData.fal_lot_low_estimate_USD} - ${auctionData.fal_lot_high_estimate_USD}</span></h3>`
                                                }
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

imageShowOnModalCls.forEach(imageTag => {
    imageTag.addEventListener('click', function(e) {
        document.querySelector('#modalImageId').src = e.target.src
        $(`#showImageModalId`).modal('show')
    })
})

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

function saveToPdf() {
    const pdfDataSaveDivId = document.querySelector('#pdfDataSaveDivId')
    window.jsPDF = window.jspdf.jsPDF
    let doc = new jsPDF()
    pdfDataSaveDivId.style.display = 'block'
    doc.html(pdfDataSaveDivId, {
        callback: function(doc) {
            // Save the PDF
            doc.save(`lotDetails_${lotId}.pdf`)
            pdfDataSaveDivId.style.display = 'none'
        },
        x: 15,
        y: 15,
        width: 170, //target width in the PDF document
        windowWidth: 650 //window width in CSS pixels
    })
}

async function getLotDetailsDataSetter() {
    let body = await fetch(`/auction/getLotDetails/?lid=${lotId}`, {
        method: 'GET',
    })
        .then(response => response.json())
            apiArtistId = body.fa_artist_ID
            apiArtworkId = body.fal_artwork_ID
            apiCategory = body.faa_artwork_category
            headerTitleId.innerHTML = headerPdfTitleId.innerHTML = body.faa_artwork_title

            image1Id.src = image1PdfId.src = image11Id.src = `https://f000.backblazeb2.com/file/fineart-images/${body.fal_lot_image1}`

            if (body.fal_lot_image2) {
                image2Id.src = `https://f000.backblazeb2.com/file/fineart-images/${body.fal_lot_image2}`
            }
            else {
                image2Id.scr = `https://f000.backblazeb2.com/file/fineart-images/${body.fal_lot_image1}`
            }
            image2PdfId.src = image22Id.src = image2Id.src

            if (body.fal_lot_image3) {
                image3Id.src = `https://f000.backblazeb2.com/file/fineart-images/${body.fal_lot_image3}`
            }
            else {
                image3Id.src = `https://f000.backblazeb2.com/file/fineart-images/${body.fal_lot_image1}`
            }
            image3PdfId.src = image33Id.src = image3Id.src

            if (body.fal_lot_image4) {
                image4Id.src = `https://f000.backblazeb2.com/file/fineart-images/${body.fal_lot_image4}`
            }
            else {
                image4Id.src = `https://f000.backblazeb2.com/file/fineart-images/${body.fal_lot_image1}`
            }
            image4PdfId.src = image44Id.src = image4Id.src

            if (body.fal_lot_image5) {
                image5Id.src = `https://f000.backblazeb2.com/file/fineart-images/${body.fal_lot_image5}`
            }
            else {
                image5Id.src = `https://f000.backblazeb2.com/file/fineart-images/${body.fal_lot_image1}`
            }
            image5PdfId.src = image55Id.src = image5Id.src

            artistId.innerHTML = artistPdfId.innerHTML = `Artist : <span>${body.fa_artist_name}</span>`
            titleId.innerHTML = titlePdfId.innerHTML = `Title : <span>${body.faa_artwork_title}</span>`
            headerLotNoId.innerHTML = lotNoId.innerHTML = headerLotNoPdfId.innerHTML = lotNoPdfId.innerHTML = `Lot : ${body.fal_lot_no}`
            auctionTitle.innerHTML = auctionTitlePdf.innerHTML = `Auction : <span>${body.faac_auction_title}</span>`
            dimensionsId.innerHTML = dimensionsPdfId.innerHTML = `Dimensions : <span>${body.fal_lot_height} x ${body.fal_lot_width} x ${body.fal_lot_depth} ${body.fal_lot_measurement_unit}</span></h5>`
            nameLocationId.innerHTML = nameLocationPdfId.innerHTML = `<span>${body.cah_auction_house_name}, ${body.cah_auction_house_location}</span>`
            estimatesId.innerHTML = estimatesPdfId.innerHTML = `Estimates <span>${body.cah_auction_house_currency_code} ${body.fal_lot_low_estimate} - ${body.fal_lot_high_estimate}</span>`
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
            soldPricePdfId.innerHTML = soldPriceId.innerHTML
            soldPriceUSDPdfId.innerHTML = soldPriceUSDId.innerHTML
            }
            dateId.innerHTML = datePdfId.innerHTML = `<span>${body.fal_lot_sale_date}</span>`
            
            if (body.faa_artwork_material) {
                mediumId.classList.add('mb-2')
                mediumId.innerHTML = mediumPdfId.innerHTML = `Medium : <span>${body.faa_artwork_material}</span>`
            }

            if (body.faa_artwork_category) {
                categoryId.classList.add('mb-3')
                categoryId.innerHTML = categoryPdfId.innerHTML = `Category : <span>${body.faa_artwork_category}</span>`
            }

            if (body.faa_artwork_markings) {
                markingId.classList.add('mb-5')
                markingId.innerHTML = markingPdfId.innerHTML = `Markings : <span>${body.faa_artwork_markings}</span>`
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
                provenancePdfId.innerHTML = `<h6>Provenance : </h6>
                                                <div>
                                                    <p class="pl-md-2">${provenanceData}</p>
                                                </div>`
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
                literaturePdfId.innerHTML = `<h6>Literature : </h6>
                                            <div>
                                                <p class="pl-md-2">${literatureData}</p>
                                            </div>`
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
                exhibitionPdfId.innerHTML = `<h6>Exhibition : </h6>
                                            <div>
                                                <p class="pl-md-2">${exhibitionData}</p>
                                            </div>`
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
                descriptionpdfId.innerHTML = `<h6>Description : </h6>
                                            <div>
                                                <p class="pl-md-2">${descData}</p>
                                            </div>`
            }
            saveToPdfBtnId.addEventListener('click', saveToPdf)
            getRelatedLotsDataSetter(0)
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
