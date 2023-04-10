const frmpricefilter = document.querySelector('#frmpricefilter')
const advanceSearchResultDataDivId = document.querySelector('#advanceSearchResultDataDivId')
const txttitle = document.querySelector('#txttitle')
const txtartistname = document.querySelector('#txtartistname')
const sel_auctionhouses = document.querySelector('#sel_auctionhouses')
const displayDataDivId = document.querySelector('#displayDataDivId')
let passwordShowHideFlag = false

function clearFilter(e) {
    $('#txttitle').val(null).trigger('change')
    $('#txtartistname').val(null).trigger('change')
    $('#sel_auctionhouses').val(null).trigger('change')
    frmpricefilter.reset()
}

function htmlDataBinder(auctionData) {
    let htmlData = `<div class="col-sm-12 col-md-6 col-lg-4 col-xl-3 mb-3 artworkData">
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
                                    <h3 class="mb-3">Category : <span>${auctionData.faa_artwork_category}</span>
                                    </h3>

                                    <h3>${auctionData.faac_auction_title}</h3>
                                    <h3><span>${auctionData.cah_auction_house_name}</span></h3>
                                    <h3 class="mb-3"><span>${auctionData.faac_auction_start_date} | ${auctionData.cah_auction_house_location}</span>
                                    </h3>`

                                    if (auctionData.fal_lot_low_estimate != 0 & auctionData.fal_lot_high_estimate != 0) {
                                        htmlData += `<h3>Estimate : <span>${auctionData.cah_auction_house_currency_code} ${auctionData.fal_lot_low_estimate} - ${auctionData.fal_lot_high_estimate}</span></h3>`
                                    }
                                    if (auctionData.cah_auction_house_currency_code === 'USD') {
                                        if (auctionData.fal_lot_sale_price == 0 || auctionData.fal_lot_sale_price == null) {
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
                                        if (auctionData.fal_lot_sale_price == 0 || auctionData.fal_lot_sale_price == null) {
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
    return htmlData
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

function dataFilter(start, limit) {
    const medium1 = document.querySelector('#medium1')
    const medium2 = document.querySelector('#medium2')
    const medium3 = document.querySelector('#medium3')
    const medium4 = document.querySelector('#medium4')
    const medium5 = document.querySelector('#medium5')
    const medium6 = document.querySelector('#medium6')
    const medium7 = document.querySelector('#medium7')
    const medium8 = document.querySelector('#medium8')
    const sel_artwork_start = document.querySelector('#sel_artwork_start')
    const sel_artwork_end = document.querySelector('#sel_artwork_end')
    const dtauctionstartdate = document.querySelector('#dtauctionstartdate')
    const txtauctionlocation = document.querySelector('#txtauctionlocation')
    const soldCheckId = document.querySelector('#soldCheckId')
    const yetToBeSoldCheckId = document.querySelector('#yetToBeSoldCheckId')
    const boughtInCehckId = document.querySelector('#boughtInCehckId')
    const withdrawnCheckId = document.querySelector('#withdrawnCheckId')
    const txtsaletitle = document.querySelector('#txtsaletitle')
    const txtsalecode = document.querySelector('#txtsalecode')
    const dtauctionenddate = document.querySelector('#dtauctionenddate')

    const formData = new FormData()
    formData.append('txtartistname', txtartistname.value)
    formData.append('txttitle', txttitle.value)
    if (medium1.checked) {
        formData.append('medium1', medium1.value)
    }
    if (medium2.checked) {
        formData.append('medium2', medium2.value)
    }
    if (medium3.checked) {
        formData.append('medium3', medium3.value)
    }
    if (medium4.checked) {
        formData.append('medium4', medium4.value)
    }
    if (medium5.checked) {
        formData.append('medium5', medium5.value)
    }
    if (medium6.checked) {
        formData.append('medium6', medium6.value)
    }
    if (medium7.checked) {
        formData.append('medium7', medium7.value)
    }
    if (medium7.checked) {
        formData.append('medium8', medium8.value)
    }
    formData.append('sel_artwork_start', sel_artwork_start.value)
    formData.append('sel_artwork_end', sel_artwork_end.value)
    formData.append('dtauctionstartdate', dtauctionstartdate.value)
    formData.append('sel_auctionhouses', sel_auctionhouses.value)
    formData.append('txtauctionlocation', txtauctionlocation.value)
    if (soldCheckId.checked) {
        formData.append('soldCheckId', soldCheckId.value)
    }
    if (yetToBeSoldCheckId.checked) {
        formData.append('yetToBeSoldCheckId', yetToBeSoldCheckId.value)
    }
    if (boughtInCehckId.checked) {
        formData.append('boughtInCehckId', boughtInCehckId.value)
    }
    if (withdrawnCheckId.checked) {
        formData.append('withdrawnCheckId', withdrawnCheckId.value)
    }
    formData.append('txtsaletitle', txtsaletitle.value)
    formData.append('txtsalecode', txtsalecode.value)
    formData.append('dtauctionenddate', dtauctionenddate.value)

    fetch(`/price/database/?start=${start}&limit=${limit}`, {
        method: 'POST',
        body: formData
    })
        .then(reponse => reponse.json())
        .then(body => {
            let htmlData = ''
            body.forEach(resultData => {
                htmlData += htmlDataBinder(resultData)
            })
            advanceSearchResultDataDivId.innerHTML = htmlData
            displayDataDivId.style.display = 'block'
        })
}

frmpricefilter.addEventListener('submit', function (event) {
    event.preventDefault()
    dataFilter(0, 50)
})

function selectChange(event) {
    let limit = document.querySelector('#inputGroupSelect01').value
    dataFilter(0, limit)
}

function selectAutionHouse() {
    $('#sel_auctionhouses').select2({
        placeholder: 'Select Auction House', 
        ajax: {
            url: '/price/searchAuctionHouses/',
            type: "GET",
            dataType: 'json',
            data: function (data) {
                return {search: data.term}
            },
            processResults: function (response) {
                let data = $.map(response, function (dataObj) {
                    return {id: dataObj.cah_auction_house_name, text: dataObj.cah_auction_house_name}
                })
                return {results: data}
            },
        }
    });
}

function selectArtist() {
    $('#txtartistname').select2({
        placeholder: 'Select Artist', 
        ajax: {
            url: '/price/searchArtists/',
            type: "GET",
            dataType: 'json',
            data: function (data) {
                return {search: data.term}
            },
            processResults: function (response) {
                let data = $.map(response, function (dataObj) {
                    return {id: dataObj.fa_artist_name, text: dataObj.fa_artist_name}
                })
                return {results: data}
            },
        }
    });
}

function selectArtwork() {
    $('#txttitle').select2({
        placeholder: 'Select Artwork', 
        ajax: {
            url: '/price/searchArtworks/',
            type: "GET",
            dataType: 'json',
            data: function (data) {
                return {search: data.term}
            },
            processResults: function (response) {
                let data = $.map(response, function (dataObj) {
                    let newTitle = dataObj.faa_artwork_title.replaceAll('\t', '').replaceAll('\r', '').replaceAll('\u0000', '').replaceAll('\n', '')
                    return {id: newTitle, text: newTitle}
                })
                return {results: data}
            },
        }
    });
}

async function select2Ajax() {
    selectAutionHouse()
    selectArtist()
    selectArtwork()
}

document.addEventListener('DOMContentLoaded', function () {
    select2Ajax()
    displayDataDivId.style.display = 'none'
})
